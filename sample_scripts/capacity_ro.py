#! /usr/bin/env python
# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

""" capacity_ro.py

    This script was written to satisfy the following request by a
    researcher

       "for a given list of windfarms, capacity and RO certificates
        for a given period, as an Excel spreadsheet"

    Ofgem were unable to limit their data to the criteria but did supply
    an Excel spreadsheet of all their data - which was too large to be
    opened on most computers!

    To use this script to get the information for the station Braes of Doune

    $ ./convert_ro.py --start Jan-2010 --end Dec-2010
    Enter a station name (or blank to finish)Braes Of Doune
    Enter a station name (or blank to finish)

    Total of 1 stations to process

         Braes Of Doune

    Complete. Generating Excel spreadsheet certificates.xls
    $

    When entering station names, you can specify more than one on a line
    by seperating them with commas, so rerun the above query for the stations
    Braes of Doune and Boulfruich you could do this

    $ ./convert_ro.py --start Jan-2010 --end Dec-2010 --filename two_stations
    Enter a station name (or blank to finish)Braes Of Doune, Boulfruich
    Enter a station name (or blank to finish)

    Total of 2 stations to process

         Braes Of Doune
         Boulfruich

    Complete. Generating Excel spreadsheet two_stations.xls
    $

    Station names are looked up and the full name and accreditation number
    for the RO scheme are listed in the output.
"""

import sys
import argparse
from datetime import date
from xlwt import Alignment, XFStyle, Workbook, Worksheet

from pywind.ofgem import CertificateSearch, StationSearch
from pywind.ofgem.utils import get_period

PERIOD_START = 6

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download bulk information from Ofgem to produce an Excel spreadsheet')
    parser.add_argument('--start', action='store', required=True, help='Period to start from (MMM-YYYY)')
    parser.add_argument('--end', action='store', required=True, help='Period to finish on (MMM-YYYY)')
    parser.add_argument('--scheme', action='store', default='RO', help='Scheme to get certificates for')
    parser.add_argument('--filename', action='store', default='certificates.xls', help='Filename to export to')
    args = parser.parse_args()

    (start_year, start_month) = get_period(args.start)
    (end_year, end_month) = get_period(args.end)
    if not args.filename.endswith('.xls'):
        args.filename += '.xls'

    periods = []
    for yy in range(start_year, end_year + 1):
        mm = start_month if start_year == yy else 1
        mm2 = end_month if end_year == yy else 12
        for m in range(mm, mm2+1):
            periods.append(date(yy,m,1).strftime("%b-%Y"))

    stations = []
    while (True):
        station = raw_input("Enter a station name (or blank to finish)")
        if station.strip() == '':
            break
        if ',' in station:
            for s in station.strip().split(','):
                s = s.strip()
                if s in stations:
                    continue
                stations.append(s)
        else:
            station = station.strip()
            if station in stations:
                continue
            stations.append(station)

    if len(stations) == 0:
        print "No stations to process. Exiting..."
        sys.exit(0)

    wb = Workbook()
    ws = wb.add_sheet('Certificate Data', cell_overwrite_ok=True)
    ws.write(PERIOD_START - 1,0,"Period")
    for i in range(0, len(periods)):
        ws.write(PERIOD_START + i, 0, periods[i])

    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    al.vert = Alignment.VERT_CENTER

    title_style = XFStyle()
    title_style.alignment = al

    print "\nTotal of %d stations to process\n" % len(stations)
    for i in range(0, len(stations)):
        s = stations[i]
        col = 1 + 5 * i
        print "    ", s

        # add headers
        ws.write(PERIOD_START - 1, col, "Installed Capacity")
        ws.write(PERIOD_START - 1, col + 1, "RO Certificates")
        ws.write(PERIOD_START - 1, col + 2, "RO Factor")
        ws.write(PERIOD_START - 1, col + 3, "REGO Certificates")
        ws.write(PERIOD_START - 1, col + 4, "REGO Factor")

        capacity = {}
        for scheme in ['RO','REGO']:
            offset = 1 if scheme == 'RO' else 3
            ss = StationSearch()
            ss.for_wind()
            ss.set_scheme(scheme)
            ss.station = s
            if not ss.get_data():
                print "Unable to find any station with a name %s" % s
                continue

            station = None
            if len(ss) > 1:
                for st in ss.stations:
 #                   print st.as_string()
                    if 'wind' in st.technology.lower():
                        station = st
                        break
            else:
                station = ss.stations[0]

            if station is None:
                print "Unable to get station data for '%s'" % s
                continue

            # Write name
            ws.write_merge(PERIOD_START - 4, PERIOD_START - 4, col, col + 4,
                           station.name, title_style)
            # add accreditation #
            if scheme == 'RO':
                ws.write_merge(PERIOD_START - 2, PERIOD_START - 2, col, col + 4,
                               'RO: ' + station.accreditation + '  [' + station.commission_dt.strftime("%d %b %Y") + ']',
                               title_style)
            elif scheme == 'REGO':
                ws.write_merge(PERIOD_START - 3, PERIOD_START - 3, col, col + 4,
                               'REGO: ' + station.accreditation + '  [' + station.commission_dt.strftime("%d %b %Y") + ']',
                               title_style)

            cs = CertificateSearch()

            cs.set_scheme(scheme)
            cs.set_start_month(start_month)
            cs.set_start_year(start_year)
            cs.set_finish_month(end_month)
            cs.set_finish_year(end_year)
            cs.accreditation = station.accreditation

            if not cs.get_data():
                print "Unable to get any certificate data :-("
                continue

            data = {}
            for c in cs.certificates:
#                print c.as_string()
                if c['status'] in ['Revoked','Retired','Expired']:
                    continue

                row = periods.index(c.period) + PERIOD_START
                if not capacity.has_key(c.period):
                    ws.write(row, col, c.capacity)
                    capacity[c.period] = True

                data[c.period] = data.get(c.period,0) + c.certs
                ws.write(row, col + offset + 1, c.factor)

            for p,val in data.iteritems():
                row = periods.index(p) + PERIOD_START
                ws.write(row, col + offset, val)

    print "\nComplete. Excel spreadsheet %s" % args.filename
    wb.save(args.filename)