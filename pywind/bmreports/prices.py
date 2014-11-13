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

from datetime import date

from pywind.ofgem.utils import get_url
from .utils import xpath_gettext, parse_response_as_xml


class SystemPrices(object):
    URL = 'http://www.bmreports.com/bsp/additional/soapfunctions.php'

    def __init__(self, dt=None):
        self.dt = dt or date.today()
        self.prices = []

    def get_data(self):
        data = {'element': 'SYSPRICE', 'dT': self.dt.strftime("%Y-%m-%d")}
        req = get_url(self.URL, data)
        if req is None or req.code != 200:
            print("Unable to get data...")
            return False
        return self._process(req)

    def _process(self, req):
        """ The XML data returned from the request should contain a series of
            ELEMENT elements

            <ELEMENT>
              <SD>2013-04-09</SD>
              <SP>1</SP>
              <SSP>48.90000</SSP>
              <SBP>67.57225</SBP>
              <BD>F</BD>
              <PDC>A</PDC>
              <NIV>353.6212</NIV>
              <SPPA>0.00</SPPA>
              <BPPA>0.00</BPPA>
              <OV>881.007</OV>
              <BV>-528.289</BV>
              <TOV>527.385</TOV>
              <TBV>-528.289</TBV>
              <ASV>0.000</ASV>
              <ABV>0.000</ABV>
              <TASV>0.000</TASV>
              <TABV>0.000</TABV>
            </ELEMENT>

            Currently only the SSP and SBP subelements are recorded.

            :param: req: The request object to process.
        """
        root = parse_response_as_xml(req)
        if root is None:
            return False

        for e in root.xpath('.//ELEMENT'):
            data = {'period': xpath_gettext(e, './/SP', 99),
                    'sbp': xpath_gettext(e, './/SBP', 0),
                    'ssp': xpath_gettext(e, './/SSP', 0),
            }
            self.prices.append(data)
        return len(self.prices) > 0
