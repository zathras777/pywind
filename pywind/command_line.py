"""Functions that provide the command line script functionality."""

import sys
from pprint import pprint

from pywind.bmreports.cmd import *
from pywind.log import setup_logging
from pywind.utils import commandline_parser, multi_level_get


COMMANDS = {
    'bm_generation_type': ('BM Report by Generation Type', 'bm_generation_type'),
    'bm_system_prices': ('BM Report Electricity Prices', 'bm_systemprices'),
    'bm_unitdata': ('BM Report Unit Data', 'bm_unitdata'),
}


def main():
    parser = commandline_parser("pywind command line app")
    parser.add_argument('command', nargs='?', help='Command to execute')
    args = parser.parse_args()

    cmd = COMMANDS.get(args.command, None)
    if cmd is None:
        if args.command is not None:
            print("Invalid command specified: {}".format(args.command))
        print("Possible commands are:")
        for key in sorted(COMMANDS.keys()):
            print("  {:30s}  {}".format(key, COMMANDS[key][0]))
        sys.exit(0)

    setup_logging(args.debug, request_logging=args.request_debug)

    cmd_fn = globals()[cmd[1]]
    cmd_fn(cmd, args)


if __name__ == '__main__':
    main()
