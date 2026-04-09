"""GPS OLAF app."""

from importlib.resources import files
from pathlib import Path

from olaf import app, logger, olaf_run, olaf_setup, render_olaf_template, rest_api

from oresat_gps.gps_service import GpsService
from oresat_gps.skytraq import MockSkyTraq, SkyTraq, SkyTraq10, SkyTraq11

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0"  # package is not installed

__all__ = ["__version__", "main"]


@rest_api.app.route("/skytraq")
def skytraq_template() -> str:
    """Render skytraq webpage."""
    return render_olaf_template("skytraq.html", name="SkyTraq")


def main() -> None:
    """GPS OLAF app main."""
    args, _ = olaf_setup("gps")
    mock_args = [i.lower() for i in args.mock_hw]
    mock_skytraq = "skytraq" in mock_args or "all" in mock_args

    app.od["versions"]["sw_version"].value = __version__
    hw_version = app.od["versions"]["hw_version"].value

    if mock_skytraq:
        logger.debug("Mocking the skytraq.")
        skytraq: SkyTraq = MockSkyTraq()
    elif hw_version == "1.0":
        skytraq = SkyTraq10(Path("/dev/ttyS2"))
    elif hw_version == "1.1":
        skytraq = SkyTraq11(Path("/dev/ttyS2"))
    else:
        logger.error("Invalid gps board version")
        # attempt the latest anyway
        skytraq = SkyTraq11(Path("/dev/ttyS2"))

    app.add_service(GpsService(skytraq))

    rest_api.add_template(files('oresat_gps') / 'templates' / 'skytraq.html')

    olaf_run()


if __name__ == "__main__":
    main()
