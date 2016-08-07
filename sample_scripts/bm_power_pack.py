#!/usr/bin/env python
# coding=utf-8
""" Small script to demonstrate using the bmreports.PowerPackUnits. """

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

from __future__ import print_function

import argparse

from pywind.bmreports import PowerPackUnits

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Balancing Mechanism Unit list')
    args = parser.parse_args()

    row_format = "{:12s} {:10s} {:40s} {:>10s} {:15s} {:8s} {:>10s}"
    ul = PowerPackUnits()
    print("Total of {} units".format(len(ul)))
    print(row_format.format("Sett ID", "NGC ID", "Station Name", "Reg Cap", "Date Added", "BM Unit?", "Capacity"))
    print("{} {} {} {} {} {} {}".format('-'*12, '-'*10, '-'*40, '-'*10, '-'*15, '-'*8, '-'*10))

    for unit in ul.units:
        vals = [
            unit.get('sett_id', 'n/a'),
            unit.get('ngc_id'),
            unit.get('name'),
            str(unit.get('reg_capacity', '')),
            unit.get('date_added'),
            "Yes" if unit.get('bmunit') else "No",
            str(unit.get('cap'))
        ]
        if vals[4] is not None:
            vals[4] = vals[4].strftime("%d %b %Y")
        else:
            vals[4] = 'Unknown'
        print(row_format.format(*vals))
