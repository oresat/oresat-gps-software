import logging
from argparse import ArgumentParser
from pathlib import Path

from oresat_cand import NodeClient

from .gen.gps_od import GpsEntry
from .gps import Gps


def get_hw_version() -> str:
    version = ""
    try:
        with open("/sys/bus/i2c/devices/0-0050/eeprom", "rb") as f:
            raw = f.read(28)
            version = raw[12:16].decode()
            version = f"{int(version[:2])}.{int(version[2:])}"
    except Exception:
        logging.critical("failed to read hardware version from eeprom")
    return version


def main():
    parser = ArgumentParser()
    parser.add_argument("-s", "--serial", default="/dev/ttyS2", help="serial port path")
    parser.add_argument(
        "-w",
        "--hardware-version",
        choices=Gps.SUPPORTED_HW_VERSIONS,
        default="",
        help="will detect if not set",
    )
    parser.add_argument("-m", "--mock-hw", action="store_true", help="mock hardware")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose logging")
    args = parser.parse_args()

    LOG_FMT = "%(levelname)s: %(filename)s:%(lineno)s - %(message)s"
    logging.basicConfig(format=LOG_FMT)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    hw_version = args.hardware_version
    if args.hardware_version and not args.mock_hw:
        get_hw_version()

    od_config_path = Path(__file__).parent / "gen/od.csv"
    node = NodeClient(GpsEntry, od_config_path=od_config_path)
    gps = Gps(hw_version, args.serial, node, args.mock_hw)

    try:
        gps.run()
    except KeyboardInterrupt:
        pass

    gps.stop()


if __name__ == "__main__":
    main()
