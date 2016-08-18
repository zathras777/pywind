"""Functions that provide the command line script functionality."""

from __future__ import print_function

import sys

from pywind.bmreports.cmd import *  # pylint: disable=unused-import
from pywind.ofgem.cmd import *      # pylint: disable=unused-import
from pywind.log import setup_logging
from pywind.utils import commandline_parser


COMMANDS = {
    'bm_generation_type': 'BM Report by Generation Type',
    'bm_system_prices': 'BM Report Electricity Prices',
    'bm_unitdata': 'BM Report Unit Data',
    'ofgem_certificates': 'Ofgem Certificate parser',
    'ofgem_certificate_search': 'Ofgem Certificate Search',
    'ofgem_station_search': 'Ofgem Station Search',
}


def main():
    """ Main command line function.
    """
    parser = commandline_parser("pywind command line app")
    parser.add_argument('command', nargs='?', help='Command to execute')
    args = parser.parse_args()

    cmd = COMMANDS.get(args.command, None)
    if cmd is None:
        if args.command is not None:
            print("Invalid command specified: {}".format(args.command))
        print("Possible commands are:")
        for key in sorted(COMMANDS.keys()):
            print("  {:30s}  {}".format(key, COMMANDS[key]))
        sys.exit(0)

    setup_logging(args.debug, request_logging=args.request_debug,
                  filename=args.log_filename)

    cmd_fn = globals()[args.command]
    cmd_fn(args)


if __name__ == '__main__':
    main()
