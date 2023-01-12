import os

from flask import Blueprint, render_template
from olaf import app, rest_api, olaf_run

from .gps_resource import GPSResource

gps_bp = Blueprint('gps_template', __name__, template_folder='templates')


@gps_bp.route('/skytraq')
def skytraq_template():
    return render_template('skytraq.html', title=os.uname()[1], name='SkyTraq')


def main():
    app.add_resource(GPSResource)
    rest_api.add_blueprint(gps_bp)

    olaf_run(f'{os.path.dirname(os.path.abspath(__file__))}/data/oresat_gps.dcf')


if __name__ == '__main__':
    main()
