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


from .Base import Base
from pywind.ofgem.Station import Station
from .utils import parse_csv_line

class StationSearch(Base):
    SCHEMES = {'RO': 1, 'REGO': 2}

    START_URL = 'ReportViewer.aspx?ReportPath=/Renewables/Accreditation/AccreditedStationsExternalPublic&ReportVisibility=1&ReportCategory=1'

    FIELDS = {
        3:  {'name': 'scheme', 'type': 'select'},
        5:  {'name': 'country', 'type': 'multi'},
        7:  {'name': 'commission_year', 'type': 'select', 'all': True},
        9:  {'name': 'accreditation_year', 'type': 'select', 'all': True},
        11: {'name': 'commission_year', 'type': 'select', 'all': True},
        13: {'name': 'accreditation_month', 'type': 'select', 'all': True},
        15: {'name': 'capacity_band', 'type': 'select', 'all': True},
        17: {'name': 'accreditation_status', 'type': 'multi', 'all': True},
        19: {'name': 'contract_type', 'type': 'select', 'all': True},
        21: {'name': 'technology_group', 'type': 'multi', 'all': True},
        23: {'type': 'select', 'all': True},
        25: {'name': 'organisation', 'type': 'text', 'null': True},
        27: {'name': 'generating_station', 'type': 'select', 'all': True},
        29: {'name': 'station', 'type': 'text', 'null': True},
        31: {'name': 'accreditation_no', 'type': 'text', 'null': True},
    }

    def __init__(self, scheme = 'RO'):
        Base.__init__(self)

        self.options = {
            5: [1, 2, 3, 4],
        }
        self.set_scheme(scheme)

    @property
    def stations(self): return self.results

    def parse(self):
        for line in self.rawdata.split("\r\n"):
            if 'textbox' in line:
                continue
            st = Station(line)
            if st.is_valid:
                self.results.append(st)
