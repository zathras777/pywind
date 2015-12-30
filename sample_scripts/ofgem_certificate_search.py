#!/usr/bin/env python
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

# Dec 2015 Changes
#
# - year now defaults to current year
# - accreditation changed to generator_id
# - order of filtering updated to avoid conflicts
# - updated output for new object structure
# - verbose flag added to output full output

import argparse
import csv
from datetime import datetime

from pywind.ofgem.Base import to_string
from pywind.ofgem.CertificateSearch import CertificateSearch
from pywind.ofgem.Certificates import CertificateStation


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get ofgem certificates for a given month & year')
    parser.add_argument('--month', type=int, default=1, action='store', help='Month (as a number)')
    parser.add_argument('--year', type=int, default=datetime.today().year, action='store', help='Year')
    parser.add_argument('--generator', action='store', help='Generator ID to search for')
    parser.add_argument('--scheme', action='store', help='Scheme to search (defaults to RO and REGO)')
    parser.add_argument('--filename', action='store', help='Filename to parse')
    parser.add_argument('--output', action='store', help='Filename to store output in (as CVS)')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')

    args = parser.parse_args()

    if args.filename is None:
        print("Contacting Ofgem and preparing to search.\n")
        ocs = CertificateSearch()

        crit = "Searching Ofgem Certificates: "
        crits = []

        if args.scheme:
            ocs.filter_scheme(args.scheme)
            crits.append('\n\tscheme %s' % args.scheme)

        if args.generator:
            ocs.filter_generator_id(args.generator.upper())
            crits.append("\n\tgenerator id is '%s'" % args.generator.upper())

        if args.month:
            ocs.set_month(args.month)
            crits.append('\n\tmonth %s' % args.month)

        if args.year:
            ocs.set_year(args.year)
            crits.append('\n\tyear %s' % args.year)

        print("Searching Ofgem for certificates matching:{}\n".format(", ".join(crits)))
        ocs.get_data()
    else:
        ocs = CertificateSearch(filename=args.filename)

    print("Total of %d records returned" % len(ocs))

    if args.output is None:
        for station in ocs.stations():
            print("{:16s}: {}".format(to_string(station, 'generator_id'), to_string(station, 'name')))
            if station.has_rego:
                print("  REGO:")
                for c in station.get_certs(b'REGO'):
                    print(c.as_string() if args.verbose else str(c))
                print("\n")

            if station.has_ro:
                print("  RO:")
                for c in station.get_certs(b'RO'):
                    print(c.as_string() if args.verbose else str(c))
                print("\n")
    else:
        with open(args.output, 'wt') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(CertificateStation.csv_title_row())
            for s in ocs.stations():
                csv_writer.writerows(s.as_csvrow())
        print("Output saved to file {} [CSV]".format(args.output))
