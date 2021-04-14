"""Print parsed skytraq NMEA data"""

import io
import sys
import pynmea2
import serial

# first time will fail
try:
    with open("/sys/class/gpio/export", "w") as fptr:
        fptr.write("98")
except PermissionError:
    pass  # first time will fail
with open("/sys/class/gpio/export", "w") as fptr:
    fptr.write("98")
with open("/sys/class/gpio/gpio98/direction", "w") as fptr:
    fptr.write("out")
with open("/sys/class/gpio/gpio98/value", "w") as fptr:
    fptr.write("1")


def main():
    """loop and print data"""

    ser = serial.Serial('/dev/ttyS2', 115200, timeout=5.0)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

    while 1:
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)
            print(repr(msg))
        except serial.SerialException as exc:
            print('Device error: {}'.format(exc))
            break
        except pynmea2.ParseError as exc:
            print('Parse error: {}'.format(exc))
            continue


try:
    main()
except KeyboardInterrupt:
    with open("/sys/class/gpio/gpio98/value", "w") as fptr:
        fptr.write("0")
    sys.exit()
