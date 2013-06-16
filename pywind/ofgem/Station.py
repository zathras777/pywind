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

from datetime import datetime

class Station(object):

    """ Class to store details of a single station using data from ofgem.

        The exposed object makes the individual pices of data available
        by acting as a dict, i.e.
            name = station['name']

        The convenience function as_string will return a full list of
        the data formatted for display in a terminal.

    """

    FIELDS = [
        'accreditation', 'status', 'name', 'scheme',
        'capacity', 'country', 'technology', 'output',
        'accreditation_dt', 'commission_dt', 'developer',
        'developer_address', 'address', 'fax'
    ]

    def __init__(self, node):

        mapping = [
            ['GeneratorID', 'accreditation'],
            ['StatusName', 'status'],
            ['GeneratorName', 'name'],
            ['SchemeName', 'scheme'],
            ['Capacity'],
            ['Country'],
            ['TechnologyName', 'technology'],
            ['OutputType', 'output'],
            ['AccreditationDate', 'accreditation_dt'],
            ['CommissionDate', 'commission_dt'],
            ['textbox6', 'developer'],
            ['textbox61', 'developer_address'],
            ['textbox65', 'address'],
            ['FaxNumber', 'fax']
        ]
        for m in mapping:
            if len(m) == 1:
                self.set_attr_from_xml(node, m[0], m[0].lower())
            else:
                self.set_attr_from_xml(node, m[0], m[1])

        if self.capacity:
            self.capacity = float(self.capacity)
        self._convert_date('commission_dt')
        self._convert_date('accreditation_dt')
        if self.address is not None:
            self.address = self.address.replace("\r", ", ")
        if self.developer_address is not None:
            self.developer_address = self.developer_address.replace("\r", ", ")
        # catch/correct some odd results I have observed...
        if self.technology is not None and '\n' in self.technology:
            self.technology = self.technology.split('\n')[0]


    def _convert_date(self, which):
        dtstr = getattr(self, which)
        if '\n' in dtstr:
            dtstr = dtstr.split("\n")[0]
        setattr(self, which, datetime.strptime(dtstr, '%d/%m/%Y'))

    def set_attr_from_xml(self, node, attr, name):
        val = node.get(attr, None)
        if val is not None and val.isdigit():
            val = int(val)
        setattr(self, name, val)

    def as_string(self):
        lines = []
        for f in self.FIELDS:
            lines.append("    %-30s: %s" % (f.capitalize().replace('_',' '), getattr(self, f)))
        return "\n".join(lines)
