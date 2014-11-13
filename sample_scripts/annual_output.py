#!/usr/bin/env python
# coding=utf-8

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

# This sample script was written on behalf of Graham and an enquiry he
# had for a years worth of output data for Hydro & Biogas stations.
#
# As usual REGO output will be used a proxy for output.
#
# The library appears unable to cope with setting the technology field
# directly and so we restrict the options setting to the year, month and
# scheme and then simply filter the returned data.

import argparse
import sys
import csv
from datetime import date

from pywind.ofgem import CertificateSearch

TECHNOLOGY_LIST = {
    'Aerothermal': 1,
    'Biodegradable': 2,
    'Biogas': 3,
    'Biomass': 4,
    'Biomass 50kW DNC or less': 5,
    'Biomass using an Advanced Conversion Technology': 6,
    'CHP Energy from Waste': 7,
    'Co-firing of Biomass with Fossil Fuel': 8,
    'Co-firing of Energy Crops': 9,
    'Filled Storage Hydro': 10,
    'Filled Storage System': 11,
    'Fuelled': 12,
    'Geopressure': 13,
    'Geothermal': 14,
    'Hydro': 15,
    'Hydro 20MW DNC or less': 16,
    'Hydro 50kW DNC or less': 17,
    'Hydro greater than 20MW DNC': 18,
    'Hydrothermal': 19,
    'Landfill Gas': 20,
    'Micro Hydro': 21,
    'Ocean Energy': 22,
    'Off-shore Wind': 23,
    'On-shore Wind': 24,
    'Photovoltaic': 25,
    'Photovoltaic 50kW DNC or less': 26,
    'Sewage Gas': 27,
    'Solar and On-shore Wind': 28,
    'Tidal Flow': 29,
    'Tidal Power': 30,
    'Waste using an Advanced Conversion Technology': 31,
    'Wave Power': 32,
    'Wind': 33,
    'Wind 50kW DNC or less': 34
}


def test(theseargs):

    parser = argparse.ArgumentParser(description='Extract monthly data for supplied year for Hydro or Biogas stations.')
    parser.add_argument('--year',
                        action='store',
                        type=int,
                        default=date.today().year - 1,
                        help='Year to extract data for')
    parser.add_argument('--technology', nargs='*')

    args = parser.parse_args(args=theseargs)

    if args.technology is None:
        print("You must specify at least one technology group")
        sys.exit(0)
    print("  Searching year %d \n" % args.year)
    tids = []
    fn = "_".join(args.technology) + "_%d.csv" % args.year
    print(fn)
    for t in args.technology:
        for poss in TECHNOLOGY_LIST:
            if t.lower() in poss.lower():
                tids.append(TECHNOLOGY_LIST[poss])
                print("  Filter will match technology "+ poss)

    cs = CertificateSearch()
    cs.set_start_year(args.year)
    cs.set_finish_year(args.year)
    cs.set_start_month(1)
    cs.set_finish_month(12)
    cs.scheme = 1

    print("\n\nSearching for certificates...")
    cs.get_data()
    print("\n Complete.\n\nTotal of %d records to be filtered" % len(cs))
    added = 0
    if sys.version_info.major > 2:
        csvfile = open(fn, 'w', newline='')
    else:
        csvfile = open(fn, 'wb')
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow([x.capitalize() for x in cs.certificates[0].FIELDS])
    for c in cs.certificates:
        for t in args.technology:
            if t.lower() in c.technology.lower():
                spamwriter.writerow(c.as_list())
                added += 1
    csvfile.close()
    print("Filtering complete. %d records saved as %s" % (added, fn))


if __name__ == '__main__':
    test(sys.argv[1:])