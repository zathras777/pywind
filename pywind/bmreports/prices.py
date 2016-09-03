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

""" BMReports make the system electricity prices available. This module contains
classes to access those reports.
"""
import os
from datetime import date, datetime

from pywind.utils import get_or_post_a_url, parse_response_as_xml


class SystemPrices(object):
    """ Class to get the electricity prices from BMreports. """
    URL = 'http://www.bmreports.com/bsp/additional/soapfunctions.php'

    def __init__(self, dtt=None):
        self.dtt = dtt or date.today()
        self.xml = None
        self.prices = []

    def get_data(self):
        """ Get the data from the remote server. """
        data = {'element': 'SYSPRICE',
                'dT': self.dtt.strftime("%Y-%m-%d")}
        resp = get_or_post_a_url(self.URL, params=data)
        self.xml = parse_response_as_xml(resp)
        if self.xml is None:
            return False

        for elm in self.xml.xpath('.//ELEMENT'):
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

    def rows(self):
        """Generator to return rows for export.

        :returns: Dict containing information for a single price period.
        :rtype: dict
        """
        for per in self.prices:
            yield {'PricePeriod': {'@{}'.format(key):per[key] for key in per}}

    def save_original(self, filename):
        """ Save the downloaded certificate data into the filename provided.

        :param filename: Filename to save the file to.
        :returns: True or False
        :rtype: bool
        """

        if self.xml is None:
            return False
        name, ext = os.path.splitext(filename)
        if ext is '':
            filename += '.xml'
        self.xml.write(filename)
        return True

    def as_dict(self):
        """ Return the data as a dict. """
        return {'date': self.dtt, 'data': self.prices}
