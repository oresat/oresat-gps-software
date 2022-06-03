import struct
from enum import IntEnum

from serial import Serial, SerialException


class SkyTrackError(Exception):
    '''An error occured with the SkyTrack'''


class NavData(IntEnum):
    '''NavData offsets for skytraq binary data'''

    MESSAGE_ID = 0
    FIX_MODE = 1
    NUMBER_OF_SV = 2
    GPS_WEEK = 3
    TOW = 4
    LATITUDE = 5
    LONGITUDE = 6
    ELLIPSOID_ALTITUDE = 7
    MEAN_SEA_LVL_ALTITUDE = 8
    GDOP = 9
    PDOP = 10
    HDOP = 11
    VDOP = 12
    TDOP = 13
    ECEF_X = 14
    ECEF_Y = 15
    ECEF_Z = 16
    ECEF_VX = 17
    ECEF_VY = 18
    ECEF_VZ = 19


class FixMode(IntEnum):
    '''Quality of fix'''

    NO_FIX = 0
    FIX_2D = 1
    FIX_3D = 2
    FIX_3D_DGPS = 3


class SkyTrack:

    BINARY_MODE = b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A'
    '''Command to swap to binary mode'''

    MOCK_DATA = (b'\xa0\xa1\x00\x3b\xa8\x02\x07\x08\x6a\x03\x21\x7a\x1f\x1b\x1f\x16\xf1\xb6\xe1'
                 b'\x3c\x1c\x00\x00\x0f\x6f\x00\x00\x17\xb7\x01\x0d\x00\xe4\x00\x7e\x00\xbd\x00'
                 b'\x8f\xf1\x97\x18\xd2\xe9\x88\x7d\x90\x1a\xfb\x26\xf7\x00\x00\x00\x00\x00\x00'
                 b'\x00\x00\x00\x00\x00\x00\x68\x0d\x0a')
    '''Mock binary line'''

    def __init__(self, port: str, gpio0: str, gpio1: str, mock: bool = True):
        '''
        Paramters
        ---------
        port: str
            Serial port to use.
        gpio0: str
            gpio to use.
        gpio1: str
            gpio to use.
        mock: str
            option to mocking the skytraq.
        '''

        self._port = port
        self._baud = 9600
        self._gpio0 = gpio0
        self._gpio1 = gpio1
        self._mock = mock

        self._is_on = False
        self._ser = None

    def power_on(self):
        ''' Turn the skytraq on'''

        if not self._mock and not self._is_on:
            try:
                # first time will fail
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(self._gpio0)
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(self._gpio0)
            except PermissionError:
                pass  # first time will fail
            with open(f'/sys/class/gpio/gpio{self._gpio0}/direction', 'w') as f:
                f.write('out')
            with open(f'/sys/class/gpio/gpio{self._gpio0}/value', 'w') as f:
                f.write('1')

            try:
                # first time will fail
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(self._gpio1)
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(self._gpio1)
            except PermissionError:
                pass  # first time will fail
            with open(f'/sys/class/gpio/gpio{self._gpio1}/direction', 'w') as f:
                f.write('out')
            with open(f'/sys/class/gpio/gpio{self._gpio1}/value', 'w') as f:
                f.write('1')

            self._ser = Serial(self._port, self._baud, timeout=0.5)
            self._ser.write(self.BINARY_MODE)  # swap to binary mode

        self._is_on = True

    def power_off(self):
        ''' Turn the skytraq off'''

        if not self._mock and self._is_on:
            self._ser.close()

            with open(f'/sys/class/gpio/gpio{self._gpio0}/value', 'w') as f:
                f.write('0')
            with open(f'/sys/class/gpio/gpio{self._gpio1}/value', 'w') as f:
                f.write('0')

        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    def _readline(self, timeout) -> bytes:
        '''readline from skytraq serial bus

        format:
            [0xA0A1][PL][ID][P][CS][\r\n]
            PL = payload length
            ID = unique id
            P = payload
            CS = checksum

        Raises
        ------
        SkyTrackError
            An error occured.

        Returns
        -------
        bytes
            The bytes from the body. The first byte is the message the rest are the payload bytes.
        '''

        if self._mock:
            line = self.MOCK_DATA
        else:
            line = bytearray()
            while True:
                try:
                    c = self._ser.read(timeout)
                except SerialException as exc:
                    raise SkyTrackError(f'Serial device error: {exc}')

                if c:
                    line += c
                    if line[-2:] == b'\r\n':
                        break
                else:
                    break
            line = bytes(line)

        if not line:
            raise SkyTrackError('skytraq read serial failed')

        line_len = len(line)
        if line_len <= 7:
            raise SkyTrackError('skytraq message length is too short')

        payload_len_bytes = line[2: (line_len - 4) * -1]
        payload_bytes = line[4:-3]
        checksum_byte = line[-3]

        # validate payload length in line
        try:
            pl = struct.unpack('>H', payload_len_bytes)[0]
        except struct.error:
            raise SkyTrackError('skytraq payload length unpack failed')
        if len(payload_bytes) != pl:
            raise SkyTrackError(f'payload length does not match {len(payload_bytes)} vs {pl}')

        # validate checksum
        cs = 0
        for i in payload_bytes:
            cs = cs ^ i
        if cs != checksum_byte:
            raise SkyTrackError('invalid checksum')

        return payload_bytes

    def read(self) -> ():
        '''Read a message from the skytraq.'''

        if not self._is_on:
            raise SkyTrackError('skytraq is not on')

        payload = self._readline(1)

        try:
            data = struct.unpack('>3BHI2i2I5H6i', payload)
        except struct.error:
            raise SkyTrackError('skytraq message unpack failed')

        return data
