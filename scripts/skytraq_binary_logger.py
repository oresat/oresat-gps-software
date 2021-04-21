"""Log skytraq binary data"""

import sys
from datetime import datetime
from serial import Serial, SerialException
from oresat_gps.skytraq import power_on, power_off

# open data file
time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
fptr = open("skytraq_data_" + time_str + ".txt", "wb")
# working directory assume debian user and repo in home dir


def main():
    """loop and print data"""

    # open serial
    ser = Serial('/dev/ttyS2', 115200, timeout=5.0)

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


try:
    power_on()
    main()
except KeyboardInterrupt:
    fptr.close()
    power_off()
    sys.exit()
