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

#from datetime import datetime
from django.utils.datetime_safe import datetime
import re


class Certificates(object):
    FIELDS = ['accreditation', 'name','capacity','scheme','country',
              'technology','output','period','certs',
              'start_no','finish_no','factor','issue_dt',
              'status','status_dt','current_holder','reg_no']

    def __init__(self, node):
        """ Extract information from the supplied XML node.
        """

        mapping = [
            ['textbox4', 'accreditation'],
            ['textbox13', 'name'],
            ['textbox5', 'scheme'],
            ['textbox19', 'capacity', 0],
            ['textbox12', 'country'],
            ['textbox15', 'technology'],
            ['textbox31', 'output'],
            ['textbox18', 'period'],
            ['textbox21', 'certs', 0],
            ['textbox24', 'start_no'],
            ['textbox27', 'finish_no'],
            ['textbox37', 'factor', 0],
            ['textbox30', 'issue_dt'],
            ['textbox33', 'status'],
            ['textbox36', 'status_dt'],
            ['textbox39', 'current_holder'],
            ['textbox45', 'reg_no']
        ]

        for m in mapping:
            self.set_attr_from_xml(node, m)

        self.factor = float(self.factor)
        self.certs = int(self.certs) or 0
        self.capacity = float(self.capacity) or 0
        self.issue_dt = datetime.strptime(re.sub(r'T.*', '', self.issue_dt), '%Y-%m-%d')
        self.status_dt = datetime.strptime(re.sub(r'T.*', '', self.status_dt), '%Y-%m-%d')

        if self.period.startswith("01"):
            dt = datetime.strptime(self.period[:10], '%d/%m/%Y')
            self.period = dt.strftime("%b-%Y")

    def set_attr_from_xml(self, node, mapping):
        val = node.get(mapping[0], None)
        if val is not None and val.isdigit():
            val = int(val)
        if val is None and len(mapping) == 3:
            val = mapping[2]
        setattr(self, mapping[1], val)

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), self[f])
        return s

    def as_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    def as_list(self):
        return [getattr(self, f) for f in self.FIELDS]

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self['period'], self['name'], self['certs'],
                                                 self['capacity'], perc)
