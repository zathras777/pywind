# coding=utf-8
""" Module containing class to perform a search of Certificate records at Ofgem. """
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
# pylint: disable=E1101

from __future__ import print_function

from lxml import etree

from .Base import OfgemForm
from .Certificates import CertificatesList


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

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/' + \
                'CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    def __init__(self, filename=None):
        self.cert_list = None
        self.output_fn = None
        if filename is not None:
            self.parse_filename(filename)
        else:
            self.form = OfgemForm(self.START_URL)

    def __len__(self):
        return 0 if self.cert_list is None else len(self.cert_list)

    def set_month(self, month):
        """ Set month for certificates (start and finish)"""
        if isinstance(month, int) or isinstance(month, long):
            month = MONTHS[month - 1]
        self.set_start_month(month)
        self.set_finish_month(month)

    def set_year(self, year):
        """ Set year for certificates (start and finish) """
        self.set_start_year(year)
        self.set_finish_year(year)

    def set_period(self, year, month):
        """ Set the year and month for certificates. """
        self.set_year(int(year))
        self.set_month(int(month))

    def set_start_month(self, month):
        """ Set the start month for certificates """
        self.form.set_value("output period \"month from\"", month)

    def set_finish_month(self, month):
        """ Set the finish month for certificates """
        self.form.set_value("output period \"month to\"", month)

    def set_start_year(self, year):
        """ Set the start year for certificates """
        self.form.set_value("output period \"year from\"", year)

    def set_finish_year(self, year):
        """ Set the finish year for certificates """
        self.form.set_value("output period \"year to\"", year)

    def filter_technology(self, what):
        """ Filter certificates by technology group """
        self.form.set_value('technology group', what)

    def filter_generation_type(self, what):
        """ Filter certificates by generation type """
        self.form.set_value('generation type', what)

    def filter_scheme(self, what):
        """ Filter certificates by scheme """
        self.form.set_value('scheme', what.upper())

    def filter_generator_id(self, acc_no):
        """ Filter certificates by generator id (accreditation number) """
        self.form.set_value('accreditation no', acc_no.upper())

    def get_data(self):
        """ Get data from the ofgem form """
        if not self.form.get_data():
            return False

        doc = etree.fromstring(self.form.data)

        if self.output_fn:
            with open(self.output_fn, "w") as fhh:
                fhh.write("{}".format(etree.tostring(doc, pretty_print=True)))
            print("returned XML saved to '{}'".format(self.output_fn))

        self.cert_list = CertificatesList(data=self.form.data)

    def parse_filename(self, filename):
        """ Parse a file of certificates. """
        self.cert_list = CertificatesList(filename=filename)
        return True

    def stations(self):
        """ Return a list of stations related to the certificates """
        return [] if self.cert_list is None else self.cert_list.stations()
