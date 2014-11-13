# coding=utf-8

#
# Copyright 2013, 2014 david reid <zathrasorama@gmail.com>
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

import os
import xlrd

from datetime import timedelta, date, datetime
from tempfile import NamedTemporaryFile

from .utils import xpath_gettext, parse_response_as_xml
from pywind.ofgem.utils import get_url


def _mkdate(book, sheet, row, col):
    val = sheet.cell(row, col).value
    if val == '':
        return None
    return datetime(*xlrd.xldate_as_tuple(val, book.datemode)).date()


class UnitData(object):
    """ Class that gets data about Balancing Mechanism Units
        from the Balancing Mechanism website.
    """
    HOST = 'http://www.bmreports.com'
    TYPES = {'Physical': '/servlet/com.logica.neta.bwp_PanBMDataServlet',
             'Dynamic': '/servlet/com.logica.neta.bwp_PanDynamicServlet',
             'Bid-Offer': '/servlet/com.logica.neta.bwp_PanBodServlet',
             'Derived': 'DerivedBMUnit',
             'BSV': '/servlet/com.logica.neta.bwp_PanBsvServlet'
    }
    CX_TYPE = {'T': 'Directly Connected to Transmission System',
               'E': 'Embedded in Distribution System',
               'I': 'Interconnector User',
               'G': 'Supplier (base)',
               'S': 'Supplier (additional)',
               'M': 'Other'
    }
    DURATION = {'S': 'Short', 'L': 'Long'}

    def __init__(self, *args, **kwargs):
        """ Create an instance of a UnitData class. By default the
            UnitData will query for settlement period 1 yesterday for
            Derived Data.
        """
        #print(kwargs)
        self.data = []
        self.date = kwargs.get('date', date.today() - timedelta(days=1))
        #print(self.date)
        self.period = kwargs.get('period', 1)
        self.unitid = kwargs.get('unitid', '')
        self.unittype = kwargs.get('unittype', '')
        self.leadparty = kwargs.get('leadparty', '')
        self.ngcunitname = kwargs.get('ngcunitname', '')
        self.historic = kwargs.get('historic', True)
        self.latest = kwargs.get('latest', False)

        self.set_type(kwargs.get('type', 'Derived'))

    def set_type(self, typ):
        ''' Will throw an error if an invalid type is used... '''
        self.type = self.TYPES[typ]

    def as_params(self):
        return {'param5': self.date.strftime("%Y-%m-%d"),
                'param6': self.period,
                'element': self.type,
                'param1': self.unitid,
                'param2': self.unittype,
                'param3': self.leadparty,
                'param4': self.ngcunitname,
        }

    def get_data(self):
        base = self.as_params()
        self.data = []

        if self.historic:
            req = get_url('http://www.bmreports.com/bsp/additional/soapfunctions.php?', base)
            if req is None or req.code != 200:
                return False
            return self._process(req)
        return False

    def as_dict(self):
        return {'date': self.date.strftime("%y-%m-%d"),
                'period': self.period,
                'data': self.data
        }

    def _process(self, req):
        """ Process the XML returned from the request. This will contain a
            series of BMU elements, e.g.

            <BMU ID="T_WBUPS-4"
                 TYPE="T"
                 LEAD_PARTY="West Burton Limited"
                 NGC_NAME="WBUPS-4">
              <VOLUME>
                <BID_VALUES>
                  <ORIGINAL>
                    <M1>-6.0833</M1>
                    <TOTAL>-6.0833</TOTAL>
                  </ORIGINAL>
                  <TAGGED>
                    <M1>-6.0833</M1>
                    <TOTAL>-6.0833</TOTAL>
                  </TAGGED>
                  <REPRICED/>
                  <ORIGINALPRICED/>
                </BID_VALUES>
                <OFFER_VALUES>
                  <ORIGINAL/>
                  <TAGGED/>
                  <REPRICED/>
                  <ORIGINALPRICED/>
                </OFFER_VALUES>
              </VOLUME>
              <CASHFLOW>
                <BID_VALUES>
                  <M1>-203.3800</M1>
                  <TOTAL>-203.3800</TOTAL>
                </BID_VALUES>
                <OFFER_VALUES/>
              </CASHFLOW>
            </BMU>

            Each units record shows the details of Bids & Offers made
            during the settlement period. The actual accepted volumes
            should be shown in the ORIGINAL elements.
            Units can have both Bid & Offer results in the same Settlement Period.
        """
        root = parse_response_as_xml(req)
        if root is None:
            return False

        ELEMENTS = [
            ['VOLUME//BID_VALUES//ORIGINAL//TOTAL', 'bid', 'volume'],
            ['VOLUME//OFFER_VALUES//ORIGINAL//TOTAL', 'offer', 'volume'],
            ['CASHFLOW//BID_VALUES//TOTAL', 'bid', 'cashflow'],
            ['CASHFLOW//OFFER_VALUES//TOTAL', 'offer', 'cashflow']
        ]

        for bmu in root.xpath(".//ACCEPT_PERIOD_TOTS//*//BMU"):
            bmud = {'id': bmu.get('ID'),
                    'type': bmu.get('TYPE'),
                    'lead': bmu.get('LEAD_PARTY'),
                    'ngc': bmu.get('NGC_NAME'),
                    'bid': {},
                    'offer': {}
            }
            for el in ELEMENTS:
                val = xpath_gettext(bmu, el[0], 0)
                if val != 0:
                    bmud[el[1]][el[2]] = val
            if not 'volume' in bmud['bid'] and not 'volume' in bmud['offer']:
                continue
            self.data.append(bmud)
        return len(self.data) > 0


class UnitList(object):
    """ Get a list of the Balancing Mechanism Units with their
        Fuel Type and dates.
    """
    XLS_URL='http://www.bmreports.com/bsp/staticdata/BMUFuelType.xls'

    def __init__(self):
        self.get_list()

    def __len__(self):
        return len(self.units)

    def _mkdate(self, book, sheet, row, col):
        val = sheet.cell(row, col).value
        return datetime(*xlrd.xldate_as_tuple(val, book.datemode)).date()

    def by_fuel_type(self, fuel):
        units = []
        for unit in self.units:
            if unit['fuel_type'].lower() == fuel.lower():
                units.append(unit)
        return units

    def get_list(self):
        self.units = []
        req = get_url(self.XLS_URL)
        f = NamedTemporaryFile(delete=False)
        with open(f.name, 'w') as fh:
            fh.write(req.read())

        wb = xlrd.open_workbook(f.name)
        sh = wb.sheet_by_name(u'BMU Fuel Types')

        for rownum in range(1, sh.nrows):
            ud = {'ngc_id': sh.cell(rownum, 0).value,
                  'sett_id': sh.cell(rownum, 1).value,
                  'fuel_type': sh.cell(rownum, 2).value,
                  'eff_from': _mkdate(wb, sh, rownum,3),
                  'eff_to': _mkdate(wb, sh, rownum, 4)
            }
            if ud['sett_id'] == 42:
                del(ud['sett_id'])

            self.units.append(ud)
        try:
            os.unlink(f.name)
        except:
            pass


class PowerPackUnits(object):
    """ Download the latest Power Pack modules spreadsheet and make the
        list of stations available as a list.
    """
    XLS_URL='http://www.bmreports.com/bsp/staticdata/PowerParkModules.xls'
    def __init__(self):
        self.get_list()

    def __len__(self):
        return len(self.units)

    def yesno(self, val):
        if val.lower() in ['yes','true']:
            return True
        return False

    def get_list(self):
        self.units = []
        req = get_url(self.XLS_URL)
        f = NamedTemporaryFile(delete=False)
        with open(f.name, 'w') as fh:
            fh.write(req.read())

        wb = xlrd.open_workbook(f.name)
        sh = wb.sheet_by_name(u'Sheet1')

        for rownum in range(1, sh.nrows):
            ud = {
                'sett_id': sh.cell(rownum, 0).value,
                'ngc_id': sh.cell(rownum, 1).value,
                'name': sh.cell(rownum, 2).value,
                'reg_capacity': sh.cell(rownum, 3).value,
                'date_added': _mkdate(wb, sh, rownum, 4),
                'bmunit': self.yesno(sh.cell(rownum, 5).value),
                'cap': sh.cell(rownum, 6).value
            }
            if ud['ngc_id'] == '':
                break
            self.units.append(ud)

        try:
            os.unlink(f.name)
        except:
            pass

