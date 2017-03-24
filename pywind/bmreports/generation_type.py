# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

"""
BMReports make available a number of reports, but this module provides
access to their report on output by generation type for the 3 periods,

 - instant
 - last hour
 - last 24 hours

"""
import os
from datetime import datetime, timedelta

import sys

from pywind.utils import parse_response_as_xml, get_or_post_a_url, _convert_type


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
        self.val = _convert_type(el.get("VAL"), 'int')
        self.pct = _convert_type(el.get("PCT"), 'float')

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
            :param elm: the element to parse
        """
        self.dtt = datetime.strptime(elm.get("AT"), self.DT1)

    def hh(self, elm):
        """ Store the start and finish times for a half hour record.
            :param elm: the element to parse
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
        resp = get_or_post_a_url(self.URL, params=self.PARAMS)
        self.xml = parse_response_as_xml(resp)
        if self.xml is None:
            return

        for section in ['INST', 'HH', 'LAST24H']:
            self.sections.append(GenerationPeriod(self.xml.xpath(section)[0]))

    def save_original(self, filename):
        """ Save the downloaded certificate data into the filename provided.

        :param filename: Filename to save the file to.
        :rtype: bool
        """

        if self.xml is None:
            return False
        name, ext = os.path.splitext(filename)
        if ext is '':
            filename += '.xml'
        self.xml.write(filename)
        return True

    def rows(self):
        """ Return export data as a series of rows.

        :rtype: dict
        """
        for sect in self.sections:
            for rec in self.sections[sect]:
                yield rec

    def as_dict(self):
        """ Return the data as a dict object.
        """
        return {s.keyname(): s.as_dict() for s in self.sections}
