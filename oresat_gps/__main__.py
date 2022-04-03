from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

from .gps_resource import GPSResource

if __name__ == '__main__':

    parser = ArgumentParser(parents=[app_args_parser])
    args = parser.parse_args()
    parse_app_args(args)

    app = App(dirname(abspath(__file__)) + '/data/oresat_gps.eds', args.bus, args.node_id)

    app.add_resource(GPSResource(app.node))

    app.run()
