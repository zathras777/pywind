# coding=utf-8
#
# Copyright 2013-2015 david reid <zathrasorama@gmail.com>
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

import sys
from datetime import datetime
from pywind.ofgem.Base import set_attr_from_xml


def fix_address(addr):
    if sys.version_info < (3, 0):
        return addr.replace("\r", ", ")
    return addr.decode().replace("\r", ", ").encode('utf-8')


class Station(object):

    """ Class to store details of a single station using data from ofgem.

        The exposed object makes the individual pieces of data available
        by acting as a dict, i.e.
            name = station['name']

        The convenience function as_string will return a full list of
        the data formatted for display in a terminal.

    """

    FIELDS = [
        'generator_id', 'status', 'name', 'scheme',
        'capacity', 'country', 'technology', 'output',
        'accreditation_dt', 'commission_dt', 'developer',
        'developer_address', 'address', 'fax'
    ]
    mapping = [
        ['GeneratorID', 'generator_id'],
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

    def __init__(self, node):
        for m in self.mapping:
            if len(m) == 1:
                set_attr_from_xml(self, node, m[0], m[0].lower())
            else:
                set_attr_from_xml(self, node, m[0], m[1])

        # Now tidy up and ajust a few formats...
        if self.capacity is not None:
            self.capacity = float(self.capacity)
        self._convert_date('commission_dt')
        self._convert_date('accreditation_dt')
        if self.address is not None:
            self.address = fix_address(self.address)
        if self.developer_address is not None:
            self.developer_address = fix_address(self.developer_address)

        # catch/correct some odd results I have observed...
        if self.technology is not None and b'\n' in self.technology:
            self.technology = self.technology.split(b'\n')[0]

    def as_string(self):
        """ Mainly used for command line tools... """
        lines = []
        for f in self.FIELDS:
            lines.append("    {:>30s}: {}".format(f.capitalize().replace('_', ' '), self._string(f)))
        return "\n".join(lines)

    @classmethod
    def csv_title_row(cls):
        titles = []
        for m in cls.mapping:
            _t = (m[0] if len(m) == 1 else m[1]).replace('_', ' ')
            titles.append(" ".join([x.capitalize() for x in _t.split(' ')]))
        return titles

    def as_csvrow(self):
        return [self._csv(f) for f in self.FIELDS]

    ###
    ### Private functions below
    ###
    def _convert_date(self, which):
        dtstr = getattr(self, which)
        if b'\n' in dtstr:
            dtstr = dtstr.split(b"\n")[0]
        setattr(self, which, datetime.strptime(dtstr.decode(), '%d/%m/%Y').date())

    def _string(self, attr):
        """ This is long winded, but allows for as_string() to work for both Python 2 & 3 """
        val = getattr(self, attr)
        if val is None:
            return ''
        if type(val) is str:
            return val
        elif type(val) is int:
            return str(val)
        elif type(val) is float:
            return "{:.02f}".format(val)
        elif hasattr(val, 'strftime'):
            return val.strftime("%Y-%m-%d")
        return val.decode()

    def _csv(self, f):
        """ Return the given field as a value suitable for inclusion in a CSV file for Python 2 or 3 """
        val = getattr(self, f)
        if sys.version_info >= (3, 0) and type(val) is bytes:
            return val.decode()
        return val

    def _csv_title(self, m):
        _t = m[0] if len(m) == 1 else m[1]
        return _t.capitalize().replace('_', ' ')
