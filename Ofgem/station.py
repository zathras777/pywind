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

from .base import OfgemBase

class OfgemStationData(OfgemBase):

    START_URL = 'ReportViewer.aspx?ReportPath=/Renewables/Accreditation/AccreditedStationsExternalPublic&ReportVisibility=1&ReportCategory=1'
    SCHEMES = {'RO': 1, 'REGO': 2}

    def __init__(self, scheme = 'RO'):
        OfgemBase.__init__(self)
        self.stations = []
        self.scheme = self.SCHEMES[scheme]

        self.field_names = {
            'scheme': 3,
            'country': 5,
            'commission year': 7,
            'accreditation year': 9,
            'commission month': 11,
            'accreditation year': 13,
            'capacity': 15,
            'accreditation status': 17,
            'contract type': 19,
            'technology group': 21,
            'organisation': 23,
            'organisation search': 25,
            'generating station': 27,
            'station search': 29,
            'accreditation search': 31
        }
        self.fields = {
            3:  {'type': 'select', 'options': self.SCHEMES}, # scheme
            5:  {'type': 'multi'},                # country
            7:  {'type': 'select', 'all': True},  # commission year
            9:  {'type': 'select', 'all': True},  # accreditation year
            11: {'type': 'select', 'all': True},  # commission month
            13: {'type': 'select', 'all': True},  # accreditation month
            15: {'type': 'select', 'all': True},  # capacity
            17: {'type': 'multi', 'all': True},   # accreditation status
            19: {'type': 'select', 'all': True},  # contract type
            21: {'type': 'multi', 'all': True},   # technology group
            23: {'type': 'select', 'all': True},  # organisation
            25: {'type': 'text', 'null': True},   # organisation search
            27: {'type': 'select', 'all': True},  # generating station
            29: {'type': 'text', 'null': True},   # station Search
            31: {'type': 'text', 'null': True},   # accreditation Search
        }
        self.options = {
            3: self.scheme,
            5: [1,2,3,4],
        }

    def parse(self):
        if self.debug:
            print "Raw Data:"
            print self.rawdata
            print "..."

        if self.rawdata is None or len(self.rawdata) == 0:
            return
        for line in self.rawdata.split("\r\n"):
            if 'textbox' in line:
                continue
            st = OfgemStation(line)
            if st.is_valid:
                self.stations.append(st)
        if len(self.stations):
            return True
        return False

class OfgemStation(object):
    ''' Class to store details of a single station using data from Ofgem.

        The exposed object makes the individual pices of data available
        by acting as a dict, i.e.
            name = station['name']

        The convenience function as_string will return a full list of
        the data formatted for display in a terminal.

    '''
    def __init__(self, line):
        self.data = parse_csv_line(line)
        self.is_valid = False

        if len(self.data) >= 13:
            self.data[4] = float(self.data[4])
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

    def __getitem__(self, key):
        if key.lower() in self.FIELDS:
            idx = self.FIELDS.index(key.lower())
            if idx < len(self.data):
                if type(self.data[idx]) is str:
                    return self.data[idx].strip()
                return self.data[idx]
        return None

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), self[f])
        return s
