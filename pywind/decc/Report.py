import sys
import csv

from datetime import datetime

from .geo import osGridToLatLong, LatLon
from pywind.ofgem.utils import HttpsWithCookies

if sys.version_info >= (3, 0):
    import codecs


RECORD_FIELDS = []


def field_to_attr(fld):
    fld = fld.lower()
    for c in [' ', '-', '/']:
        fld = fld.replace(c, '_')
    return fld


class DeccRecord(object):
    DATE_FIELDS = ['record_last_updated',
                   'application_submitted',
                   'application_determined',
                   'appeal_determined',
                   'construction_date',
                   'date_on_which_generation_commenced',
                   'developer_last_contacted',
                   'lpa_/_cc_last_contacted'
    ]

    BOOLEAN_FIELDS = ['section_36',
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
    ]
    INT_FIELDS = ['x_coord', 'y_coord', 'no_wind_turbines']

    def __init__(self, row):
        if len(row) < len(RECORD_FIELDS):
            return

        for i in range(len(RECORD_FIELDS)):
            attr = field_to_attr(RECORD_FIELDS[i])
            setattr(self, attr, row[i])

        for f in self.BOOLEAN_FIELDS:
            val = getattr(self, f, None)
            if val is None:
                continue
            setattr(self, f, False if (val.lower() == 'false' or val.lower() == 'no') else True)

        for f in self.DATE_FIELDS:
            try:
                val = getattr(self, f)
                setattr(self, f, datetime.strptime(val, "%Y-%m-%d").date())
            except (AttributeError, ValueError):
                setattr(self, f, None)

        for f in self.INT_FIELDS:
            val = getattr(self, f, 0)
            if val == '':
                val = 0
            setattr(self, f, float(val))

        mw_capacity = getattr(self, 'installed_capacity_(elec)', 0)
        mw_capacity = float(mw_capacity.replace(',', ''))
        setattr(self, 'installed_capacity_(elec)', mw_capacity * 1000)
        setattr(self, 'capacity', getattr(self, 'installed_capacity_(elec)'))

        # Convert x,y to lat/lon
        latlon = osGridToLatLong(int(self.x_coord), self.y_coord)
        latlon.convert(LatLon.WGS84)
        setattr(self, 'lat', latlon.lat)
        setattr(self, 'lon', latlon.lon)

    def dump(self):
        for f in self.FIELDS:
            print("%-30s: %s" % (f, getattr(self, field_to_attr(f), '')))


class MonthlyExtract(object):
    'https://www.gov.uk/government/collections/renewables-statistics'
    #https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/434482/Public_Database_-_May_2015.xlsx

    URL = "https://restats.decc.gov.uk/app/reporting/decc/monthlyextract/style/csv/csvwhich/reporting.decc.monthlyextract"

    def __init__(self):
        self.web = HttpsWithCookies()
        self.records = []

    def __len__(self):
        return len(self.records)

    def get_data(self):
        global RECORD_FIELDS
        resp = self.web.open(self.URL)
        if resp is None or resp.code != 200:
            return False

        if sys.version_info >= (3, 0):
            csvfile = csv.reader(codecs.iterdecode(resp, 'utf-8'))
        else:
            csvfile = csv.reader(resp)

        for row in csvfile:
            if row[0] == 'Reference':
                RECORD_FIELDS = row
                continue
            d = DeccRecord(row)
            self.records.append(d)
        return True
