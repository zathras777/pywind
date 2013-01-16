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

__author__ = 'david reid'
__version__ = '0.1'

import re
import urllib
import urllib2
import cookielib
from lxml import html

class OfgemBase(object):
    '''Base object for the classes that actually get data from the
       Ofgem website using their report forms.

       Child classes should define
         fields    - list of fields that are available on the form
         options   - options for the fields
         START_URL - the url of the form they are using
         parse()   - function to parse CSV into appropriate data
    '''

    SITE_URL = 'https://www.renewablesandchp.ofgem.gov.uk'
    BASE_URL = SITE_URL + '/Public/'

    def __init__(self):
        self.rawdata = None
        self.post_url = ''
        self.post_data = {}
        self.is_valid = False
        self.debug = False
        self.cj = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cj)
        httpsHandler = urllib2.HTTPSHandler(debuglevel = 0)
        self.opener = urllib2.build_opener(cookie_handler, httpsHandler)

    def get_data(self):
        self.start_session()
        if not self.is_valid:
            return False
        self.update_post_data()

        if self.debug:
            print "post_data"
            self.dump_post_data()
            print "..."

        pdata = urllib.urlencode(self.post_data)
        resp = self.opener.open(self.post_url, data = pdata)
        if resp.code != 200:
            return False

        return self.parse_response(resp)

    # Private functions below that shouldn't need to be called directly.

    def start_session(self):
        response = self.opener.open(self.BASE_URL + self.START_URL)
        doc = html.parse(response)
        form = doc.findall('.//form')[0]

        self.post_url = self.BASE_URL + urllib.unquote(form.get('action'))
        self.opener.addheaders = [('Referer', self.BASE_URL + self.START_URL),
                                  ('Origin', self.BASE_URL)]

        for el in form.findall('.//input'):
            if el.get('name').startswith('__'):
                self.post_data[el.get('name')] = el.get('value')

        self.is_valid = True

    def parse_response(self, resp):
        '''
           1. Parse the response
           2. Download the actual data we want as a CSV
           3. Parse the CSV data
           4. Return True or False
        '''
        doc = html.parse(resp)

        for s in doc.findall('.//script'):
            if s.text is None:
                continue
            if "RSToolbar(" in s.text:
                ck = re.search("new RSToolbar\((.*)\);", s.text)
                if ck is None:
                    return False

                url = ck.group(1).split(',')[-2].replace('"', '').strip()
                url = self.SITE_URL + url + 'CSV'
                docresp = self.opener.open(url)
                if docresp.code != 200 or docresp.headers['content-type'] != 'text/plain':
                    return False
                self.rawdata = docresp.read()
                if len(self.rawdata) == 0:
                    return False
                self.rawdata = self.rawdata.decode('utf-16').encode('utf-8')
                return self.parse()
        return False

    def update_post_data(self):
        self.post_data['__EVENTTARGET'] = ''
        self.post_data['__EVENTARGUMENT'] = ''
        self.post_data['__LASTFOCUS'] = ''
        self.post_data['ReportViewer$ctl04'] = ''
        self.post_data['ReportViewer$ctl05'] = ''
        self.post_data['ReportViewer$ctl06'] = 0

        for k,v in self.fields.iteritems():
            vals = self.options.get(k, None)
            nm = 'ReportViewer$ctl00$ctl%02d' % k
            typ = v.get('type')
            if typ is None:
                continue

            if typ == 'multi':
                if vals is None:
                    if v.get('all', False):
                        self.post_data[nm + '$ctl03$ctl00'] = 'on'
                    if v.get('null', False):
                        self.post_data[nm + '$ctl01'] = 'on'
                else:
                    for n in vals:
                        self.post_data[nm + '$ctl03$ctl%02d' % n] = 'on'
            elif typ == 'text':
                if vals is None:
                    if v.get('null', False):
                        self.post_data[nm + '$ctl01'] = 'on'
                else:
                    self.post_data[nm + '$ctl00'] = vals
            elif typ == 'select':
                if vals is None:
                    if v.get('all', False):
                        self.post_data[nm + '$ctl00'] = 1
                else:
                    self.post_data[nm + '$ctl00'] = vals
            elif typ == 'bool':
                if vals is None:
                    if v.get('default', False):
                        self.post_data[nm+'$ctl01'] = 'on'
                else:
                    self.post_data[nm + '$ctl01'] = 'on' if vals else 'off'

    def dump_post_data(self):
        for k in sorted(self.post_data.keys()):
            if k.startswith('__'): continue
            print k, ':', self.post_data[k]

