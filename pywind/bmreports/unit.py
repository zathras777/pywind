# coding=utf-8
#
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

from datetime import timedelta, date
from lxml import etree
import urllib

from pywind.bmreports.utils import _geturl, xpath_gettext


class UnitData(object):

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

    def __init__(self, kwargs={}):
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
        self.set_type(kwargs.get('type', 'Derived'))
        self.historic = kwargs.get('historic', True)
        self.latest = kwargs.get('latest', False)

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
            url = 'http://www.bmreports.com/bsp/additional/soapfunctions.php?'
            url += urllib.urlencode(base)
            req = _geturl(url)
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
            series of BMU elements

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

            The original bid values for volume and total bid values for
            cashflow are currently recorded together with the information
            about the station.
        """
        root = etree.parse(req)
        DATA_DICT = {'bid': 'VOLUME//BID_VALUES//ORIGINAL//TOTAL',
                     'cash': 'CASHFLOW//BID_VALUES//TOTAL',
        }
        for bmu in root.xpath(".//ACCEPT_PERIOD_TOTS//*//BMU"):
#            print etree.tostring(bmu)
            bmud = {'id': bmu.get('ID'),
                    'type': bmu.get('TYPE'),
                    'lead': bmu.get('LEAD_PARTY'),
                    'ngc': bmu.get('NGC_NAME'),
                    'volumes': {},
                    'cash': {}}
            for c in ['ORIGINAL', 'TAGGED', 'REPRICED', 'ORIGINALPRICED']:
                val = xpath_gettext(bmu, "VOLUME//BID_VALUES//%s//TOTAL" % c, 0)
                if val != 0:
                    bmud['volumes'][c.lower()] = val
            for c in ['BID', 'OFFER']:
                val = xpath_gettext(bmu, "CASHFLOW//%s_VALUES//TOTAL" % c, 0)
                if val != 0:
                    bmud['cash'][c.lower()] = val

#for k, v in DATA_DICT.iteritems():
#                bmud[k] = xpath_gettext(bmu, v, 0)
            self.data.append(bmud)
        return len(self.data) > 0
