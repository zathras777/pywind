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
Unit data from BM Reports
"""

import os
import xlrd

from datetime import timedelta, date, datetime
from tempfile import NamedTemporaryFile

from pywind.utils import parse_response_as_xml, get_or_post_a_url, _convert_type


def _mkdate(book, sheet, row, col):
    val = sheet.cell(row, col).value
    if val == '':
        return None
    return datetime(*xlrd.xldate_as_tuple(val, book.datemode)).date()


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
        self.type = self.TYPES[kwargs.get('type', 'Derived')]

    def get_data(self):
        """ Get the report data and update.

        :returns: True or False
        :rtype: bool
        """
        self.data = []
        params = {
            'param5': self.date.strftime("%Y-%m-%d"),
            'param6': self.period,
            'element': self.type,
            'param1': self.unitid,
            'param2': self.unittype,
            'param3': self.leadparty,
            'param4': self.ngcunitname,
        }

        if self.historic:
            resp = get_or_post_a_url('http://www.bmreports.com/bsp/additional/soapfunctions.php?',
                                     params=params)
            return self._process(resp)
        return False

    def as_dict(self):
        return {
            'date': self.date.strftime("%y-%m-%d"),
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
        """ Download and update the unit list.

        :returns: True
        :rtype: bool
        """
        self.units = []
        req = get_or_post_a_url(self.XLS_URL)
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
        return True

    def rows(self):
        """ Generator to return row data.

        :returns: Dict of unit data
        :rtype: dict
        """
        for unit in self.units:
            yield {'Unit': {'@{}'.format(key): unit[key] for key in unit.keys()}}

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
            'bmunit': _convert_type(sht.cell(rownum, 5).value, 'bool'),
            'cap': _convert_type(sht.cell(rownum, 6).value, 'float')
        }
        if row_data['ngc_id'] == '':
            return
        self.units.append(row_data)
