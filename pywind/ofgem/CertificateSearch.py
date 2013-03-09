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

import csv
from cStringIO import StringIO
from datetime import datetime

from .utils import *
from .Base import Base
from .Certificates import Certificates

class CertificateSearch(Base):
    """ Class that queries ofgem for certificate data. If it succeeds then
        the returned certificates are available in the .certifcates member.

        The data can be restricted by using the following keywords when
        creating the class instance

          period  - month & year to search
          month   - just the month to search
          year    - just the year to search

        len(object) will return the number of certificates currently available.

        object.certificate_dicts() will return a list of every certificate as a dict.
    """

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    SCHEMES = {'REGO': 1, 'RO': 2}

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

    FIELDS = {
        3:  {'name': 'scheme', 'type': 'multi', 'all': True},
        5:  {'name': 'technology', 'type': 'multi', 'all': True},
        7:  {'name': 'ro_order', 'type': 'multi', 'all': True},
        9:  {'name': 'generation', 'type': 'multi', 'all': True},
        11: {'name': 'country', 'type': 'multi', 'all': True},
        13: {'name': 'agent_station', 'type': 'select', 'default': 1 },
        15: {'name': 'all_generators', 'type': 'bool', 'default': True},
        17: {'name': 'station', 'type': 'text', 'null': True},
        19: {'name': 'start_year', 'type': 'select', 'default': 0},
        21: {'name': 'finish_year', 'type': 'select', 'default': 0},
        23: {'name': 'start_month', 'type': 'select', 'default': 0},
        25: {'name': 'finish_month', 'type': 'select', 'default': 0},
        27: {'name': 'output_type', 'type': 'multi', 'all': True},
        29: {'name': 'accreditation', 'type': 'text', 'null': True},
        31: {'name': 'status', 'type': 'multi', 'all': True},
        33: {'name': 'certificate_no', 'type': 'text', 'null': True},
        35: {'name': 'all_organisations', 'type': 'bool', 'default': True},
        37: {'name': 'current_holder_name', 'type': 'text', 'null': True}
    }

    def __init__(self):
        Base.__init__(self)
        # Default options only restrict the countries to England, Scotland, Wales
        # and Northern Ireland.
        self.options = {
            11: [3,4,5,7],
        }

    def set_month(self, m):
        self.options[23] = m
        self.options[25] = m

    def set_start_month(self, m):
        self.options[23] = m

    def set_finish_month(self, m):
        self.options[25] = m

    def set_year(self, yr):
        self.options[19] = ofgem_year(yr)
        self.options[21] = ofgem_year(yr)

    def set_start_year(self, yr):
        self.options[19] = ofgem_year(yr)

    def set_finish_year(self, yr):
        self.options[21] = ofgem_year(yr)

    def set_period(self, period):
        year, month = get_period(period)
        self.set_month(month)
        self.set_year(year)

    def set_start_period(self, period):
        year, month = get_period(period)
        self.options[19] = year
        self.options[23] = month

    def set_finish_period(self, period):
        year, month = get_period(period)
        self.options[21] = year
        self.options[25] = month

    def parse(self):
        csvfile = StringIO(self.rawdata)
        linereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in linereader:
            if 'textbox' in row[0]: continue
            c = Certificates(row)
            if hasattr(c, 'data'):
                self.results.append(c)

    @property
    def certificates(self): return self.results

    def certificate_dicts(self):
        return [c.as_dict() for c in self.results]
