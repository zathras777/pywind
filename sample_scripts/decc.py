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


""" This script demonstrates how to use the decc.MonthlyExtract class to
    get the planning information from DECC
"""

from pywind.decc import MonthlyExtract
me = MonthlyExtract()
me.get_data()
print('%d records found - this is the first one:' % len(me))
me.records[0].dump()