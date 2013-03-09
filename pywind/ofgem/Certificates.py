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

class Certificates(object):
    FIELDS = ['accreditation', 'name','capacity','scheme','country',
              'technology','generation','period','certs',
              'start_no','finish_no','factor','issue_dt',
              'status','status_dt','current_holder','reg_no']

    def __init__(self, line_data):
        """ Given an array which contains a single line from a CSV formatted
            report from the ofgem Renewables website, create an object with
            the relevant information. The fields contained in the line are

              0  - Summary of report
              1  - Period of Generation :
              2  - The period covered by the report
              3  - Total certificates:
              4  - The number of certificates covered by the report
              5  - Accreditation No of the station
              6  - Name of the station
              7  - Total Installed Generating Capacity
              8  - Scheme
              9  - Country
              10 - Technology Group
              11 - Generation Type

              12 - Output Period
              13 - No. of Certificates
              14 - Start Certificate No.
              15 - Finish Certificate No.
              16 - MWh per Certificate
              17 - Issue Date
              18 - Certificate Status
              19 - Status Date
              20 - Current Holder Organisation Name
              21 - Company Registration Number

            The first 5 fields are repeated on every row and are identical,
            so are ignored for the purposes of this object.

            e.g.
              0  - 'All Certificates by Accreditation (REGO, RO)'
              1  - 'Period of Generation :'
              2  - 'Apr 2012 - May 2012'
              3  - 'Total certificates:'
              4  - '1,783,319'
              5  - 'G01542NWSC'
              6  - 'Farr Wind farm ltd - A'
              7  - '92000.00'
              8  - 'REGO'
              9  - 'Scotland'
              10 - 'Wind'
              11 - 'N/A'
              12 - 'Apr-2012'
              13 - '9468'
              14 - 'G01542NWSC0000000000010412300412GEN'
              15 - 'G01542NWSC0000009467010412300412GEN'
              16 - '1.000000000000'
              17 - '31/05/2012'
              18 - 'Issued'
              19 - '31/05/2012'
              20 - 'Beaufort Wind Ltd'
              21 - ''

        """
        if len(line_data) < 20 or 'No rows found' in line_data[5]:
            return
        self.data = line_data[5:]
        # numbers...
        self.data[2] = float(self.data[2])
        self.data[8] = int(self.data[8])
        self.data[11] = float(self.data[11])
        # dates
        self.data[12] = datetime.strptime(self.data[12], '%d/%m/%Y')
        self.data[14] = datetime.strptime(self.data[14], '%d/%m/%Y')
        # Catch odd period values...
        if self.data[7].startswith('01'):
            dt = datetime.strptime(self.data[7][:10], '%d/%m/%Y')
            self.data[7] = dt.strftime("%b-%Y")

    def _get_field(self, fld, exp):
        if fld.lower() in self.FIELDS:
            idx = self.FIELDS.index(fld.lower())
            if self.data is not None and idx < len(self.data):
                if isinstance(self.data[idx], basestring):
                    return self.data[idx].strip()
                return self.data[idx]
        raise exp

    def __getitem__(self, key):
        return self._get_field(key, IndexError)

    def __getattr__(self, item):
        return self._get_field(item, AttributeError)

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), self[f])
        return s

    def as_dict(self):
        return {self.FIELDS[n]: self.data[n] for n in range(0, len(self.FIELDS))}

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self['period'], self['name'], self['certs'],
                                                 self['capacity'], perc)
