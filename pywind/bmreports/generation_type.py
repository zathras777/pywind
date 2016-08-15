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

""" BMReports make available a number of reports, but this module provides
access to their report on output by generation type for the 3 periods,
- instant
- last hour
- last 24 hours

"""

from datetime import datetime, timedelta

from .utils import parse_response_as_xml
from pywind.ofgem.utils import get_url


class GenerationRecord(object):
    """ Class to record details of a single generation type record.
    """
    FUELS = {
        'CCGT': 'Combined Cycle Gas Turbine',
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
        self.icr = el.get("IC")
        self.val = el.get("VAL")
        self.pct = el.get("PCT")

    def __repr__(self):
        return u"%s" % self.FUELS[self.type]

    def as_dict(self):
        """ Return data as a dict. """
        return {'code': self.type,
                'name': self.FUELS[self.type],
                'value': self.val,
                'percent': self.pct,
                'interconnector': self.icr == 'Y'}


class GenerationPeriod(object):
    """ The basic report contains information on 3 different periods. Each will
    be represented by an instance of this class.
    """
    DT1 = "%Y-%m-%d %H:%M:%S"
    DT2 = "%Y-%m-%d %H:%M"
    NAMES = {'INST': 'instant', 'HH': 'halfhour', 'LAST24H': '24hours'}

    def __init__(self, elm):
        self.tag = elm.tag
        self.total = int(elm.get("TOTAL"))
        self.dtt = None
        self.start = None
        self.finish = None
        if hasattr(self, self.tag.lower()):
            getattr(self, self.tag.lower())(elm)
        self.data = []
        for frr in elm.getchildren():
            self.data.append(GenerationRecord(frr))

    def inst(self, elm):
        """ Store the time for an instant record.
            :param el: the element to parse
        """
        self.dtt = datetime.strptime(elm.get("AT"), self.DT1)

    def hh(self, elm):
        """ Store the start and finish times for a half hour record.
            :param el: the element to parse
        """
        ddd = elm.get("SD")
        hhh = elm.get("AT")
        self.start = datetime.strptime(ddd + ' ' + hhh[:5], self.DT2)
        self.finish = datetime.strptime(ddd + ' ' + hhh[6:], self.DT2)

    def last24h(self, elm):
        """ Store the start and finish date/time records for a 24 hour record.
            :param el: the element to parse
        """
        ddd = elm.get("FROM_SD")
        hhh = elm.get("AT")
        self.start = datetime.strptime(ddd + ' ' + hhh[:5], self.DT2)
        self.finish = datetime.strptime(ddd + ' ' + hhh[6:], self.DT2) + timedelta(1)

    def keyname(self):
        """ Return the full name of the tag. """
        return self.NAMES[self.tag]

    def as_dict(self):
        """ Return the data as a dict. """
        drv = {'total': self.total, 'data': [f.as_dict() for f in self.data]}
        if self.tag == 'INST':
            drv['time'] = self.dtt
        else:
            drv['start'] = self.start
            drv['finish'] = self.finish
        return drv


class GenerationData(object):
    """ Class to allow access to the report and parse the response into usable structures.
    """
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
