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
from pywind.bmreports import UnitData

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Constraint Payment information for yesterday')
    args = parser.parse_args()

    data = {}
    ud = UnitData()
    for period in range(1, 49):
        ud.period = period
        if ud.get_data():
            data[period] = ud.data

    for period, bids in sorted(data.iteritems()):
        print "Period: ", period
        for bid in sorted(bids, key=lambda x: x['ngc']):
            print "    ", bid['ngc'], bid['lead'], ' (', UnitData.CX_TYPE[bid['type']], ')'
            print "        Volume: ", ', '.join(["%s: %s" % (k, v) for k, v in bid['volumes'].iteritems()])
            print "        Cash:   ", ', '.join(["%s: %s" % (k, v) for k, v in bid['cash'].iteritems()])


