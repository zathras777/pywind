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

import argparse
from datetime import datetime
from pywind.ofgem.CertificateSearch import CertificateSearch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get ofgem certificates for a given month & year')
    parser.add_argument('--month', type=int, default=1, action='store', help='Month')
    parser.add_argument('--year', type=int, default=2012, action='store', help='Year')
    parser.add_argument('--accreditation', action='store', help='Accreditation number to search for')
    parser.add_argument('--scheme', action='store', help='Scheme to search (defaults to RO and REGO)')
    parser.add_argument('--filename', action='store', help='Filename to parse')

    args = parser.parse_args()

    if args.filename is None:
        print("Preparing to search.")
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
            ocs.filter_scheme(args.scheme)
            crits.append('scheme %s' % args.scheme)

        if args.accreditation:
            ocs.filter_accreditation(args.accreditation.upper())
            crits.append("accreditation number '%s'" % args.accreditation.upper())

        print("Searching Ofgem Certificates: {}".format(", ".join(crits)))

    #    ocs.output_fn = 'certificates.xml'
        ocs.get_data()
    else:
        ocs = CertificateSearch(filename=args.filename)

    print("Total of %d records returned" % len(ocs))

    for cert in ocs.stations():
        if 'REGO' in cert and len(cert['REGO']) == 1:
            continue
        if 'RO' in cert and len(cert['RO']) == 1:
            continue

#        print(cert)
        print("{:16s}: {}".format(cert['accreditation'], cert['name']))
#        print(cert.as_string())
#        if 'REGO' in cert:
#            print("REGO:")
#            for c in cert['REGO']:
#                print(c.as_string())
#            print("\n")
#        if 'RO' in cert:
#            print("RO:")
#            for c in cert['RO']:
#                print(c.as_string())
#            print("\n")
