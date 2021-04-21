"""Skytraq message parser"""

from enum import IntEnum
import struct


class NavData(IntEnum):
    """NavData offsets for skytraq binary data"""

    MESSAGE_ID = 0
    FIX_MODE = 1
    NUMBER_OF_SV = 2
    GPS_WEEK = 3
    TOW = 4
    LATITUDE = 5
    LONGITUDE = 6
    ELLIPSOID_ALTITUDE = 7
    MEAN_SEA_LVL_ALTITYDE = 8
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


def power_on():
    """ Turn the skytraq on"""
    try:
        # first time will fail
        with open("/sys/class/gpio/export", "w") as fptr:
            fptr.write("98")
        with open("/sys/class/gpio/export", "w") as fptr:
            fptr.write("98")
    except PermissionError:
        pass  # first time will fail
    with open("/sys/class/gpio/gpio98/direction", "w") as fptr:
        fptr.write("out")
    with open("/sys/class/gpio/gpio98/value", "w") as fptr:
        fptr.write("1")

    try:
        # first time will fail
        with open("/sys/class/gpio/export", "w") as fptr:
            fptr.write("100")
        with open("/sys/class/gpio/export", "w") as fptr:
            fptr.write("100")
    except PermissionError:
        pass  # first time will fail
    with open("/sys/class/gpio/gpio100/direction", "w") as fptr:
        fptr.write("out")
    with open("/sys/class/gpio/gpio100/value", "w") as fptr:
        fptr.write("1")


def power_off():
    with open("/sys/class/gpio/gpio98/value", "w") as fptr:
        fptr.write("0")
    with open("/sys/class/gpio/gpio100/value", "w") as fptr:
        fptr.write("0")


def parse_skytraq_binary(line) -> ():
    """Parse the skytraq binary message."""

    data = None

    if len(line) < 7:
        return data

    if line[:2] != b'\xA0\xA1' or line[:-2] != b'\x0D\x0A':
        return data

    payload_len = line[2:]
    payload_len = payload_len[:2]

    try:
        if line[3] == '\x83' and payload_len == b'\x00\x02':  # ACK
            data = struct.unpack('=4x2B3x', line)
        elif line[3] == '\x84' and payload_len == b'\x00\x02':  # ACK
            data = struct.unpack('=4x2B3x', line)
        elif line[3] == '\xA8' and payload_len == b'\x00\x3B':  # nav data
            data = struct.unpack('=4x3BHI2i2I5H6i3x', line)
    except struct.error:
        data = None

    return data
