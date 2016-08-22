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
One of the most common requests is to search the Ofgem database for certificate issuance.
This script provides an example of using :mod:`pywind` to do this.

.. code::

  $ ofgem_certificate_search --period 201601 --generator R00160SQSC
  Contacting Ofgem and preparing to search.

  Filtering search:
      - generator id  R00160SQSC
      - period should be 201601

  Total of 1 records returned
    Issue Date  Period    Station Name                         Scheme  Status      Certificates
    ----------  --------  -----------------------------------  ------  ----------  ------------
    2016-04-08  Jan-2016  Griffin Wind Farm                    RO      Issued             37491

"""

# Aug 2016
#
# Updated for recent changes in pywind structure.

# Dec 2015 Changes
#
# - year now defaults to current year
# - accreditation changed to generator_id
# - order of filtering updated to avoid conflicts
# - updated output for new object structure
# - verbose flag added to output full output

from __future__ import print_function

import sys

from pywind.log import setup_logging
from pywind.ofgem import CertificateSearch
from pywind.utils import commandline_parser, StdoutFormatter


def main():
    parser = commandline_parser('Get ofgem certificates for a given month & year')
    parser.add_argument('--generator', action='store', help='Generator ID to search for')

    args = parser.parse_args()
    setup_logging(args.debug, request_logging=args.request_debug)

    print("Contacting Ofgem and preparing to search.\n")
    ocs = CertificateSearch()
    ocs.start()
    print("Filtering search:")

    if args.station:
        print("    - cannot filter results based on station name")

    if args.scheme:
        if ocs.filter_scheme(args.scheme):
            print("    - scheme {}".format(args.scheme))
        else:
            print("\nFailed to filter for scheme.")
            sys.exit(0)

    if args.generator:
        if ocs.filter_generator_id(args.generator.upper()):
            print("    - generator id  {}".format(args.generator.upper()))
        else:
            print("\nFailed to filter by generator")
            sys.exit(0)

    if args.period:
        if ocs.set_period(args.period):
            print('    - period should be {}'.format(args.period))
        else:
            print("\nFailed to set period")
            sys.exit(0)

    if ocs.get_data() is False:
        print("No data was returned from the Ofgem server")
        sys.exit(0)

    print("Total of %d records returned" % len(ocs))

    fmt = StdoutFormatter("10s", "8s", "35s", "6s", "10s", "12d")
    print(fmt.titles("Issue Date", "Period", "Station Name", "Scheme", "Status", "Certificates"))
    for cert in ocs.certificates():
        print(fmt.row(cert.issue_dt.strftime("%Y-%m-%d"),
                      cert.period,
                      cert.name,
                      cert.scheme,
                      cert.status,
                      cert.certificates))


if __name__ == '__main__':
    main()
