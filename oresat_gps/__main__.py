from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

from .gps_resource import GPSResource


def main():
    parser = ArgumentParser(parents=[app_args_parser])
    parser.add_argument('-m', '--mock-hw', action='store_true', help='mock hardware')
    args = parser.parse_args()
    parse_app_args(args)

    app = App(f'{dirname(abspath(__file__))}/data/oresat_gps.dcf', args.bus, args.node_id)

    app.add_resource(GPSResource(app.node, args.mock_hw))

    app.run()


if __name__ == '__main__':
    main()
