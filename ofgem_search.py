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

__author__ = 'david reid'
__version__ = '0.2'

import argparse

from Ofgem.station import OfgemStationData

def do_name_search(name, scheme='REGO'):
    osd = OfgemStationData(scheme)
    osd.options[29] = name.strip()
    if osd.get_data():
        for s in osd.stations:
            print s.as_string()
    else:
        print "No stations matched."

def do_acc_search(scheme, roc):
    osd = OfgemStationData(scheme)
    osd.options[31] = roc.upper().strip()
    if osd.get_data():
        for s in osd.stations:
            print s.as_string()
    else:
        print "No stations matched."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search Ofgem database for matching stations')
    parser.add_argument('--name', action='store', help='Station name to search for')
    parser.add_argument('--accreditation', action='store', help='Accreditation number to search for')
    parser.add_argument('--scheme', action='store', default='REGO',
                        help='Scheme to search (ignored for accreditation) default REGO')
    args = parser.parse_args()

    if args.name:
        do_name_search(args.name, args.scheme)

    if args.accreditation:
        if args.accreditation.startswith('R'):
            do_acc_search('RO', args.accreditation)
        elif args.accreditation.startswith('G'):
            do_acc_search('REGO', args.accreditation)
