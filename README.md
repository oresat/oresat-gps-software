# OreSat GPS Software

Software for OreSat's GPS receiver

## Hardware GPS

Hardware-based GPS using the [SkyTraq Venus838FLPx-L]

### Setup

- `$ sudo apt install python3 python3-pydbus libsystemd-dev python3-serial`

### Building OreSast Debian package

- `$ dpkg-buildpackage -uc -us`
- This will produce `../oresat-gps_*_all.deb`

### Usage

- If installed as a Debian package:
  - `$ sudo systemctl start oresat-gpsd`
- From repo:
  - Add system D-Bus config: `$ sudo cp org.OreSat.GPS.conf /usr/share/dbus-1/system.d/`
  - `$ sudo python3 -m oresat_gps`

## SDR GPS

SDR GPS using the [MAX2771]

TDB

[MAX2771]:https://www.maximintegrated.com/en/products/comms/wireless-rf/MAX2771.html
[SkyTraq Venus838FLPx-L]:https://www.skytraq.com.tw/homesite/Venus838FLPx_PB_v1.pdf
