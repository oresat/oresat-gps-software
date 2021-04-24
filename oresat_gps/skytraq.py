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
    """ Turn the skytraq off"""
    with open("/sys/class/gpio/gpio98/value", "w") as fptr:
        fptr.write("0")
    with open("/sys/class/gpio/gpio100/value", "w") as fptr:
        fptr.write("0")


def parse_skytraq_binary(line) -> ():
    """Parse the skytraq binary message."""

    data = None

    if valid_message(line):
        try:
            data = struct.unpack('>4x3BHI2i2I5H6i3x', line)
        except struct.error:
            data = None

    return data


def valid_message(message) -> bool:
    """check is the checksum is correct"""

    message_len = len(message)
    body_len = message_len - 7

    if message_len <= 7:
        return False

    pl_bytes = message[2: (len(message) - 4) * -1]

    try:
        pl = struct.unpack('>H', pl_bytes)
    except struct.error as exc:
        print('Parse error: {}\n'.format(exc))
        return False

    if body_len != pl[0]:
        print('payload len error: {} {}'.format(body_len, pl[0]))
        return False

    cs = 0
    for i in message[4:-3]:
        cs = cs ^ i

    if cs != message[-3]:
        print("invalid cs")
        return False

    return True
