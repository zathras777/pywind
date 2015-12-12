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

import sys
import time
from datetime import datetime

try:
    from urllib import urlencode
    from urllib2 import HTTPCookieProcessor, HTTPSHandler, build_opener, urlopen, URLError
    from cookielib import CookieJar
except ImportError:
    from urllib.request import HTTPCookieProcessor, HTTPSHandler, build_opener, urlopen, URLError
    from urllib.parse import urlencode
    from http.cookiejar import CookieJar


def http_date_time_string(timestamp=None):
    """ Return the current date and time formatted for a message header. """
    time_struct = time.gmtime(timestamp if timestamp is not None else time.time())
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_struct)


def tidy_string(s):
    """ Remove some unicode characters that can cause trouble. """
    s = s.replace(u'\u2013', "-")
    return s


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


def viewitems(obj, **kwargs):
    """ Provide support for iterating over a dict in both
        Python 2 and 3.
        Code from the future module.
    """
    func = getattr(obj, "viewitems", None)
    if not func:
        func = obj.items
    return func(**kwargs)


class HttpsWithCookies(object):
    def __init__(self):
        self.cookieJar = CookieJar()
        cookie_handler = HTTPCookieProcessor(self.cookieJar)
        httpsHandler = HTTPSHandler(debuglevel=5)
        self.opener = build_opener(cookie_handler, httpsHandler)

    def open(self, url, data=None):
        try:
            return self.opener.open(url, data)
        except URLError:
            return None

def get_url(url, data=None):
    """ Perform a simple GET request, optionally using the supplied data.
        Returns None if unable to get the url after 3 attempts, or an object
        encapsulating the opened url.
    """
    req_url = url
    if data:
        if not url.endswith('?'):
            req_url += '?'
        req_url += urlencode(data)
    for attempt in range(0, 3):
        try:
            return urlopen(req_url)
        except:
            e = sys.exc_info()[0]
            print("Failed {0} of 3, retrying...".format(attempt))
            print(e)
    return None
