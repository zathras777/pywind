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

""" BMReports make the system electricity prices available. This module contains
classes to access those reports.
"""

from datetime import date, datetime

from pywind.utils import get_or_post_a_url, parse_response_as_xml


class SystemPrices(object):
    """ Class to get the electricity prices from BMreports. """
    URL = 'http://www.bmreports.com/bsp/additional/soapfunctions.php'

    def __init__(self, dtt=None):
        self.dtt = dtt or date.today()
        self.prices = []

    def get_data(self):
        """ Get the data from the remote server. """
        data = {'element': 'SYSPRICE',
                'dT': self.dtt.strftime("%Y-%m-%d")}
        resp = get_or_post_a_url(self.URL, params=data)
        root = parse_response_as_xml(resp)
        if root is None:
            return False

        for elm in root.xpath('.//ELEMENT'):
            data = {}
            for elm2 in elm.getchildren():
                if elm2.tag == 'SP':
                    data['period'] = int(elm2.text)
                elif elm2.tag == 'SD':
                    data['date'] = datetime.strptime(elm2.text, "%Y-%m-%d")
                else:
                    data[elm2.tag.lower()] = elm2.text
            self.prices.append(data)
        return len(self.prices) > 0

    def as_dict(self):
        """ Return the data as a dict. """
        return {'date': self.dtt, 'data': self.prices}
