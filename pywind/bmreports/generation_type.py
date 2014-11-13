#! /usr/bin/env python
# coding=utf-8

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
#


from datetime import datetime, timedelta

from .utils import parse_response_as_xml
from pywind.ofgem.utils import get_url


class FuelRecord(object):
    FUELS = {'CCGT': 'Combined Cycle Gas Turbine',
             'OCGT': 'Open Cycle Gas Turbine',
             'OIL': 'Oil',
             'COAL': 'Coal',
             'NUCLEAR': 'Nuclear',
             'WIND': 'Wind',
             'PS': 'Pumped Storage',
             'NPSHYD': 'Non Pumped Storage Hydro',
             'OTHER': 'Other',
             'INTFR': 'Import from France',
             'INTIRL': 'Import from Ireland',
             'INTNED': 'Import from the Netherlands',
             'INTEW': 'East/West Interconnector'
    }

    def __init__(self, el):
        """ Object to represent a single fuel record entry. These
            will have the format:
              <FUEL TYPE="OTHER" IC="N" VAL="13528" PCT="1.6"/>
        """
        self.type = el.get("TYPE")
        self.ic = el.get("IC")
        self.val = el.get("VAL")
        self.pct = el.get("PCT")

    def __repr__(self):
        return u"%s" % self.FUELS[self.type]

    def as_dict(self):
        return {'code': self.type, 'name': self.FUELS[self.type],
                'value': self.val, 'percent': self.pct}


class GenerationPeriod(object):
    DT1 = "%Y-%m-%d %H:%M:%S"
    DT2 = "%Y-%m-%d %H:%M"
    NAMES = {'INST': 'instant', 'HH': 'halfhour', 'LAST24H': '24hours'}

    def __init__(self, el):
        self.tag = el.tag
        self.total = int(el.get("TOTAL"))
        if hasattr(self, self.tag):
            getattr(self, self.tag)(el)
        self.data = []
        for f in el.getchildren():
            self.data.append(FuelRecord(f))

    def INST(self, el):
        """ Store the time for an instant record.
            :param el: the element to parse
        """
        self.dt = datetime.strptime(el.get("AT"), self.DT1)

    def HH(self, el):
        """ Store the start and finish times for a half hour record.
            :param el: the element to parse
        """
        dd = el.get("SD")
        hh = el.get("AT")
        self.start = datetime.strptime(dd + ' ' + hh[:5], self.DT2)
        self.finish = datetime.strptime(dd + ' ' + hh[6:], self.DT2)

    def LAST24H(self, el):
        """ Store the start and finish date/time records for a 24 hour record.
            :param el: the element to parse
        """
        dd = el.get("FROM_SD")
        hh = el.get("AT")
        self.start = datetime.strptime(dd + ' ' + hh[:5], self.DT2)
        self.finish = datetime.strptime(dd + ' ' + hh[6:], self.DT2) + timedelta(1)

    def keyname(self):
        return self.NAMES[self.tag]

    def as_dict(self):
        rv = {'total': self.total, 'data': [f.as_dict() for f in self.data]}
        if self.tag == 'INST':
            rv['time'] = self.dt
        else:
            rv['start'] = self.start
            rv['finish'] = self.finish
        return rv


class GenerationData(object):
    URL = "http://www.bmreports.com/bsp/additional/soapfunctions.php"
    PARAMS = {'element': 'generationbyfueltypetable'}

    def __init__(self):
        self.sections = []
        self.xml = None
        self.get_data()

    def get_data(self):
        """ Get data from the BM Reports website. Try 3 times.
        """
        resp = get_url(self.URL, self.PARAMS)
        if resp is None or resp.code != 200:
            return

        self.xml = parse_response_as_xml(resp)
        if self.xml is None:
            return

        for section in ['INST', 'HH', 'LAST24H']:
            self.sections.append(GenerationPeriod(self.xml.xpath(section)[0]))

    def as_dict(self):
        """ Return the data as a dict object.
        """
        return {s.keyname(): s.as_dict() for s in self.sections}
