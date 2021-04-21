"""Print parsed skytraq NMEA data"""

import io
import sys
import pynmea2
import serial
from oresat_gps.skytraq import power_on, power_off


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
    power_on()
    main()
except KeyboardInterrupt:
    power_off()
    sys.exit()
