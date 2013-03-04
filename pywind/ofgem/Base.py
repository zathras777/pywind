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
__version__ = '0.2'

import re
import urllib
import urllib2
import cookielib
from lxml import html

class BaseError(Exception):
    pass

class Base(object):
    ''' Base object for the classes that actually get data from the
        ofgem website using their report forms.

        Child classes should define
          FIELDS    - list of fields that are available on the form
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
        self.results = []
        self.is_valid = False
        self.debug = False
        self.cj = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cj)
        httpsHandler = urllib2.HTTPSHandler(debuglevel = 0)
        self.opener = urllib2.build_opener(cookie_handler, httpsHandler)

    def set_scheme(self, scheme):
        SCHEMES = {'RO': 1, 'REGO': 2}
        try:
            self['scheme'] = SCHEMES[scheme.upper()]
        except KeyError:
            raise BaseError("Invalid scheme specified - %s" % scheme.upper())

    def get_data(self):
        self._start_session()
        if not self.is_valid:
            return False
        self._update_post_data()

        if self.debug:
            self.dump_post_data()

        pdata = urllib.urlencode(self.post_data)
        resp = self.opener.open(self.post_url, data = pdata)
        if resp.code != 200:
            return False

        return self._parse_response(resp)

    def dump_post_data(self):
        if not self.post_data:
            self._update_post_data()
        for k in sorted(self.post_data.keys()):
            if k.startswith('__'): continue
            print k, ':', self.post_data[k]

    def _start_session(self):
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

    def _parse_response(self, resp):
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
                if self.rawdata is None or len(self.rawdata) == 0:
                    self.results = []
                    return False
                if self.debug:
                    print self.rawdata
                self.parse()
                if len(self.results):
                    return True
                return False
        return False

    def _update_post_data(self):
        ''' Each child class is expected to provide a dict giving details
            of the fields that are required for form submission. The dict
            gives the type of field and defaults.
            The child class should also have an options dict that provides
            values to be used for the fields when making a request.
        '''
        self.post_data['__EVENTTARGET'] = ''
        self.post_data['__EVENTARGUMENT'] = ''
        self.post_data['__LASTFOCUS'] = ''
        self.post_data['ReportViewer$ctl04'] = ''
        self.post_data['ReportViewer$ctl05'] = ''
        self.post_data['ReportViewer$ctl06'] = 0

        for k,v in self.FIELDS.iteritems():
            options = self.options.get(k, None)
            nm = 'ReportViewer$ctl00$ctl%02d' % k
            typ = v.get('type')
            fld_name = v.get('name', 'Field %d' % k)
            if typ is None:
                raise BaseError("No type sepcified for %s" % fld_name)

            if typ == 'multi':
                # multiple choice select field
                if options is None:
                    if v.get('all', False):
                        options = [0]
                    if v.get('null', False):
                        self.post_data[nm + '$ctl01'] = 'on'
                if options is not None:
                    if not hasattr(options, '__getitem__'):
                        options = [options]
                    for n in options:
                        self.post_data[nm + '$ctl03$ctl%02d' % n] = 'on'
            elif typ == 'text':
                # simple text field
                if options is None:
                    if v.get('null', False):
                        self.post_data[nm + '$ctl01'] = 'on'
                else:
                    self.post_data[nm + '$ctl00'] = options
            elif typ == 'select':
                # select field with only one options allowed
                if options is None:
                    if v.get('all', False):
                        options = 1
                    elif v.has_key('default'):
                        options = v.get('default')
                self.post_data[nm + '$ctl00'] = options
            elif typ == 'bool':
                if options is None:
                    options = v.get('default', False)
                self.post_data[nm + '$ctl01'] = 'on' if options else 'off'
            elif typ == 'radio':
                key = nm + "$ReportViewer_ctl00_ctl%02d" % k
                if options is None:
                    options = v.get('default', True)
                self.post_data[key] = "ctl00" if options else "ctl01"

    def _get_field(self, fld):
        for n,f in self.FIELDS.iteritems():
            if f.get('name', None) == fld.lower().replace(' ','_'):
                return self.options[n]
        return None

    def _set_field(self, fld, value):
        for n,f in self.FIELDS.iteritems():
            if f.get('name', None) == fld.lower().replace(' ','_'):
                self.options[n] = value
                return True
        return False

    def __getitem__(self, item):
        return self._get_field(item)

    def __getattr__(self, item):
        return self._get_field(item)

    def __setitem__(self, key, value):
        if not self._set_field(key, value):
            super(Base, self).__setitem__(key, value)

    def __setattr__(self, key, value):
        if not self._set_field(key, value):
            super(Base, self).__setattr__(key, value)

    def __len__(self): return len(self.results)
