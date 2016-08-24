#! /usr/bin/env python
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
This script was written to satisfy the following request by a researcher

   For a given list of windfarms, get the capacity and RO certificates
   issued for a given period (or periods), as an Excel spreadsheet

Ofgem were unable to limit their data to the criteria but did supply
an Excel spreadsheet of all their data - which was too large to be
opened on most computers!

To use this script to get the information for the station Braes of Doune

.. code::

    $ ./convert_ro.py 201601 201603
    Enter a station name (or blank to finish)Braes Of Doune
    Enter a station name (or blank to finish)

    Total of 1 stations to process

         Braes Of Doune

    Complete. Generating Excel spreadsheet certificates.xls

When entering station names, you can specify more than one on a line
by seperating them with commas, so rerun the above query for the stations
Braes of Doune and Boulfruich you could do this

.. code::

    $ ./convert_ro.py --start Jan-2010 --end Dec-2010 --filename two_stations

You can also provide a file with one station name per line, using the **--input** parameter.

.. code::

  $ cat station.list
  Braes Of Doune
  Boulfruich
  $ ./convert.py --input station.list 201601 201603

An Ofgem search is conducted for each station name supplied and **all** matching stations are
added to the list of stations to have their certificate information queried and recorded.

The output is minimal but intended to keep you up to date with progress as searching for stations
takes a while.

.. code::

  $ capacity_ro.py 201601 201603 --stations Griffin
  Period covered will be Jan-2016 to Mar-2016. A total of 3 periods
  Station names to be searched for:
      - Griffin
  Enter a station name (or blank to finish)

  Searching for stations...
      - Griffin
          found
  A total of 4 stations will be recorded

  Getting certificate data (this is quicker)...
      - Griffin Wind Farm
          added to spreadsheet
      - William Griffin 6.0kwp
          nothing to add
      - Griffin PV System
          nothing to add
      - Ronald Griffin Solar Hub
          nothing to add

  Data saved to certificates.xls

.. note::

  It would be nice to have better formatting for the output, but as this is just a sample script I haven't
  spent any time adding them, e.g. the date format on the exported spreadsheet needs setting.

"""
from __future__ import print_function

import sys
from datetime import date

from xlwt import Workbook

from pywind.ofgem import CertificateSearch, StationSearch
from pywind.utils import _convert_type, commandline_parser


def add_station_sheet(wbb, stations):
    """ Add a worksheet called Stations to the workbook with details of the stations
    referenced. Certificate details for each station will appear in a seperate sheet
    (one per station).
    """
    ws = wbb.add_sheet('Stations')
    row = 0
    col = 0
    ws.write(row, 0, "Station Details")
    row = 2
    for tit in ['Name', 'Accreditation Number', 'Scheme', 'Technology', 'Capapcity']:
        ws.write(row, col, tit)
        col += 1
    row += 1
    for station in stations:
        ws.write(row, 0, station.name)
        ws.write(row, 1, station.generator_id)
        ws.write(row, 2, station.scheme)
        ws.write(row, 3, station.technology)
        ws.write(row, 4, station.capacity)
        row += 1


def add_certificate_sheet(wbb, station, certs):
    """ Add all certificates to a workbook in a sheet named for the
    station being referenced.
    """
    ws = wbb.add_sheet(station.name)
    row = 0
    ws.write(row, 0, station.name)
    row = 2
    col = 0
    for tit in ['Period', 'Issue Date', 'Scheme', 'No. of Certificates', 'Factor',
                'Status', 'Start No', 'Finish No']:
        ws.write(row, col, tit)
        col += 1
    row += 1
    for cert in certs:
        ws.write(row, 0, cert.period)
        ws.write(row, 1, cert.issue_dt)
        ws.write(row, 2, cert.scheme)
        ws.write(row, 3, cert.certificates)
        ws.write(row, 4, cert.factor)
        ws.write(row, 5, cert.status)
        ws.write(row, 6, cert.start_no)
        ws.write(row, 7, cert.finish_no)
        row += 1


def main():
    """ Function that actually does the work :-) """
    parser = commandline_parser('Download bulk information from Ofgem to produce an Excel spreadsheet')
    parser.add_argument('start', type=int, help='Period to start (YYYYMM)')
    parser.add_argument('end',  type=int, help='Period to finish (YYYYMM)')
    parser.add_argument('--filename',
                        default='certificates.xls',
                        help='Filename to export to')
    parser.add_argument('--stations', nargs='*', help='Stations to search for')
    args = parser.parse_args()
    print(args)

    if not args.filename.endswith('.xls'):
        args.filename += '.xls'

    periods = []
    start_dt = _convert_type(args.start, 'period')
    end_dt = _convert_type(args.end, 'period')
    for yyy in range(start_dt.year, end_dt.year + 1):
        mmm = start_dt.month if start_dt.year == yyy else 1
        mm2 = end_dt.month if end_dt.year == yyy else 12
        for mon in range(mmm, mm2+1):
            periods.append(date(yyy, mon, 1))

    print("Period covered will be {} to {}. A total of {} periods".
          format(start_dt.strftime("%b-%Y"),
                 end_dt.strftime("%b-%Y"),
                 len(periods)))

    stations = []
    station_names = args.stations or []

    if args.input is not None:
        with open(args.input) as fh:
            for line in fh.readlines():
                station = line.strip()
                if '#' in station:
                    (station, dummy_junk) = station.split('#', 1)
                station_names.append(station)

    if len(station_names) > 0:
        print("Station names to be searched for:")
        for stat in station_names:
            print("    - {}".format(stat))

    while True:
        station = raw_input("Enter a station name (or blank to finish)")
        if station.strip() == '':
            break
        if ',' in station:
            for s in station.strip().split(','):
                station_names.append(s)
        else:
            station_names.append(station)

    if len(station_names) == 0:
        print("No stations to process. Exiting...")
        sys.exit(0)

    print("\nSearching for stations...")
    for name in station_names:
        print("    - {}".format(name))
        sss = StationSearch()
        sss.start()
        if sss.filter_name(name) and sss.get_data():
            stations.extend(sss.stations)
            print("        found")
        else:
            print("        no stations found")

    print("A total of {} stations will be recorded".format(len(stations)))

    wbb = Workbook()
    add_station_sheet(wbb, stations)

    print("\nGetting certificate data (this is quicker)...")
    certificates = {}
    for station in stations:
        print("    - {}".format(station.name))
        ocs = CertificateSearch()
        ocs.start()
        if ocs.filter_generator_id(station.generator_id) and \
                ocs.set_start_month(start_dt.month) and \
                ocs.set_start_year(start_dt.year) and \
                ocs.set_finish_month(end_dt.month) and \
                ocs.set_finish_year(end_dt.year) and \
                ocs.get_data():
            certificates[station.name] = ocs.cert_list
            add_certificate_sheet(wbb, station, ocs.certificates)
            print("        added to spreadsheet")
        else:
            print("        nothing to add")

    wbb.save(args.filename)
    print("\nData saved to {}".format(args.filename))


if __name__ == '__main__':
    main()
