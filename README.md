# OreSat GPS Software

OreSat GPS software runs the OreSat GPS card and publishes navigation data to the satellite over CANopen. It is designed to hide receiver-specific details and provide a consistent interface for the rest of the flight software.

This app targets custom OreSat GPS hardware ([oresat-gps-hardware]) and supports two reception paths on the card:
- SkyTraq Orion B16 (current operational path)
- MAX2771 SDR path (hardware present; software path not yet implemented in this repo)

The CANopen-facing interface provides GPS-derived data such as position, velocity, fix quality, satellites-in-view, and time fields used by other systems. During development, you can inspect CAN traffic with tools like `candump` and interact with objects through standard CANopen tooling.

GPS is also used as a high-quality time reference. When a valid fix is available, the app can synchronize system time so other spacecraft services share a common clock base for telemetry correlation, event ordering, and time-sensitive control loops.

In the wider satellite stack, this data is consumed by components like ADCS and mission operations pipelines for state estimation, timeline reconstruction, and post-pass analysis.

Like other OreSat apps, this project is built on OLAF. When running locally, OLAF's debug interface is available at `http://localhost:8000`, including a GPS page at `http://localhost:8000/skytraq`.

## Quick Start

Install dependencies.

```bash
pip3 install . --group dev
```
Make a virtual CAN bus.

```bash
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
```

Run the GPS app.

```bash
python3 -m oresat_gps
```

Select the CAN bus to use (`vcan0`, `can0`, etc) with the `-b BUS` arg.

Mock hardware by using the `-m HARDWARE` flag.

- The `-m all` flag can be used to mock all hardware (CAN bus is always
required).
- The `-m skytraq` flag would only mock the skytraq

See other options with `-h` flag.

A basic [Flask]-based website for development and integration can be found at
`http://localhost:8000` when the software is running.

## Architecture Notes

Low-level receiver protocol details are intentionally abstracted behind the app interface, but for maintainers:
- The SkyTraq path is implemented in a userspace driver at [`oresat_gps/skytraq.py`](./oresat_gps/skytraq.py).
- Host-to-SkyTraq commands use the SkyTraq binary protocol (see [AN0037]).
- SkyTraq navigation reports are parsed and mapped into CANopen object dictionary entries.

[Flask]: https://flask.palletsprojects.com/en/latest/
[oresat-gps-hardware]: https://github.com/oresat/oresat-gps-hardware
[oresat-olaf repo]: https://github.com/oresat/oresat-olaf
[CANopen for Python]: https://github.com/christiansandberg/canopen
[AN0037]: https://www.skytraq.com.tw/homesite/AN0037.pdf
