import struct
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from enum import IntEnum
from threading import Event, Thread
from typing import Callable

from serial import Serial, SerialException


SKYTRAQ_EPOCH = datetime(1980, 1, 5, tzinfo=timezone.utc)
'''SkyTraq's time epoch'''


NavData = namedtuple('NavData', ['message_id', 'fix_mode', 'number_of_sv', 'gps_week', 'tow',
                                 'latitude', 'longitude', 'ellipsoid_altitude',
                                 'mean_sea_lvl_altitude', 'gdop', 'pdop', 'hdop', 'vdop', 'tdop',
                                 'ecef_x', 'ecef_y', 'ecef_z', 'ecef_vx', 'ecef_vy', 'ecef_vz'])


class SkyTraqError(Exception):
    '''An error occured with the SkyTraq'''


class FixMode(IntEnum):
    '''Quality of fix'''

    NO_FIX = 0
    FIX_2D = 1
    FIX_3D = 2
    FIX_3D_DGPS = 3


class SkyTraq:

    BINARY_MODE = b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A'
    '''Command to swap to binary mode'''

    MOCK_DATA = (b'\xa0\xa1\x00\x3b\xa8\x02\x07\x08\x6a\x03\x21\x7a\x1f\x1b\x1f\x16\xf1\xb6\xe1'
                 b'\x3c\x1c\x00\x00\x0f\x6f\x00\x00\x17\xb7\x01\x0d\x00\xe4\x00\x7e\x00\xbd\x00'
                 b'\x8f\xf1\x97\x18\xd2\xe9\x88\x7d\x90\x1a\xfb\x26\xf7\x00\x00\x00\x00\x00\x00'
                 b'\x00\x00\x00\x00\x00\x00\x68\x0d\x0a')
    '''Mock binary line'''

    BAUD = 9600
    '''Baud rate of skytraq'''

    def __init__(self, port: str, message_cb: Callable[[NavData], None],
                 error_cb: Callable[[str], None], mock: bool = False):
        '''
        Paramters
        ---------
        port: str
            Serial port to use.
        message_cb: Callable
            Message callback funtion.
        error_cb: Callable
            Error callback funtion.
        mock: str
            option to mocking the skytraq.
        '''

        self._port = port
        self._message_cb = message_cb
        self._error_cb = error_cb
        self._mock = mock

        self._event = Event()
        self._thread = Thread(target=self._stream)

    def _readline(self, ser: Serial, timeout: float) -> bytes:
        '''readline from skytraq serial bus

        format:
            [0xA0A1][PL][ID][P][CS][\r\n]
            PL = payload length
            ID = unique id
            P = payload
            CS = checksum

        Raises
        ------
        SkyTraqError
            An error occured.

        Returns
        -------
        bytes
            The bytes from the body. The first byte is the message the rest are the payload bytes.
        '''

        if self._mock:
            line = self.MOCK_DATA
            self._event.wait(0.5)
        else:
            line = bytearray()
            while True:
                try:
                    c = ser.read(timeout)
                except SerialException as exc:
                    raise SkyTraqError(f'Serial device error: {exc}')

                if c:
                    line += c
                    if line[-2:] == b'\r\n':
                        break
                else:
                    break
            line = bytes(line)

        if not line:
            raise SkyTraqError('skytraq read serial failed')

        line_len = len(line)
        if line_len <= 7:
            raise SkyTraqError('skytraq message length is too short')

        payload_len_bytes = line[2: (line_len - 4) * -1]
        payload_bytes = line[4:-3]
        checksum_byte = line[-3]

        # validate payload length in line
        try:
            pl = struct.unpack('>H', payload_len_bytes)[0]
        except struct.error:
            raise SkyTraqError('skytraq payload length unpack failed')
        if len(payload_bytes) != pl:
            raise SkyTraqError(f'payload length does not match {len(payload_bytes)} vs {pl}')

        # validate checksum
        cs = 0
        for i in payload_bytes:
            cs = cs ^ i
        if cs != checksum_byte:
            raise SkyTraqError('invalid checksum')

        return payload_bytes

    def _stream(self):
        '''Read the stream of messages from the skytraq.'''

        if not self._mock:
            ser = Serial(self._port, self.BAUD, timeout=1)
            ser.write(self.BINARY_MODE)  # swap to binary mode
        else:
            ser = None  # mocking serial bus

        while not self._event.is_set():
            try:
                payload = self._readline(ser, 1)
                data = struct.unpack('>3BHI2i2I5H6i', payload)
                nav_data = NavData(*data)
                self._message_cb(nav_data)
            except SkyTraqError:
                pass  # don't care, most likely a random parse error
            except Exception as e:
                self._error_cb(f'{e.__class__.__name__}: {e}')

        if not self._mock:
            ser.close()

    def start(self):
        '''Start read stream thread'''

        self._thread.start()

    def stop(self):
        '''Stop read stream thread'''

        self._event.set()
        if self._thread.is_alive():
            self._thread.join()


def gps_datetime(gps_week: int, tow: int) -> float:
    '''Get the unix time from SkyTraq's gps_week and TOW (time of week).'''

    usec = tow % 100 * 1000
    # 86400 is number of seconds in a day
    sec = (tow / 100) % 86400
    day = ((tow / 100) / 86400) + (gps_week * 7)
    dt = SKYTRAQ_EPOCH + timedelta(days=day, seconds=sec, microseconds=usec)

    return dt.timestamp()
