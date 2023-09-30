import os

from olaf import app, olaf_run, olaf_setup, render_olaf_template, rest_api

from .gps_service import GpsService


@rest_api.app.route("/skytraq")
def skytraq_template():
    return render_olaf_template("skytraq.html", name="SkyTraq")


def main():
    path = os.path.dirname(os.path.abspath(__file__))

    args = olaf_setup(f"{path}/data/oresat_gps.dcf")
    mock_args = [i.lower() for i in args.mock_hw]
    mock_skytraq = "skytraq" in mock_args or "all" in mock_args

    app.add_service(GpsService(mock_skytraq))

    rest_api.add_template(f"{path}/templates/skytraq.html")

    olaf_run()


if __name__ == "__main__":
    main()
