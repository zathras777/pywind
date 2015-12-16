#!/usr/bin/env python
# coding=utf-8

# Copyright 2013-2015 david reid <zathrasorama@gmail.com>
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

import argparse
import csv
from pywind.ofgem import StationSearch
from pywind.ofgem.Station import Station



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search ofgem database for matching stations')
    parser.add_argument('--name', action='store', help='Station name to search for')
    parser.add_argument('--generator', action='store', help='Generator ID to search for')
    parser.add_argument('--scheme', action='store', default='REGO',
                        help='Scheme to search (ignored for accreditation) [default REGO]')
    parser.add_argument('--organisation', action='store', help='Organisation to search for')
    parser.add_argument('--output', action='store', help='Filename to output data into (as CSV)')

    args = parser.parse_args()

    print("Connecting with Ofgem website and preparing the search...")
    osd = StationSearch()

    crit = "Searching for Ofgem Stations where:\n\tscheme is %s" % args.scheme

    osd.filter_scheme(args.scheme)

    if args.name:
        osd.filter_name(args.name)
        crit += "\n\tname contains '%s'" % args.name

    if args.organisation:
        osd['organisation'] = args.organisation
        crit += "\n\torganisation is '%s'" % args.organisation

    if args.generator:
        if args.generator.upper()[0] == 'R':
            osd.filter_scheme('RO')
        elif args.generator.upper()[0] == 'G':
            osd.filter_scheme('REGO')
        osd.filter_generator_id(args.generator.upper())
        crit += "\n\tgenerator ID is '%s' [also forces scheme]" % args.generator.upper()

    print(crit)
    print("\nGetting results from Ofgem...\n")
    if osd.get_data():
        print("Query returned {} result{}".format(len(osd), '' if len(osd) == 0 else 's'))

        if args.output is None:
            for s in osd.stations:
                print(s.as_string() + "\n")
        else:
            output_fn = args.output
            if '.' not in output_fn:
                output_fn += '.csv'

            with open(output_fn, 'wt') as csvfile:
                csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow(Station.csv_title_row())
                for s in osd.stations:
                    csv_writer.writerow(s.as_csvrow())
            print("Output saved to file {} [CSV]".format(output_fn))

    else:
        print("No stations were returned")
