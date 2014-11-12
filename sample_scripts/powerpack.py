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

""" This script demonstrates how to use the bmreports.PowerPackUnits class to
    get a list of the power pack units.
"""

from pywind.bmreports import PowerPackUnits
pp = PowerPackUnits()
print("%d Power pack units found. Here's the first in the list:" % len(pp))
print(pp.units[0])