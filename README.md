# OreSat GPS Software

Software for Linux version of the GPS card.

Like all OreSat software projects it is built using OLAF (OreSat Linux App
Framework), which it built ontop of [CANopen for Python]. See the
[oresat-olaf repo] for more info about OLAF.

## Quickstart

Install dependenies

```bash
$ pip3 install -r requirements.txt
```
Make a virtual CAN bus

```bash
$ sudo ip link add dev vcan0 type vcan
$ sudo ip link set vcan0 up
```

Run the GPS app

```bash
$ python3 -m oresat_gps
```

Can select the CAN bus to use (`vcan0`, `can0`, etc) with the `-b BUS` arg.

Can mock hardware by using the `-m HARDWARE` flag.

- The`-m all` flag can be used to mock all hardware (CAN bus is always
required).
- The `-m skytraq` flag would only mock the skytraq

See other options with `-h` flag.

A basic [Flask]-based website for development and integration can be found at
`http://localhost:8000` when the software is running.

[Flask]: https://flask.palletsprojects.com/en/latest/
[oresat-olaf repo]: https://github.com/oresat/oresat-olaf
[CANopen for Python]: https://github.com/christiansandberg/canopen
