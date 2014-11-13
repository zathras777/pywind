#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import sys
from pywind.ofgem.CertificateSearch import CertificateSearch


def test(theseargs):
    
    parser = argparse.ArgumentParser(description='Get ofgem certificates for a given month & year')
    parser.add_argument('--month', type=int, default=1, action='store', help='Month')
    parser.add_argument('--year', type=int, default=2012, action='store', help='Year')
    parser.add_argument('--accreditation', action='store', help='Accreditation number to search for')
    parser.add_argument('--scheme', action='store', help='Scheme to search (defaults to RO and REGO)')

    args = parser.parse_args(args=theseargs)

    ocs = CertificateSearch()

    crit = "Searching Ofgem Certificates: "
    crits = []
    if args.month:
        ocs.set_month(args.month)
        crits.append('month %s' % args.month)
    if args.year:
        ocs.set_year(args.year)
        crits.append('year %s' % args.year)
    if args.scheme:
        ocs.set_scheme(args.scheme)
        crits.append('scheme %s' % args.scheme)

    if args.accreditation:
        ocs['accreditation_no'] = args.accreditation.upper()
        crits.append("accreditation number '%s'" % args.accreditation.upper())

    print(crit + ", ".join(crits))
    #ocs.dump_post_data()
    ocs.get_data()
    print("Total of %d records returned. Here are the first two:" % len(ocs))
    for s in ocs.certificates[0:1]:
        print(s.as_string())


if __name__ == '__main__':
    test(sys.argv[1:])