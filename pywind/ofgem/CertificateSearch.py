# coding=utf-8

#
# Copyright 2013-2015 david reid <zathrasorama@gmail.com>
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
#

import csv
from datetime import datetime
from lxml import etree


try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


from .Base import OfgemForm
from .Certificates import Certificates, CertificatesList


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class CertificateSearch(object):
    """ Class that queries ofgem for certificate data. If it succeeds then
        the returned certificates are available in the .certifcates member.

        The data can be restricted by using the following keywords when
        creating the class instance

          period  - month & year to search
          month   - just the month to search
          year    - just the year to search

        len(object) will return the number of certificates currently available.

    """

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    def __init__(self, filename=None):
        self.cert_list = None
        self.output_fn = None
        if filename is not None:
            self.parse_filename(filename)
        else:
            self.form = OfgemForm(self.START_URL)

    def __len__(self):
        if self.cert_list is None:
            return 0
        return len(self.cert_list)

    def set_month(self, m):
        if type(m) is int:
            m = MONTHS[m - 1]

        self.set_start_month(m)
        self.set_finish_month(m)

    def set_year(self, yr):
        self.set_start_year(yr)
        self.set_finish_year(yr)

    def set_period(self, year, month):
        self.set_year(year)
        self.set_month(month)

    def set_start_month(self, m):
        self.form.set_value("output period \"month from\"", m)

    def set_finish_month(self, m):
        self.form.set_value("output period \"month to\"", m)

    def set_start_year(self, yr):
        self.form.set_value("output period \"year from\"", yr)

    def set_finish_year(self, yr):
        self.form.set_value("output period \"year to\"", yr)

    def filter_technology(self, what):
        self.form.set_value('technology group', what)

    def filter_generation_type(self, what):
        self.form.set_value('generation', what)

    def filter_scheme(self, what):
        self.form.set_value('scheme', what.upper())

    def filter_generator_id(self, acc_no):
        self.form.set_value('accreditation no', acc_no.upper())

    def get_data(self):
        if not self.form.get_data():
            print("Failed to get data.")
            return False

        doc = etree.fromstring(self.form.data)

        if self.output_fn:
            with open(self.output_fn, "w") as fh:
                fh.write("{}".format(etree.tostring(doc, pretty_print=True)))
            print("returned XML saved to '{}'".format(self.output_fn))

        self.cert_list = CertificatesList(data=self.form.data)

    def parse_filename(self, filename):
        self.cert_list = CertificatesList(filename=filename)
        return True

    def stations(self):
        return self.cert_list.stations()

