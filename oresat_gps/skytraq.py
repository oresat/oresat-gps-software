"""SkyTraq serial driver."""

import struct
from enum import Enum, unique
from functools import reduce
from operator import xor
from pathlib import Path
from time import sleep
from typing import Iterable, NamedTuple

from olaf import Gpio
from serial import Serial, SerialException


class NavData(NamedTuple):
    '''Raw Navigation data returned from a SkyTraq.'''

    message_id: int
    fix_mode: int
    number_of_sv: int
    gps_week: int
    tow: int
    latitude: int
    longitude: int
    ellipsoid_alt: int
    mean_sea_lvl_alt: int
    gdop: int
    pdop: int
    hdop: int
    vdop: int
    tdop: int
    ecef_x: int
    ecef_y: int
    ecef_z: int
    ecef_vx: int
    ecef_vy: int
    ecef_vz: int


class SkyTraqError(Exception):
    """An error occurred with the SkyTraq."""


@unique
class FixMode(Enum):
    """Quality of fix."""

    NO_FIX = 0
    FIX_2D = 1
    FIX_3D = 2
    FIX_3D_DGPS = 3


class SkyTraq:
    """SkyTraq serial driver."""

    """Command to swap to binary mode"""
    BINARY_START: bytes = b'\xA0\xA1'
    """SkyTraq binary message start bytes"""
    BINARY_END: bytes = b'\x0D\x0A'
    """SkyTraq binary message end bytes"""

    BAUD = 9600
    """Baud rate of skytraq"""

    def __init__(self, port: Path) -> None:
        """Create a SkyTraq instance associated with a specific serial port.

        Parameters
        ----------
        port: str
            Serial port to use.
        """
        self._port = port

    def _read(self) -> bytes:
        r"""Read from skytraq serial bus.

        format:
            [0xA0A1][PL][ID][P][CS][\r\n]
            PL = payload length
            ID = unique id
            P = payload
            CS = checksum

        Raises
        ------
        SkyTraqError
            An error occurred.

        Returns
        -------
        bytes
            The bytes from the body. The first byte is the message the rest are the payload bytes.
        """
        try:
            line = self._ser.readline()
        except SerialException as e:
            raise SkyTraqError("Error reading GPS line") from e
        if not line:
            raise SkyTraqError("skytraq read serial failed")
        return line

    def read(self) -> tuple[NavData, bytes]:
        """Read the stream of messages from the skytraq."""
        # See Application Note AN0037 for format
        line = self._read()
        if len(line) <= 7:
            raise SkyTraqError("skytraq message length is too short")

        payload_len_bytes = line[2:4]
        payload_bytes = line[4:-3]
        checksum_byte = line[-3]

        # validate payload length in line
        try:
            (pl,) = struct.unpack(">H", payload_len_bytes)
        except struct.error as e:
            raise SkyTraqError("skytraq payload length unpack failed") from e
        if len(payload_bytes) != pl:
            raise SkyTraqError(f"payload length does not match {len(payload_bytes)} vs {pl}")

        if SkyTraq.checksum(payload_bytes) != checksum_byte:
            raise SkyTraqError("invalid checksum")

        try:
            nav_data = NavData(*struct.unpack(">3BHI2i2I5H6i", payload_bytes))
        except (struct.error, TypeError) as e:
            raise SkyTraqError("Error unpacking payload") from e

        return nav_data, payload_bytes

    @staticmethod
    def checksum(payload: Iterable[int]) -> int:
        return reduce(xor, payload, 0)

    @classmethod
    def encode_binary(cls, message_id: int, body: bytes) -> bytes:
        """Encode a message ID and body into a SkyTraq binary message.

        Parameters
        ----------
        message_id
            The message ID.
        body
            The message body.

        Returns
        -------
        bytes
            The encoded message.

        Raises
        ------
        OverflowError
            If message_id > 1 byte or body > 65534 bytes. SkyTraq limits total
            payload size to 65535 bytes (id + body).
        """
        msg_bytes: bytes = message_id.to_bytes(1, byteorder="big")
        payload_length: bytes = (1 + len(body)).to_bytes(2, byteorder="big")
        payload_bytes: bytearray = bytearray(msg_bytes)
        payload_bytes += body
        cs: bytes = cls.checksum(payload_bytes).to_bytes(1, byteorder="big")
        # <0xA0,0xA1><PL><Message ID><Message Body><CS><0x0D,0x0A>
        payload_bytes[0:0] = cls.BINARY_START + payload_length
        payload_bytes += cs + cls.BINARY_END
        return bytes(payload_bytes)

    def connect(self) -> None:
        """Connect to the skytraq serial bus."""
        self._ser = Serial(str(self._port), self.BAUD, timeout=1)
        self._ser.write(SkyTraq.encode_binary(0x09, b"\x02\x00"))  # swap to binary mode

    def disconnect(self) -> None:
        """Disconnect from the skytraq serial bus."""
        self._ser.close()

    @property
    def is_connected(self) -> bool:
        """Status of the connection to the skytraq serial bus."""
        return self._ser.is_open


class SkyTraq10(SkyTraq):
    '''SkyTraq driver for the GPS 1.0 series boards.'''

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._enable = Gpio("STQ_EN")
        self._lna = Gpio("MAX_EN")

    def connect(self) -> None:
        self._enable.high()
        self._lna.high()
        super().connect()

    def disconnect(self) -> None:
        super().disconnect()
        self._lna.low()
        self._enable.low()


class SkyTraq11(SkyTraq):
    '''SkyTraq driver for the GPS 1.1 series boards.'''

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._enable = Gpio("GPS_EN")

    def connect(self) -> None:
        self._enable.high()
        super().connect()

    def disconnect(self) -> None:
        super().disconnect()
        self._enable.low()


class MockSkyTraq(SkyTraq):
    '''A simulated SkyTraq driver that doesn't touch any physical hardware.

    Returns only a message of type 0xA8 - Navigation Data Message.
    '''

    MOCK_DATA = (
        b"\xa0\xa1\x00\x3b\xa8\x02\x07\x08\x6a\x03\x21\x7a\x1f\x1b\x1f\x16\xf1\xb6\xe1"
        b"\x3c\x1c\x00\x00\x0f\x6f\x00\x00\x17\xb7\x01\x0d\x00\xe4\x00\x7e\x00\xbd\x00"
        b"\x8f\xf1\x97\x18\xd2\xe9\x88\x7d\x90\x1a\xfb\x26\xf7\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x68\x0d\x0a"
    )

    def __init__(self) -> None:
        self._connected = False

    def _read(self) -> bytes:
        sleep(0.5)
        return self.MOCK_DATA

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected
