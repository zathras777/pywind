#!/usr/bin/env python
# coding=utf-8

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

import argparse

from pywind.ofgem import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search ofgem database for matching stations')
    parser.add_argument('--name', action='store', help='Station name to search for')
    parser.add_argument('--accreditation', action='store', help='Accreditation number to search for')
    parser.add_argument('--scheme', action='store', default='REGO',
                        help='Scheme to search (ignored for accreditation) default REGO')
    parser.add_argument('--organisation', action='store', help='Organisation to search for')

    args = parser.parse_args()

    print("Preparing search...")
    osd = StationSearch()

    crit = "Searching for Ofgem Stations: scheme %s" % args.scheme

#    osd.filter_scheme(args.scheme)

    if args.name:
        osd.filter_name(args.name)
        crit += ", name = '%s'" % args.name

    if args.organisation:
        osd['organisation'] = args.organisation
        crit += ", organisation = '%s'" % args.organisation

    if args.accreditation:
        if args.accreditation.upper()[0] == 'R':
            osd.filter_scheme('RO')
        elif args.accreditation.upper()[0] == 'G':
            osd.filter_scheme('REGO')
        osd.filter_accreditation(args.accreditation.upper())
        crit += ", accreditation number = '%s'" % args.accreditation.upper()

    print crit
    if osd.get_data():
        print "Query returned %d results" % len(osd)
        for s in osd.stations:
            print s.as_string() + "\n"
    else:
        print "No stations were returned"
