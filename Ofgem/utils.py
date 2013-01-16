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

# Utility functions for the Ofgem module.

__author__ = 'david reid'
__version__ = '0.1'

import time
from datetime import datetime

def http_date_time_string(timestamp=None):
    """Return the current date and time formatted for a message header."""
    time_struct = time.gmtime(timestamp if timestamp is not None else time.time())
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_struct)

def ofgem_year(yr):
    ''' Not sure how their indexing is generated, but this works for now!
    '''
    return (yr - 2012) + 1

def get_period(pdstr):
    # We expect to be given a month/year string, which we need to convert
    # into year, month...
    months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct',
              'nov','dec']
    mm = None
    for div in ['-','/']:
        if div in pdstr:
            mm,yy = pdstr.split(div)
            break
    if mm is None: return 0,0

    yy = int(yy)
    if yy < 100: yy += 2000
    if mm.isdigit():
        mm = int(mm)
    else:
        if not mm.lower() in months:
            return 0,0
        mm = months.index(mm.lower()) + 1
    return yy, mm

def parse_csv_line(line):
    pieces = []
    s = ''
    iss = False
    for c in line:
        if c == ',' and not iss:
            pieces.append(s if len(s) else ' ')
            s = ''
            continue
        if c == '\r':
            s += ','
            continue
        if c == '"':
            iss = not(iss)
            continue
        s += c
    if len(s):
        pieces.append(s)
    return pieces
