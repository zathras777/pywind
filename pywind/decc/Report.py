""" DECC information module """

from __future__ import print_function

import logging
import sys
import csv
from datetime import datetime
if sys.version_info >= (3, 0):
    import codecs
import html5lib

from pywind.utils import get_or_post_a_url
#from .geo import osGridToLatLong, LatLon


def field_to_attr(fld):
    """ Convert the field title into an attribute string. """
    fld = fld.lower()
    for char in [' ', '-', '/']:
        fld = fld.replace(char, '_')
    return fld


class DeccRecord(object):
    """ Simple class to hold details of one DECC station. """
    DATE_FIELDS = ('record_last_updated_(dd_mm_yyyy)',
                   'planning_application_submitted',
                   'planning_application_withdrawn',
                   'planning_permission_refused',
                   'appeal_lodged',
                   'appeal_withdrawn',
                   'appeal_refused',
                   'appeal_granted',
                   'planning_permission_granted',
                   'planning_permission_granted',
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
    FLOAT_FIELDS = ('installed_capacity_(mwelec)',
                    'ro_banding_(roc_mwh)',
                    'fit_tariff_(p_kwh)',
                    'cfd_capacity_(mw)',
                    'turbine_capacity_(mw)',
                    'height_of_turbines_(m)'
                   )
    INT_FIELDS = ('ref_id', 'no._of_turbines')

    def __init__(self, row, fields):
        self.logger = logging.getLogger(__name__)
        if len(row) < len(fields):
            self.logger.warning("Incorrect number of rows for a DECC record." +
                                " Expected %d, got %d", len(fields), len(row))
            return

        for fld in fields:
            attr = field_to_attr(fld)
            val = self._process_value(attr, row.pop(0))
            if fld != '':
                setattr(self, attr, val)

#        latlon = osGridToLatLong(int(self.x_coord), self.y_coord)
#        latlon.convert(LatLon.WGS84)
#        setattr(self, 'lat', latlon.lat)
#        setattr(self, 'lon', latlon.lon)

    def _process_value(self, attr, val):
        """ Take the raw value and which attribute it is for and convert as required. """
        if attr in self.BOOLEAN_FIELDS:
            return False if val.lower() in ['false', 'no'] else True
        if attr in self.DATE_FIELDS:
            if len(val) == 0:
                return None
            try:
                return datetime.strptime(val, "%d/%m/%Y").date()
            except ValueError as err:
                self.logger.info("Invalid date: %s. %s", val, err)
        elif attr in self.INT_FIELDS:
            if len(val) == 0 or val.lower() == 'n/a':
                final_val = None
            else:
                final_val = int(val)
            return final_val
        elif attr in self.FLOAT_FIELDS:
            if len(val) == 0 or val.lower() == 'n/a':
                return None
            val = val.replace(',', '')
            final_val = float(val)
            return final_val
        return val


class MonthlyExtract(object):
    'https://www.gov.uk/government/collections/renewables-statistics'
    BASE_URL = "https://www.gov.uk"
    URL = "https://www.gov.uk/government/publications/renewable-energy-planning-database-monthly-extract"

    def __init__(self):
        self.records = []
        self.available = None
        self.csv_fields = None
        self._find_available()

    def __len__(self):
        return len(self.records)

    def get_data(self):
        """ Get the data from the DECC server and parse it into DECC records. """
        if self.available is None:
            self._find_available()
            if self.available is None:
                raise Exception("Unable to get details of available downloads")

        response = get_or_post_a_url(self.available['url'])

        if sys.version_info >= (3, 0):
            csvfile = csv.reader(codecs.iterdecode(response.content.splitlines(), 'utf-8'))
        else:
            csvfile = csv.reader(response.content.splitlines())

        for row in csvfile:
            if row[3] == '':
                continue
            if 'Ref ID' in row:
                self.csv_fields = row
                continue
            if self.csv_fields is None:
                continue
            decc = DeccRecord(row, self.csv_fields)
            self.records.append(decc)

        return True

    def _find_available(self):
        """ Get the URL and period for the currently available download. """
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
