"""Log skytraq binary data"""

import sys
from datetime import datetime
import struct
from serial import Serial, SerialException

# open data file
time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
fptr = open("skytraq_data_" + time_str + ".txt", "wb")
fptr2 = open("skytraq_bi_data_" + time_str + ".csv", "w")


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


def main():
    """loop and print data"""

    # open serial
    ser = Serial('/dev/ttyS2', 9600, timeout=5.0)

    # swap to binary mode
    ser.write(b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A')

    try:
        line = ser.readline()
    except SerialException as exc:
        print('Device error: {}\n'.format(exc))
        sys.exit(1)

    while 1:
        try:
            line = ser.readline()
        except SerialException as exc:
            print('Device error: {}\n'.format(exc))
            continue

        fptr.write(line)
        fptr.flush()

        try:
            data = struct.unpack('=4x3BHI2i2I5H6i3x', line)
        except struct.error as exc:
            print('Parse error: {}\n'.format(exc))
            continue

        fptr2.write(data[1:-1] + '\n')
        fptr2.flush()


try:
    power_on()
    main()
except KeyboardInterrupt:
    power_off()
    fptr.close()
    sys.exit()
