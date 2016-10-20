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
The DECC publish monthly extracts of planning applications for renewable projects.
This module aims to make accessing this report simpler.

https://www.gov.uk/government/publications/renewable-energy-planning-database-monthly-extract
"""

from __future__ import print_function

import logging
import sys
import csv
from datetime import datetime
from pprint import pprint

if sys.version_info >= (3, 0):
    import codecs
import html5lib

from pywind.utils import get_or_post_a_url, _convert_type
from .geo import Coord


class DeccRecord(object):
    """
    Simple class to hold details of one DECC station.

    """
    DATE_FIELDS = ('record_last_updated_dd_mm_yyyy',
                   'planning_application_submitted',
                   'planning_application_withdrawn',
                   'planning_permission_refused',
                   'appeal_lodged',
                   'appeal_withdrawn',
                   'appeal_refused',
                   'appeal_granted',
                   'planning_permission_granted',
                   'planning_permission_granted',
                   'record_last_updated_dd_mm_yyyy',
                   'secretary_of_state___intervened',
                   'secretary_of_state___refusal',
                   'secretary_of_state___granted',
                   'planning_permission_expired',
                   'under_construction',
                   'operational',
                  )
    BOOLEAN_FIELDS = ('chp_enabled',
                      'green_belt',
                      'national_park',
                      'aonb',
                      'heritage_coast',
                      'special_landscape_area',
                      'employment_use',
                      'natural_environment',
                      'other_land_use',
                      'built_heritage__archaeology',
                      'project_specific',
                      'chp'
                     )
    FLOAT_FIELDS = ('installed_capacity_mwelec',
                    'ro_banding_roc_mwh',
                    'fit_tariff_p_kwh',
                    'cfd_capacity_mw',
                    'turbine_capacity_mw',
                    'height_of_turbines_m'
                   )
    INT_FIELDS = ('ref_id',
                  'no._of_turbines',
                  'x-coordinate',
                  'y-coordinate')

    def __init__(self, app_info):
        self.logger = logging.getLogger(__name__)
        self.attrs = {}
        for key in app_info.keys():
            val = app_info[key]
            key = key.replace('(', '').replace(')', '').replace('/', '_')
            if val in ['', '#REF!']:
                val = None
            else:
                if key in self.INT_FIELDS + self.FLOAT_FIELDS and val.lower() == 'n/a':
                    val = '0'
                if key in self.DATE_FIELDS:
                    val = _convert_type(val, 'date')
                elif key in self.INT_FIELDS:
                    val = _convert_type(val, 'int')
                elif key in self.FLOAT_FIELDS:
                    val = _convert_type(val, 'float')
                elif key in self.BOOLEAN_FIELDS:
                    val = _convert_type(val, 'bool')
                else:
                    if sys.version_info < (3, 0):
                        val = val.decode('latin1').encode('utf-8')

            self.attrs[key] = val

        if self.attrs.get('x-coordinate') is not None and self.attrs.get('y-coordinate') is not None:
            coord = Coord(self.attrs['x-coordinate'], self.attrs['y-coordinate'])
            self.attrs['lat'], self.attrs['lon'] = coord.as_wgs84()

    def __getattr__(self, item):
        if item in self.attrs:
            return self.attrs[item]
        raise AttributeError(item)

    def __contains__(self, item):
        return item in self.attrs

    def fit_rate_mwh(self):
        """ Convert the FIT Tariff rate into GBP per MWh.

        :rtype: float
        """
        fit = self.attrs.get('fit_tariff_(p_kwh)', 0)
        if fit in [0.0, None]:
            return 0.0
        return fit * 10


class MonthlyExtract(object):
    """
    The MonthlyExtract class allows the current monthly data to be easily retrieved and parsed.

    .. note::

     The CSV data returned does not declare an encoding, so latin1 is presently assumed.

    """
    BASE_URL = "https://www.gov.uk"
    URL = "https://www.gov.uk/government/publications/renewable-energy-planning-database-monthly-extract"

    def __init__(self, filename=None):
        self.records = []
        self.raw_data = None
        self.available = None
        self.csv_fields = {}
        self.filename = filename
        if filename is None:
            self._find_available()

    def __len__(self):
        """
        Return the number of DECC records that have been extracted. Will be 0 until get_data() has been called.
        """
        return len(self.records)

    def __getitem__(self, item):
        return self.records[item]

    def get_data(self):
        """ Get the data from the DECC server and parse it into DECC records.

        :returns: True or False
        :rtype: bool
        """
        if self.filename is not None:
            return self._parse_filename()

        if self.available is None:
            self._find_available()
            if self.available is None:
                raise Exception("Unable to get details of available downloads")

        response = get_or_post_a_url(self.available['url'])
        self.raw_data = response.content

        if sys.version_info >= (3, 0):
            csvfile = csv.reader(codecs.iterdecode(response.content.splitlines(), 'latin1'))
        else:
            csvfile = csv.reader(response.content.splitlines())

        for row in csvfile:
            self._parse_row(row)
        self.records = sorted(self.records, key=lambda rec: rec.site_name)
        return True

    def rows(self):
        """ Generator that returns records

        :returns: Dict of planning application information
        :rtype: dict
        """
        for app in self.records:
            yield {'PlanningApplication': {'@{}'.format(key): getattr(app, key)
                                           for key in self.csv_fields}}

    def save_original(self, filename):
        """ Save the downloaded certificate data into the filename provided.

        :param filename: Filename to save the file to.
        :returns: True or False
        :rtype: bool
        """
        if self.raw_data is None:
            return False
        with open(filename, 'wb') as ofh:
            ofh.write(self.raw_data)
        return True

    # Private functions
    def _find_available(self):
        """
        Get the URL and period for the currently available download.
        """
        response = get_or_post_a_url(self.URL)
        document = html5lib.parse(response.content,
                                  treebuilder="lxml",
                                  namespaceHTMLElements=False)
        titles = document.xpath('.//h2[@class="title"]')
        period = None
        for tit in titles:
            if len(tit.getchildren()) == 0:
                period = tit.text.split(':')[1].strip()
        links = document.xpath('.//span[@class="download"]/a')
        self.available = {'period': period,
                          'url': self.BASE_URL + links[0].get('href')}

    def _parse_filename(self):
        with open(self.filename, 'rb') as ofh:
            if sys.version_info >= (3, 0):
                csvfile = csv.reader(codecs.iterdecode(ofh, 'latin1'))
            else:
                csvfile = csv.reader(ofh)

            for row in csvfile:
                self._parse_row(row)

        self.available = {'period': 'Unknown'}
        self.records = sorted(self.records, key=lambda rec: rec.site_name)
        return True

    def _parse_row(self, row):
        # There tend to be blank entries...so remove them....
        if self.csv_fields is None and 'Ref ID' not in row:
            return
        if 'Ref ID' in row:
            for colnum in range(len(row)):
                if row[colnum] == '':
                    continue
                self.csv_fields[row[colnum].lower().replace(' ', '_')] = colnum
            return
        app_info = {}
        for key in self.csv_fields.keys():
            app_info[key] = row[self.csv_fields[key]]
        if len(app_info) == 0:
            return
        decc = DeccRecord(app_info)
        try:
            chk = decc.site_name
            if chk is None:
                return
        except AttributeError:
            return
        self.records.append(decc)
