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

""" This script demonstrates how to use the bmreports.UnitData class to
    get information about Constraint Payments.

    It does not attempt to cater for long or short days and simply assumes
    that there will be 48 settlement periods.
"""
import argparse
from datetime import datetime, timedelta, date
from pywind.bmreports import UnitData

def mkdate(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d').date()

if __name__ == '__main__':
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


