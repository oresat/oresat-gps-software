"""Print parsed skytraq binary data"""

import sys
import struct
import io
from serial import Serial, SerialException


def main():
    """loop and print data"""

    # open serial
    ser = Serial('/dev/ttyS2', 9600, timeout=5.0)

    # swap to binary mode
    ser.write(b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A')

    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')

    try:
        line = sio.readline()
    except SerialException as exc:
        print('Device error: {}\n'.format(exc))
        sys.exit(1)

    while 1:
        try:
            line = sio.readline()
        except SerialException as exc:
            print('Device error: {}\n'.format(exc))
            break

        print(line)

        try:
            data = struct.unpack('>4x3BHI2i2I5H6i3x', line)
        except struct.error as exc:
            print('Parse error: {}\n'.format(exc))
            continue

        print(data)
        print("")


try:
    main()
except KeyboardInterrupt:
    sys.exit()
