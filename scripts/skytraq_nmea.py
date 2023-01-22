#!/usr/bin/env python3
"""Print parsed skytraq NMEA data"""

import io
import sys

import pynmea2
import serial


def main():
    """loop and print data"""

    ser = serial.Serial('/dev/ttyS2', 9600, timeout=5.0)
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
    sys.exit()
