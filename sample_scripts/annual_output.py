#!/usr/bin/env python
# coding=utf-8

"""
This sample script was written on behalf of Graham and an enquiry he
had for a years worth of output data for Hydro & Biogas stations.

As usual REGO output will be used a proxy for output.

The library appears unable to cope with setting the technology field
directly and so we restrict the options setting to the year, month and
scheme and then simply filter the returned data.
"""

import argparse
import sys
import csv
from datetime import date

from pywind.ofgem import *


def main():
    parser = argparse.ArgumentParser(description='Extract monthly data for supplied year for Hydro or Biogas stations.')
    parser.add_argument('--year',
                        action='store',
                        type=int,
                        default=date.today().year - 1,
                        help='Year to extract data for')
    parser.add_argument('--technology', nargs='*')

    args = parser.parse_args()

    if args.technology is None:
        print "You must specify at least one technology group"
        sys.exit(0)
    print "  Searching year ", args.year, "\n"
    tids = []
    fn = "_".join(args.technology) + "_%d.csv" % args.year
    print fn
    for t in args.technology:
        for poss in CertificateSearch.TECHNOLOGY_LIST:
            if t.lower() in poss.lower():
                tids.append(CertificateSearch.TECHNOLOGY_LIST[poss])
                print "  Filter will match technology ", poss

    cs = CertificateSearch()
    cs.set_start_year(args.year)
    cs.set_finish_year(args.year)
    cs.set_start_month(1)
    cs.set_finish_month(12)
    cs['scheme'] = 1

    print "\n\nSearching for certificates..."
    cs.get_data()
    print "\n Complete.\n\nTotal of %d records to be filtered" % len(cs)
    added = 0

    with open(fn, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([x.capitalize() for x in cs.certificates[0].FIELDS])
        for c in cs.certificates:
            for t in args.technology:
                if t.lower() in c['technology'].lower():
                    spamwriter.writerow(c.as_list())
                    added += 1
    print "Filtering complete. %d records saved as %s" % (added, fn)


if __name__ == '__main__':
    main()
