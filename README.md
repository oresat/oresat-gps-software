# OreSat GPS Software

Software for OreSat's GPS receiver

## Hardware GPS

Hardware-based GPS using the [SkyTraq Venus838FLPx-L]

### Quickstart

- Build and install device tree overlay (if not mocking SkyTraq)
  - `$ sudo apt install device-tree-compiler`
  - Build dtbo `$ make -C device_tree_overlays`
  - Copy dtbo into firmware directory `$ sudo cp
    device_tree_overlays/gps-00A0.dtbo /lib/firmware/`
  - Edit `/boot/uEnv.txt` and change the `dtb_overlay=` line to
    `dtb_overlay=/lib/firmware/gps-00A0.dtbo`
  - Reboot to apply device tree overlay `$ sudo reboot`
- Install dependencies `$ sudo apt install python3 python3-pydbus libsystemd-dev
  python3-serial`
- Add system D-Bus config `$ sudo cp org.OreSat.GPS.conf
  /usr/share/dbus-1/system.d/`
- To run `$ sudo python3 -m oresat_gps`
  - Run `$ python -m oresat_gps -h` to see all runtime arguments

### Debian Package

- Install dependencies `$ sudo apt install git fakeroot python3-all debhelper
  dh-python device-tree-compiler`
- Build package`$ dpkg-buildpackage -uc -us`
  - This will produce `../oresat-gps_*_all.deb`
- Install Debian package `$ sudo dpkg -i ../oresat-gps_*_all.deb`
- To start the daemon `$ sudo systemctl start oresat-gpsd`

## SDR GPS

SDR GPS using the [MAX2771]

TDB

[MAX2771]:https://www.maximintegrated.com/en/products/comms/wireless-rf/MAX2771.html
[SkyTraq Venus838FLPx-L]:https://www.skytraq.com.tw/homesite/Venus838FLPx_PB_v1.pdf
