"""Functions that provide the command line script functionality."""

from __future__ import print_function

import os
import sys

from pywind.bmreports.cmd import *  # pylint: disable=unused-import
from pywind.ofgem.cmd import *      # pylint: disable=unused-import
from pywind.roc.cmd import roc_prices
from pywind.decc.cmd import decc_extract
from pywind.log import setup_logging
from pywind.utils import commandline_parser
from pywind.export import export_to_file


COMMANDS = {
    'bm_generation_type': 'BM Report by Generation Type',
    'bm_system_prices': 'BM Report Electricity Prices',
    'bm_unitdata': 'BM Report Unit Data',
    'decc_extract': 'DECC Monthly Planning Extract',
    'ofgem_certificates': 'Ofgem Certificate parser',
    'ofgem_certificate_search': 'Ofgem Certificate Search',
    'ofgem_station_search': 'Ofgem Station Search',
    'roc_prices': 'eROC Auction Prices'
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
    obj = cmd_fn(args)

    if args.save:
        filename = args.original or args.command
        if hasattr(obj, 'save_original'):
            if obj.save_original(filename) is False:
                print("Unable to save the downloadd data :-(")
            else:
                print("Downloaded data saved to {}".format(filename))
        else:
            print("Saving data is not supported for this command.")

    if args.export is not None:
        export_to_file(args, obj)


if __name__ == '__main__':
    main()
