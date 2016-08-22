#!/usr/bin/env python
# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
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

"""
Sample script to demonstrate using :mod:`pywind` to search for Ofgem Stations.

.. code::

  $ ofgem_station_search.py --station Griffin
  Connecting with Ofgem website and preparing the search...
  Setting up filters:
    - station name contains Griffin

  Getting results from Ofgem...

  Query returned 4 results
    Station Name                         Commission Dt  Capacity      Technology            Country               Generator ID
    -----------------------------------  -------------  ------------  --------------------  --------------------  ---------------
    Griffin Wind Farm                    2011-07-05        186170.00  On-shore wind (RO...  Scotland              R00160SQSC
    William Griffin 6.0kwp               2013-11-21             6.00  PV with a DNC of ...  Northern Ireland      R03770NGNI
    Griffin PV System                    2014-11-20             3.50  PV with a DNC of ...  Northern Ireland      R09926NGNI
    Ronald Griffin Solar Hub             2014-09-19             4.00  PV with a DNC of ...  Northern Ireland      R09542NGNI


.. code::

  $ ofgem_station_search.py --organisation Speedwell
  Connecting with Ofgem website and preparing the search...
  Setting up filters:
    -  organisation contains Speedwell

  Getting results from Ofgem...

  Query returned 1 results
    Station Name                         Commission Dt  Capacity      Technology            Country               Generator ID
    -----------------------------------  -------------  ------------  --------------------  --------------------  ---------------
    Speedwell                            2013-10-01             6.50  PV with a DNC of ...  Northern Ireland      R03360NGNI

"""

import sys

from pywind.log import setup_logging
from pywind.ofgem import StationSearch
from pywind.utils import commandline_parser, StdoutFormatter


def main():
    parser = commandline_parser('Search ofgem database for matching stations')
    parser.add_argument('--generator', action='store', help='Generator ID to search for')
    parser.add_argument('--organisation', action='store', help='Organisation to search for')

    args = parser.parse_args()

    if args.station is None and \
                    args.generator is None and \
                    args.organisation is None:
        print("You must specify either a name, generator id or organisation")
        sys.exit(0)

    setup_logging(args.debug, request_logging=args.request_debug)

    print("Connecting with Ofgem website and preparing the search...")
    osd = StationSearch()
    osd.start()

    print("Setting up filters:")

    if args.station is not None:
        osd.filter_name(args.station)
        print("    - station name contains {}".format(args.station))

    if args.organisation:
        osd.filter_organisation(args.organisation)
        print("    -  organisation contains {}".format(args.organisation))

    if args.generator:
        if args.generator.upper()[0] in ['R', 'P']:
            osd.filter_scheme('RO')
        elif args.generator.upper()[0] == 'G':
            osd.filter_scheme('REGO')
        osd.filter_generator_id(args.generator.upper())
        print("    - generator ID is {}".format(args.generator.upper()))

    print("\nGetting results from Ofgem...\n")

    if osd.get_data() is False:
        print("Search returned no data")
        sys.exit(0)

    print("Query returned {} result{}".format(len(osd), '' if len(osd) == 0 else 's'))

    fmt = StdoutFormatter("35s", "13s", "12.2f", "20s", "20s", "15s")
    print(fmt.titles("Station Name", "Commission Dt", "Capacity",
                     "Technology", "Country", "Generator ID"))

    for stat in osd.rows():
        # The rows() output is intended for exporting, so fields will have '@' prepended
        # if they are attributes.
        # This could also be done by using osd.stations
        station = stat.get('Station')
        if station is None:
            continue
        cdt = station.get('@commission_dt')
        print(fmt.row(station.get('@name'),
                      cdt.strftime("%Y-%m-%d") if cdt else 'n/a',
                      station.get('@capacity'),
                      station.get('@technology'),
                      station.get('@country'),
                      station.get('@generator_id')))


if __name__ == '__main__':
    main()
