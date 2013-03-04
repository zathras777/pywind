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

# Utility functions for the ofgem module.

import time
from datetime import datetime


def http_date_time_string(timestamp=None):
    """ Return the current date and time formatted for a message header. """
    time_struct = time.gmtime(timestamp if timestamp is not None else time.time())
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_struct)


def ofgem_year(yr):
    """ For some odd reason the Ofgem form expects 2012 to be year 1,
        2011 to be year 2 and so on. Quite when the indexing changes
        when the year changes is unclear and despite it now being
        March 2013, 2013 is not an option in the year list.
    """
    if isinstance(yr, basestring):
        yr = int(yr)
    return (2012 - yr) + 1


def get_period(pdstr):
    """ When supplied with a month & year as a string we attempt to
        convert it into a valid numeric year and month to return. Try
        and recognise as many formats as possible.
        If no valid format is found, return 0,0
    """
    dt = None
    formats = ['%b-%Y', '%b %Y', '%b/%Y', '%Y/%b', '%Y-%b', '%Y-%m']
    for f in formats:
        try:
            dt = datetime.strptime(pdstr, f)
        except ValueError:
            pass
    if dt is None:
        return 0,0
    return dt.year, dt.month

def parse_csv_line(line):
    """ Standard CSV parser doesn't parse station lines correctly,
        so use this to get the correct data.
    """
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
