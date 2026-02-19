from oresat_gps.skytraq import SkyTraq


def test_checksum() -> None:
    assert SkyTraq.checksum(b"\x09\x02\x00") == 11

def test_encode_binary() -> None:
    # binary mode message
    assert SkyTraq.encode_binary(0x09, b"\x02\x00") == b"\xa0\xa1\x00\x03\x09\x02\x00\x0b\x0d\x0a"