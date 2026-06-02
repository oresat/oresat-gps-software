"""SkyTraq serial driver."""

import struct
from collections.abc import Iterable
from enum import Enum, unique
from functools import reduce
from operator import xor
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    import gpiod

from gpiod.line import Value
from olaf import logger
from serial import Serial, SerialException

from oresat_gps._gpio import request_gpio_output


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
    """SkyTraq serial driver.

    skytraq binary protocol
    -----------------------
    The general format is detailed at https://www.skytraq.com.tw/homesite/AN0037.pdf.

    | start     | payload len (PL) |         Payload             | checksum (CS) | end of    |
    | of seq    |                  | msg id |    message body    |               | sequence  |
    |-----------|------------------|--------|--------------------|---------------|-----------|
    | 0xa0 0xa1 | 2 bytes          | 1 byte | =< 2**16 - 1 bytes | 1 byte        | 0x0d 0x0a |

    Ex: <0xa0, 0xa1><PL><msg id><msg body><CS><0x0d, 0x0a>

    The checksum is the 8-bit exclusive OR of only the payload bytes which start from Message ID.
    For example,

    CS := 0x09 ^ 0x02 = 0x0b
    CS := 0x0b ^ 0x00 = 0x0b
    """

    BINARY_START: bytes = b'\xa0\xa1'
    """SkyTraq binary message start bytes"""
    BINARY_END: bytes = b'\x0d\x0a'
    """SkyTraq binary message end bytes"""

    BAUD = 115200

    def __init__(self, port: Path) -> None:
        """Create a SkyTraq instance associated with a specific serial interface.

        Parameters
        ----------
        port
                Serial port to use.
        """
        self._port = port

    def _read(self) -> bytes:
        r"""Read from skytraq serial interface.

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
            raise SkyTraqError("skytraq serial read failed")
        return line

    def read(self) -> tuple[NavData, bytes]:
        """Read the stream of messages from the Skytraq."""
        # See Application Note AN0037 for format
        line = self._read()
        try:
            payload = self.decode_binary(line)
        except ValueError as e:
            logger.error("Error decoding payload: %s", e)
            raise SkyTraqError("Error decoding payload") from e

        try:
            nav_data = NavData(*struct.unpack(">3BHI2i2I5H6i", payload))
        except (struct.error, TypeError) as e:
            raise SkyTraqError("Error unpacking payload") from e

        return nav_data, payload

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

    @classmethod
    def decode_binary(cls, data: bytes) -> bytes:
        """Decode a SkyTraq binary message and return the payload.

        Parameters
        ----------
        data
            The encoded message.

        Returns
        -------
        bytes
            The decoded payload.

        Raises
        ------
        ValueError
            The message is missing its sequence start or end, or length or checksum does not match.
        """
        if not data.startswith(cls.BINARY_START) or not data.endswith(cls.BINARY_END):
            raise ValueError("invalid binary message")
        inner = data[len(cls.BINARY_START) : -len(cls.BINARY_END)]
        payload_len = inner[0:2]
        payload = inner[2:-1]
        csum = inner[-1]
        if int.from_bytes(payload_len, byteorder="big") != len(payload):
            raise ValueError(f"payload length does not match {payload_len} vs {len(payload)}")
        if csum != cls.checksum(payload):
            raise ValueError("invalid checksum")
        return payload

    def connect(self) -> None:
        """Connect to the Skytraq receiver serial interface."""
        self._ser = Serial(str(self._port), self.BAUD, timeout=1)
        # swap to binary mode
        self._ser.write(SkyTraq.encode_binary(0x09, b"\x02\x00"))

    def disconnect(self) -> None:
        """Disconnect from the Skytraq receiver serial interface."""
        self._ser.close()

    @property
    def is_connected(self) -> bool:
        """Status of the Skytraq serial interface."""
        return self._ser.is_open


class SkyTraq10(SkyTraq):
    """SkyTraq driver for the GPS 1.0 series boards."""

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._enable: gpiod.LineRequest = request_gpio_output(
            chip_path="/dev/gpiochip2",
            offset=2,
            line_name="STQ_EN",
        )
        self._lna: gpiod.LineRequest = request_gpio_output(
            chip_path="/dev/gpiochip2",
            offset=4,
            line_name="MAX_EN",
        )

    def connect(self) -> None:
        """Enable GPS power domain, then connect to Skytraq receiver serial interface."""
        self._enable.set_value(self._enable.offsets[0], Value.ACTIVE)
        self._lna.set_value(self._lna.offsets[0], Value.ACTIVE)
        super().connect()

    def disconnect(self) -> None:
        """Diconnect from Skytraq receiver, disable GPS power domain."""
        super().disconnect()
        self._lna.set_value(self._lna.offsets[0], Value.INACTIVE)
        self._enable.set_value(self._enable.offsets[0], Value.INACTIVE)


class SkyTraq11(SkyTraq):
    """SkyTraq driver for the GPS 1.1 series boards."""

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._enable: gpiod.LineRequest = request_gpio_output(
            chip_path="/dev/gpiochip2",
            offset=4,
            line_name="GPS_EN",
        )

    def connect(self) -> None:
        """Enable GPS power domain, then connect to Skytraq receiver serial interface."""
        self._enable.set_value(self._enable.offsets[0], Value.ACTIVE)
        super().connect()

    def disconnect(self) -> None:
        """Diconnect from Skytraq receiver, disable GPS power domain."""
        super().disconnect()
        self._enable.set_value(self._enable.offsets[0], Value.INACTIVE)


class MockSkyTraq(SkyTraq):
    """A simulated SkyTraq driver that doesn't touch any physical hardware.

    Returns only a message of type 0xA8 - Navigation Data Message.
    """

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
