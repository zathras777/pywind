# coding=utf-8
"""
Unit data from BM Reports
"""
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
import requests
import xlrd

from datetime import timedelta, date, datetime
from tempfile import NamedTemporaryFile

from pywind.ofgem.utils import get_url
from pywind.utils import parse_response_as_xml


def _mkdate(book, sheet, row, col):
    val = sheet.cell(row, col).value
    if val == '':
        return None
    return datetime(*xlrd.xldate_as_tuple(val, book.datemode)).date()


def _yesno(val):
    """ Convert yes/no into True/False """
    return val.lower() in ['yes', 'true']


def _walk_nodes(elm):
    data = {}

    for elm2 in elm.getchildren():
        data[elm2.tag.lower()] = _walk_nodes(elm2)
    if elm.text is not None:
        data['value'] = elm.text
    return data


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
        self.data = []
        self.date = kwargs.get('date', date.today() - timedelta(days=1))
        self.period = kwargs.get('period', 1)
        self.unitid = kwargs.get('unitid', '')
        self.unittype = kwargs.get('unittype', '')
        self.leadparty = kwargs.get('leadparty', '')
        self.ngcunitname = kwargs.get('ngcunitname', '')
        self.historic = kwargs.get('historic', True)
        self.latest = kwargs.get('latest', False)

        self.set_type(kwargs.get('type', 'Derived'))

    def set_type(self, typ):
        """ Will throw an error if an invalid type is used... """
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

        for bmu in root.xpath(".//ACCEPT_PERIOD_TOTS//*//BMU"):
            bmud = {
                'id': bmu.get('ID'),
                'type': bmu.get('TYPE'),
                'lead': bmu.get('LEAD_PARTY'),
                'ngc': bmu.get('NGC_NAME'),
                }
            bmud['cashflow'] = _walk_nodes(bmu.xpath('.//CASHFLOW')[0])
            bmud['volume'] = _walk_nodes(bmu.xpath('.//VOLUME')[0])
            self.data.append(bmud)
        return len(self.data) > 0


class BaseUnitClass(object):
    """ Base class """
    XLS_URL = ""
    SHEET_NAME = ""

    def __init__(self):
        self.units = []
        self.get_list()

    def __len__(self):
        return len(self.units)

    def get_list(self):
        self.units = []
        req = requests.get(self.XLS_URL)
        if req.status_code != 200:
            return
        tmp_f = NamedTemporaryFile(delete=False)
        with open(tmp_f.name, 'w') as fhh:
            fhh.write(req.content)

        wbb = xlrd.open_workbook(tmp_f.name)
        sht = wbb.sheet_by_name(self.SHEET_NAME)

        for rownum in range(1, sht.nrows):
            self._extract_row_data(wbb, sht, rownum)

        try:
            os.unlink(tmp_f.name)
        except Exception:
            pass

    def _extract_row_data(self, wbb, sht, rownum):
        raise NotImplementedError


class UnitList(BaseUnitClass):
    """ Get a list of the Balancing Mechanism Units with their
        Fuel Type and dates.
    """
    XLS_URL = "http://www.bmreports.com/bsp/staticdata/BMUFuelType.xls"
    SHEET_NAME = "BMU Fuel Types"

    def by_fuel_type(self, fuel):
        units = []
        for unit in self.units:
            if unit['fuel_type'].lower() == fuel.lower():
                units.append(unit)
        return units

    def _extract_row_data(self, wbb, sht, rownum):
        row_data = {
            'ngc_id': sht.cell(rownum, 0).value,
            'sett_id': sht.cell(rownum, 1).value,
            'fuel_type': sht.cell(rownum, 2).value,
            'eff_from': _mkdate(wbb, sht, rownum,3),
            'eff_to': _mkdate(wbb, sht, rownum, 4)
        }
        if row_data['sett_id'] == 42:
            del(row_data['sett_id'])
        self.units.append(row_data)


class PowerPackUnits(BaseUnitClass):
    """ Download the latest Power Pack modules spreadsheet and make the
        list of stations available as a list.
    """
    XLS_URL = 'http://www.bmreports.com/bsp/staticdata/PowerParkModules.xls'
    SHEET_NAME = "Sheet1"

    def _extract_row_data(self, wbb, sht, rownum):
        row_data = {
            'sett_id': sht.cell(rownum, 0).value,
            'ngc_id': sht.cell(rownum, 1).value,
            'name': sht.cell(rownum, 2).value,
            'reg_capacity': sht.cell(rownum, 3).value,
            'date_added': _mkdate(wbb, sht, rownum, 4),
            'bmunit': _yesno(sht.cell(rownum, 5).value),
            'cap': sht.cell(rownum, 6).value
        }
        if row_data['ngc_id'] == '':
            return
        self.units.append(row_data)
