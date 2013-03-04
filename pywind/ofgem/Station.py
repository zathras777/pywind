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

from .utils import parse_csv_line

class Station(object):

    """ Class to store details of a single station using data from ofgem.

        The exposed object makes the individual pices of data available
        by acting as a dict, i.e.
            name = station['name']

        The convenience function as_string will return a full list of
        the data formatted for display in a terminal.

    """

    def __init__(self, line):
        self.data = parse_csv_line(line)
        self.is_valid = False

        if len(self.data) >= 13:
            self.data[4] = float(self.data[4])
            # Amazingly enough some date fields have \n embedded in them?!
            if '\n' in self.data[8]:
                self.data[8] = self.data[8].split('\n')[0]
            self.data[8] = datetime.strptime(self.data[8], '%d/%m/%Y')
            self.data[9] = datetime.strptime(self.data[9], '%d/%m/%Y')
            self.is_valid = True

        #  0  - Accreditation No of the station
        #  1  - Status of station
        #  2  - Name of the station
        #  3  - Scheme
        #  4  - Total Installed Generating Capacity
        #  5  - Country
        #  6  - Technology Group
        #  7  - Generation Type
        #  8  - Accreditation Date
        #  9  - Commission Date
        #  10 - Owner
        #  11 - Address
        #  12 - Fax Number
        #  13 - Station address

    FIELDS = ['accreditation', 'status', 'name', 'scheme', 'capacity',
              'country', 'technology', 'generation', 'accreditation_dt',
              'commission_dt', 'developer', 'owner_address', 'fax',
              'address']

    def _get_field(self, fld):
        if fld.lower() in self.FIELDS:
            idx = self.FIELDS.index(fld.lower())
            if idx < len(self.data):
                if type(self.data[idx]) is str:
                    return self.data[idx].strip()
                return self.data[idx]
        return None

    def __getitem__(self, item):
        return self._get_field(item)

    def __getattr__(self, item):
        return self._get_field(item)

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize().replace('_',' '), self[f])
        return s
