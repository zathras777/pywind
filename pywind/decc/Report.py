import csv
import sys
import requests
from datetime import datetime
from .geo import osGridToLatLong, LatLon

def field_to_attr(fld):
    fld = fld.lower()
    for c in [' ', '-', '/']:
        fld = fld.replace(c, '_')
    return fld

class DeccRecord(object):
    FIELDS = ['Reference',
              'NFFO/SRO/NI-NFFO/Non-NFFO',
              'General Technology',
              'Technology Type',
              'Section 36',
              'Contractor (/Applicant)',
              'Site Name',
              'Installed Capacity (Elec)',
              'CHP',
              'OffShore Wind Round',
              'Address 1',
              'Address 2',
              'Address 3',
              'Address 4',
              'Town',
              'County',
              'District',
              'Region',
              'Country',
              'Wind Turbine Capacity MW',
              'No Wind Turbines',
              'X Coord',
              'Y Coord',
              'Pre-consent',
              'Post-consent',
              'Application Submitted',
              'Application Determined',
              'Construction Date',
              'Application Number',
              'Planning Officer Recommendation',
              'Planning Appeal Status',
              'Appeal Determined',
              'Appeal Ref Number',
              'Date on which generation commenced',
              'Green Belt',
              'National Park',
              'AONB',
              'Heritage Coast',
              'Special Landscape Area',
              'Employment Use',
              'Natural Environment',
              'Other Land Use',
              'Built Heritage/ Archaeology',
              'Project Specific',
              'Relevant Supporting Details',
              'Developer Last Contacted',
              'LPA / CC Last Contacted',
              'LPA Name',
              'Record Last Updated'
    ]

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
        for i in range(len(self.FIELDS)):
            attr = field_to_attr(self.FIELDS[i])
            setattr(self, attr, row[i])

        for f in self.BOOLEAN_FIELDS:
            val = getattr(self, f, None)
            if val is None:
                continue
            setattr(self, f, False if (val.lower() == 'false' or val.lower() == 'no') else True)

        for f in self.DATE_FIELDS:
            try:
                val = getattr(self, f, None)
                setattr(self, f, datetime.strptime(val, "%Y-%m-%d").date())
            except:
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
    URL = "https://restats.decc.gov.uk/app/reporting/decc/monthlyextract/style/csv/csvwhich/reporting.decc.monthlyextract"

    def __init__(self):
        self.opener = requests.session()
        self.records = []

    def __len__(self):
        return len(self.records)

    def get_data(self):
        resp = self.opener.get(self.URL)
        if resp.status_code != 200:
            return False
        stream = resp.content if sys.version_info.major==2 else resp.text
        reader = csv.reader(csv.StringIO(stream))
        for row in reader:
            if row[0] == 'Reference':
                continue
            d = DeccRecord(row)
            self.records.append(d)
        return True
