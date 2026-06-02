"""Tests for the SkyTraq module."""

import pytest

from oresat_gps.skytraq import SkyTraq

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
def test_encode_binary(msg_id: bytes, body: bytes, expected: bytes) -> None:
    """Test the encode method."""
    assert SkyTraq.encode_binary(msg_id, body) == expected


@pytest.mark.parametrize(("raw", "expected"), DECODE_CASES)
def test_decode_binary(raw: bytes, expected: bytes) -> None:
    """Test the SkyTraq binary decoder."""
    payload = SkyTraq.decode_binary(raw)
    assert payload == expected
