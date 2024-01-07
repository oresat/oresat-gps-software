"""GPS OLAF app main"""

import os

from olaf import Gpio, app, olaf_run, olaf_setup, render_olaf_template, rest_api

from . import __version__
from .gps_service import GpsService
from .skytraq import SkyTraq


@rest_api.app.route("/skytraq")
def skytraq_template():
    """Render skytraq webpage."""

    return render_olaf_template("skytraq.html", name="SkyTraq")


def main():
    """GPS OLAF app main"""

    path = os.path.dirname(os.path.abspath(__file__))

    args, _ = olaf_setup("gps")
    mock_args = [i.lower() for i in args.mock_hw]
    mock_skytraq = "skytraq" in mock_args or "all" in mock_args

    app.od["versions"]["sw_version"].value = __version__

    skytraq = SkyTraq("/dev/ttyS2", mock_skytraq)
    gpio_lna = Gpio("MAX_EN", mock_skytraq)
    gpio_skytraq = Gpio("STQ_EN", mock_skytraq)

    app.add_service(GpsService(skytraq, gpio_lna, gpio_skytraq))

    rest_api.add_template(f"{path}/templates/skytraq.html")

    olaf_run()


if __name__ == "__main__":
    main()
