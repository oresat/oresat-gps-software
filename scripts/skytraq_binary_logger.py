"""Log skytraq binary data"""

import sys
from serial import Serial, SerialException

# first time will fail
with open("/sys/class/gpio/export", "w") as fptr:
    fptr.write("98")
with open("/sys/class/gpio/export", "w") as fptr:
    fptr.write("98")
with open("/sys/class/gpio/gpio98/direction", "w") as fptr:
    fptr.write("out")
with open("/sys/class/gpio/gpio98/value", "w") as fptr:
    fptr.write("1")

# open data file
fptr = open("data.txt", "ab")

# open serial
ser = Serial('/dev/ttyS2', 115200, timeout=5.0)

# swap to binary mode and assert ACK
ser.write(b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A')
try:
    line = ser.readline()
except SerialException as exc:
    print('Device error: {}\n'.format(exc))
    sys.exit(1)
assert line == b'\xa0\xa1\x00\x02\x83\t\x8a\r\n'

while 1:
    try:
        line = ser.readline()
    except SerialException as exc:
        print('Device error: {}\n'.format(exc))
        break

    fptr.write(line)

fptr.close()
