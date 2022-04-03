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


def _readline(ser) -> bytes:
    '''readline from serial, where line ends with "\r\n"'''
    eol = b'\r\n'
    leneol = len(eol)
    line = bytearray()

    while True:
        c = ser.read(1)
        if c:
            line += c
            if line[-leneol:] == eol:
                break
        else:
            break

    return bytes(line)


class SkyTrack:

    BINARY_MODE = b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A'
    '''Command to swap to binary mode'''

    MOCK_DATA = (b'\xa0\xa1\x00\x3b\xa8\x00\x00\x05\x65\x01\xcd\x6e\x2c\x00\x00\x00\x00\x00\x00'
                 b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                 b'\x00\xf1\x97\x20\xd4\xe9\x88\x83\xec\x1a\xfb\x24\xe8\x00\x00\x00\x00\x00\x00'
                 b'\x00\x00\x00\x00\x00\x00\xf7\x0d\x0a')
    '''Mock binary line'''

    def __init__(self, port: str, baud: str, gpio0: str, gpio1: str, mock=False):
        '''
        Paramters
        ---------
        port: str
            Serial port to use.
        baud: str
            Baud to use.
        gpio0: str
            gpio to use.
        gpio1: str
            gpio to use.
        mock: str
            option to mocking the skytraq.
        '''

        self._port = port
        self._baud = baud
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

    def read(self) -> ():
        '''Read a message from the skytraq.'''

        if not self._is_on:
            raise SkyTrackError('skytraq is not on')

        if self._mock:
            try:
                line = _readline(self._ser)
            except SerialException as exc:
                raise SkyTrackError(f'Device error: {exc}')
        else:
            line = self.MOCK_DATA

        line_len = len(line)
        if line_len <= 7:
            raise SkyTrackError('skytraq message length is <= 7')

        # validate payload length in line
        body_len = line_len - 7
        pl_bytes = line[2: (line_len - 4) * -1]
        try:
            pl = struct.unpack('>H', pl_bytes[0])
        except struct.error:
            raise SkyTrackError('skytraq payload length unpack failed')
        if body_len != pl:
            raise SkyTrackError(f'payload length does not match {body_len} vs {pl}')

        # validate checksum
        cs = 0
        for i in line[4:-3]:
            cs = cs ^ i
        if cs != line[-3]:
            raise SkyTrackError('invalid checksum')

        try:
            data = struct.unpack('>4x3BHI2i2I5H6i3x', line)
        except struct.error:
            raise SkyTrackError('skytraq message unpack failed')

        return data
