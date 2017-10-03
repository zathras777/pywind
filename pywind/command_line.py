# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

"""Functions that provide the command line script functionality."""

from __future__ import print_function

import sys
import os

from pywind.decc.cmd import decc_extract
from pywind.elexon.cmd import elexon_b1320, elexon_b1420, elexon_b1330, \
                              elexon_generation_inst, elexon_sbp, \
                              elexon_bm_data, elexon_bm_unit, elexon_b1610, \
                              elexon_b1630, elexon_uou2t52w
from pywind.log import setup_logging
from pywind.ofgem.cmd import ofgem_certificate_search,\
    ofgem_station_search
from pywind.roc.cmd import roc_prices
from pywind.utils import commandline_parser
from pywind.export import export_to_file
from pywind import __version__


COMMANDS = [
    decc_extract,
    ofgem_certificate_search,
    ofgem_station_search,
    roc_prices,
    elexon_generation_inst,
    elexon_b1320,
    elexon_b1330,
    elexon_b1420,
    elexon_b1610,
    elexon_b1630,
    elexon_sbp,
    elexon_bm_data,
    elexon_bm_unit,
    elexon_uou2t52w
]
COMMAND_NAMES = {}


def build_command_names():
    """ Use the list of commands available to build the COOMAND_NAMES dict.
    """
    for cmd in COMMANDS:
        doc = cmd.__doc__.strip() if cmd.__doc__ is not None else 'Unknown'
        doc = doc.split('\n')[0]
        COMMAND_NAMES[cmd.__name__] = {'name': doc, 'function': cmd}


def commands_help():
    hlp = "Commands presently available are:\n\n"
    for key in sorted(COMMAND_NAMES):
        hlp += "  {:30s}  {}\n".format(key, COMMAND_NAMES[key]['name'])
    return hlp


def main():
    """ Main command line function.
    """
    build_command_names()
    parser = commandline_parser("pywind command line app, version {}".format(__version__),
                                epilog=commands_help())
    parser.add_argument('command', nargs='?', help='Command to execute (see below for list)')
    args = parser.parse_args()

    if args.version:
        print("pywind version {}".format(__version__))
        sys.exit(0)

    if args.apikey is not None and os.path.exists(args.apikey):
        print("Reading API Key from {}".format(args.apikey))
        with open(args.apikey, 'r') as apifh:
            args.apikey = apifh.read().strip()

    cmd = COMMAND_NAMES.get(args.command, None)
    if cmd is None:
        if args.command is not None:
            print("Invalid command specified: {}".format(args.command))
        print(commands_help())
        sys.exit(0)

    setup_logging(args.debug, request_logging=args.request_debug,
                  filename=args.log_filename)

    print("\n{}\n{}\n".format(cmd['name'], "=" * len(cmd['name'])))
    obj = cmd['function'](args)

    if args.save:
        filename = args.original or args.command
        if hasattr(obj, 'save_original'):
            if obj.save_original(filename) is False:
                print("Unable to save the downloaded data :-(")
            else:
                print("Downloaded data saved to {}".format(filename))
        else:
            print("Saving data is not supported for this command.")

    if args.export is not None:
        export_to_file(args, obj)


if __name__ == '__main__':
    main()
