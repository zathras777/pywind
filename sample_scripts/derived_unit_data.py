#!/usr/bin/env python
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
 This script demonstrates how to use the bmreports.UnitData class to
 get information about Constraint Payments.

 It does not attempt to cater for long or short days and simply assumes
 that there will be 48 settlement periods.
"""

import argparse
from datetime import datetime, timedelta, date

from pywind.bmreports.unit import UnitData


def mkdate(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d').date()


def main():
    parser = argparse.ArgumentParser(description='Get Constraint Payment information for yesterday')
    parser.add_argument('--date', action='store', type=mkdate, help='Date to get results for')
    parser.add_argument('--period', action='store', help='Period to get data for')
    args = parser.parse_args()

    data = {}
    ud = UnitData({'date': args.date or date.today() - timedelta(days=2)})
    pr = [args.period] or range(1,49)
    for period in pr:
        ud.period = period
        if ud.get_data():
            data[period] = ud.data
        else:
            print "Unable to get data for %s, period %d" % (ud.date.strftime("%d %b %Y"), period)

    for period, units in sorted(data.iteritems()):
        print "Period: ", period
        for unit in sorted(units, key=lambda x: x['ngc']):
            print "  ", unit['ngc'], unit['lead']
            if unit['bid'].has_key('volume'):
                print "      BID:   ", unit['bid']['volume']+'MWh  ', unit['bid']['cashflow']
            if unit['offer'].has_key('volume'):
                print "      OFFER: ", unit['offer']['volume']+'MWh  ', unit['offer']['cashflow']


if __name__ == '__main__':
    main()