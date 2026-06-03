"""Tests for the SkyTraq module."""

from collections.abc import Generator
from typing import Any

import pytest
import serial

from oresat_gps.skytraq import MockSkyTraq, NavData, SkyTraq, SkyTraqError

ENCODE_CASES = [
    (0x09, b"\x02\x00", b"\xa0\xa1\x00\x03\x09\x02\x00\x0b\x0d\x0a"),
]
DECODE_CASES = [
    (b"\xa0\xa1\x00\x02\x83\x09\x8a\x0d\x0a", b"\x83\x09"),  # ACK
    (b"\xa0\xa1\x00\x03\x09\x02\x00\x0b\x0d\x0a", b"\x09\x02\x00"),  # BINARY MODE
]


def test_checksum() -> None:
    """Test the checksum method. Uses the body from a binary mode message."""
    assert SkyTraq.checksum(b"\x09\x02\x00") == 11


@pytest.mark.parametrize(("msg_id", "body", "expected"), ENCODE_CASES)
def test_encode_binary(msg_id: int, body: bytes, expected: bytes) -> None:
    """Test the encode method."""
    assert SkyTraq.encode_binary(msg_id, body) == expected


@pytest.fixture
def loopback_skytraq() -> Generator[SkyTraq, Any, None]:
    """Pyserial loopback fixture."""
    gps = SkyTraq.__new__(SkyTraq)
    gps._ser = serial.serial_for_url("loop://", timeout=1)  # noqa: SLF001
    yield gps
    gps._ser.close()  # noqa: SLF001


def test_read(loopback_skytraq: SkyTraq) -> None:
    """Test the read method."""
    loopback_skytraq._ser.write(MockSkyTraq.MOCK_DATA)  # noqa: SLF001
    nav, _payload = loopback_skytraq.read()
    assert isinstance(nav, NavData)


def test_read_terminator_payload(loopback_skytraq: SkyTraq) -> None:
    """Test the read method, with a payload containing a terminator."""
    raw = SkyTraq.encode_binary(0xA8, b"\x0a" * 63)
    loopback_skytraq._ser.write(raw)  # noqa: SLF001
    with pytest.raises(SkyTraqError):
        loopback_skytraq.read()
