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
#

import csv
from datetime import datetime
from lxml import etree


try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


from .Base import OfgemForm
from .Certificates import Certificates

class CertificateSearch(object):
    """ Class that queries ofgem for certificate data. If it succeeds then
        the returned certificates are available in the .certifcates member.

        The data can be restricted by using the following keywords when
        creating the class instance

          period  - month & year to search
          month   - just the month to search
          year    - just the year to search

        len(object) will return the number of certificates currently available.

        object.certificate_dicts() will return a list of every certificate as a dict.
    """

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    def __init__(self):
        self.form = OfgemForm(self.START_URL)
        self.certificates = []

    def __len__(self):
        return len(self.certificates)

    def set_month(self, m):
        self.set_start_month(m)
        self.set_finish_month(m)

    def set_year(self, yr):
        self.set_start_year(yr)
        self.set_finish_year(yr)

    def set_period(self, year, month):
        self.set_year(year)
        self.set_month(month)

    def set_start_month(self, m):
        self.form.set_value("month from", m)

    def set_finish_month(self, m):
        self.form.set_value("month to", m)

    def set_start_year(self, yr):
        self.form.set_value_by_label("year from", yr)

    def set_finish_year(self, yr):
        self.form.set_value_by_label("year to", yr)

    def filter_technology(self, what):
        self.form.add_filter('technology', what)

    def filter_generation_type(self, what):
        self.form.add_filter('generation', what)

    def filter_scheme(self, what):
        self.form.add_filter('scheme', what.upper())

    def get_data(self):
        if self.form.set_output_type('xml') == False:
            return False

        if self.form.get_data() == False:
            return False

        with open("certificate_search.xml","w") as fh:
            fh.write(self.form.data)

        doc = etree.fromstring(self.form.data)
        for detail in doc.xpath("//*[local-name()='Detail']"):
            self.certificates.append(Certificates(detail))

        return True

    def certificate_dicts(self):
        return [c.as_dict() for c in self.certificates]
