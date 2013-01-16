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

import csv
from cStringIO import StringIO
from datetime import datetime

from .utils import *
from .base import OfgemBase

class OfgemCertificateData(OfgemBase):
    ''' Class that queries Ofgem for certificate data. If it succeeds then
        the returned certificates are available in the .certifcates member.

        The data can be restricted by using the following keywords when
        creating the class instance

          period  - month & year to search
          month   - just the month to search
          year    - just the year to search

        len(object) will return the number of certificates currently available.

        object.certificate_dicts() will return a list of every certificate as a dict.
    '''

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    SCHEME_LIST = {'REGO': 1, 'RO': 2}

    COUNTRY_LIST = {'Austria': 1,
                    'Denmark': 2,
                    'England': 3,
                    'Northern Ireland': 4,
                    'Scotland': 5,
                    'Switzerland': 6,
                    'Wales': 7
    }
    TECHNOLOGY_LIST = {
        'Aerothermal': 1,
        'Biodegradable': 2,
        'Biogas': 3,
        'Biomass': 4,
        'Biomass 50kW DNC or less': 5,
        'Biomass using an Advanced Conversion Technology': 6,
        'CHP Energy from Waste': 7,
        'Co-firing of Biomass with Fossil Fuel': 8,
        'Co-firing of Energy Crops': 9,
        'Filled Storage Hydro': 10,
        'Filled Storage System': 11,
        'Fuelled': 12,
        'Geopressure': 13,
        'Geothermal': 14,
        'Hydro': 15,
        'Hydro 20MW DNC or less': 16,
        'Hydro 50kW DNC or less': 17,
        'Hydro greater than 20MW DNC': 18,
        'Hydrothermal': 19,
        'Landfill Gas': 20,
        'Micro Hydro': 21,
        'Ocean Energy': 22,
        'Off-shore Wind': 23,
        'On-shore Wind': 24,
        'Photovoltaic': 25,
        'Photovoltaic 50kW DNC or less': 26,
        'Sewage Gas': 27,
        'Solar and On-shore Wind': 28,
        'Tidal Flow': 29,
        'Tidal Power': 30,
        'Waste using an Advanced Conversion Technology': 31,
        'Wave Power': 32,
        'Wind': 33,
        'Wind 50kW DNC or less': 34
    }
    GENERATOR_LIST = {
        'Dedicated energy crops': 1,
        'Dedicated biomass with CHP': 2,
        'Advanced gasification': 3,
        'Dedicated energy crops with CHP': 4,
        'Co-firing of energy crops': 5,
        'N/A': 5,
        'Dedicated biomass': 6,
        'Standard gasification': 7,
        'Electricity generated from sewage gas': 8,
        'Biomass using an Advanced Conversion Technology': 9,
        'Biomass (e.g. Plant or animal matter)': 10,
        'Unspecified':11,
        'Co-firing of biomass with fossil fuel': 12,
        'AD': 13,
        'Waste using an Advanced Conversion Technology': 14,
        'Co-firing of biomass': 15
    }
    RO_ORDER_LIST = {'N/A': 1, 'NIRO': 2, 'RO': 3, 'ROS': 4},
    AGENT_LIST = {'Generating Stations and Agent Groups': 1,
                  'Agent Groups': 2,
                  'Generating Stations':3}
    OUTPUT_LIST = {'General': 1, 'NFFO': 2, 'AMO': 3}
    STATUS_LIST = {'Issued': 1,
                   'Revoked': 2,
                   'Retired': 3,
                   'Redeemed': 4,
                   'Expired': 5}

    field_names = {
        'scheme': 3,
        'technology group': 5,
        'ro order': 7,
        'generation type': 9,
        'country': 11,
        'show agent groups': 13,
        'show all generators': 15,
        'generating station': 17,
        'start year': 19,
        'finish year': 21,
        'start month': 23,
        'finish month': 25,
        'output type': 27,
        'accreditation number': 29,
        'certificate status': 31,
        'certificate number': 33,
        'show all organisations': 35,
        'current holder organisation name': 37
    }

    fields = {
        3:  {'type': 'multi', 'all': True, 'options': SCHEME_LIST}, # scheme
        5:  {'type': 'multi', 'all': True},   # technology groups
        7:  {'type': 'multi', 'all': True},   # RO Order
        9:  {'type': 'multi'},                # generation type
        11: {'type': 'multi'},                # countries
        13: {'type': 'select', },             # agents/stations
        15: {'type': 'bool', 'default': True},  #
        17: {'type': 'multi', 'null': True},  # generating station
        19: {'type': 'select'},               # start year
        21: {'type': 'select'},               # finish year
        23: {'type': 'select'},               # start month
        25: {'type': 'select'},               # finish month
        27: {'type': 'multi', 'all': True},   # output type
        29: {'type': 'text', 'null': True},   # accreditation search
        31: {'type': 'multi', 'all': True},   # certificate status
        33: {'type': 'text', 'null': True},   # certificate search
        35: {'type': 'bool', 'default': True},
        37: {'type': 'text', 'null': True}
    }

    def __init__(self, **kwargs):
        OfgemBase.__init__(self)

        year = month = 0

        if kwargs.has_key('period'):
            year, month = get_period(kwargs['period'])
        else:
            year = kwargs.get('year', datetime.today().year)
            month = kwargs.get('month', datetime.today().month)

        self.options = {
            5:  [23,24,33,34],  # technology groups
            9:  [6],            # generation type
            11: [3,4,5,7],      # countries
            13: 3,            # agents/stations
            19: ofgem_year(year),
            21: ofgem_year(year),
            23: month,
            25: month,
        }
        self.certificates = []

    def __len__(self): return len(self.certificates)

    def set_start_period(self, period):
        year, month = get_period(period)
        self.options[19] = year
        self.options[23] = month

    def set_finish_period(self, period):
        year, month = get_period(period)
        self.options[21] = year
        self.options[25] = month

    def parse(self):
        if len(self.rawdata) == 0:
            return False
        csvfile = StringIO(self.rawdata)
        linereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in linereader:
            if 'textbox' in row[0]: continue
            c = CertificateSummary(row)
            if hasattr(c, 'data'):
                self.certificates.append(c)
        if len(self.certificates) == 0:
            return False
        return True

    def certificate_dicts(self):
        return [c.as_dict() for c in self.certs]

class CertificateSummary(object):
    FIELDS = [
        'accreditation', 'name','capacity','scheme','country',
        'technology','generation','period','certs',
        'start_no','finish_no','factor','issue_dt',
        'status','status_dt','current_holder','reg_no' ]

    def __init__(self, line_data):
        ''' Given an array which contains a single line from a CSV formatted
            report from the Ofgem Renewables website, create an object with
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

        '''
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

    def __getitem__(self, key):
        if key.lower() in self.FIELDS:
            idx = self.FIELDS.index(key.lower())
            if idx < len(self.data):
                if type(self.data[idx]) is str:
                    return self.data[idx].strip()
                return self.data[idx]
        return None

    FIELDS = ['accreditation', 'name','capacity',
              'scheme', 'country', 'technology',
              'generation', 'period', 'no_certs',
              'first_cert', 'last_cert', 'factor',
              'issue_date', 'status', 'status_date',
              'holder']

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), self[f])
        return s

    def as_dict(self):
        return {self.FIELDS[n]: self.data[n] for n in range(0, len(self.FIELDS))}
#        return {'accreditation': self.data[0],
#                'name': self.data[1],
#                'capacity': self.data[2],
#                'scheme': self.data[3],
#                'country': self.data[4],
#                'technology': self.data[5],
#                'generation': self.data[6],
#                'period': self.data[7],
#                'no_certs': self.data[8],
#                'first_cert': self.data[9],
#                'last_cert': self.data[10],
#                'factor': self.data[11],
#                'issue_date': self.data[12],
#                'status': self.data[13],
#                'status_date': self.data[14],
#                'holder': self.data[15]
#        }

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self['period'], self['name'], self['certs'],
                                                 self['capacity'], perc)

