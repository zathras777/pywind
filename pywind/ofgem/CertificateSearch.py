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

# pylint: disable=E1101

""" Module containing class to perform a search of Certificate records at Ofgem. """

from __future__ import print_function

from lxml import etree

from pywind.ofgem.form import OfgemForm
from .Certificates import CertificatesList


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class CertificateSearch(object):
    """ Getting information about certificates issued by Ofgem requires accessing their webform.
    This class provides a simple way of doing that.
    Class that queries ofgem for certificate data. If it succeeds then

    .. code::

      >>> from pywind.ofgem.CertificateSearch import CertificateSearch
      >>> ocs = CertificateSearch()
      >>> ocs.start()
      True
      >>> ocs.set_period(201601)
      True
      >>> ocs.get_data()
      True
      >>> len(ocs)
      4898

    """

    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/' + \
                'CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    def __init__(self, filename=None):
        self.cert_list = None
        self.has_data = False
        self.form = None

        if filename is not None:
            self.parse_filename(filename)
        else:
            self.form = OfgemForm(self.START_URL)

    def __len__(self):
        return 0 if self.cert_list is None else len(self.cert_list)

    def start(self):
        """ Retrieve the form from Ofgem website so we can start updating it.

        :returns: True or False
        :rtype: boolean
        """
        if self.form is not None:
            return self.form.get()
        return True

    def set_period(self, yearmonth):
        """ Set the year and month for certificates.

        :param yearmonth: Numeric period in YYYYMM format
        :returns: True or False
        :rtype: boolean
        """
        if not isinstance(yearmonth, int):
            yearmonth = int(yearmonth)
        year = yearmonth / 100
        if self._set_year(year) is False:
            return False
        return self._set_month(yearmonth % year)

    def set_start_month(self, month):
        """ Set the start month for certificates

        :param month: Numeric month number
        :returns: True or False
        :rtype: boolean
        """
        return self.form.set_value("output period \"month from\"", MONTHS[month - 1])

    def set_finish_month(self, month):
        """ Set the finish month for certificates

        :param month: Numeric month number
        :returns: True or False
        :rtype: boolean
        """
        return self.form.set_value("output period \"month to\"", MONTHS[month - 1])

    def set_start_year(self, year):
        """ Set the start year for certificates

        :param year: Numeric year to be set
        :returns: True or False
        :rtype: boolean
        """
        return self.form.set_value("output period \"year from\"", str(year))

    def set_finish_year(self, year):
        """ Set the finish year for certificates

        :param year: Numeric year to be set
        :returns: True or False
        :rtype: boolean
        """
        return self.form.set_value("output period \"year to\"", str(year))

    def filter_technology(self, what):
        """ Filter certificates by technology group """
        self.form.set_value('technology group', what)

    def filter_generation_type(self, what):
        """ Filter certificates by generation type """
        self.form.set_value('generation type', what)

    def filter_scheme(self, what):
        """ Filter certificates by scheme

        :param what: Scheme abbreviation [REGO, RO]
        :returns: True or False
        :rtype: boolean
        """
        return self.form.set_value('scheme', what.upper())

    def filter_generator_id(self, acc_no):
        """ Filter certificates by generator id (accreditation number) """
        self.form.set_value('accreditation no', acc_no.upper())

    def get_data(self):
        """ Submit the form, get the results and parse them into :class:`Certificate` objects

        :returns: True or False
        :rtype: boolean
        """
        if not self.form.submit():
            return False
        self.cert_list = CertificatesList(data=self.form.raw_data)
        self.has_data = len(self.cert_list) > 0
        return self.has_data

    def save_original(self, filename):
        """ Save the downloaded certificate data into the filename provided.

        :param filename: Filename to save the file to.
        :returns: True or False
        :rtype: boolean
        """
        return self.form.save_original(filename)

    def rows(self):
        """ Generator function that returns a station each time it is called.

        :returns: A function that returns a dict containing information on one station.
        :rtype: generator
        """
        if self.cert_list is None:
            yield None
        yield self.cert_list.rows()

    def parse_filename(self, filename):
        """Parse an Ofgem generated file of certificates. This parses downloaded Ofgem files.

        :param filename: The filename to be parsed
        :returns: True or False
        :rtype: boolean
        """
        self.cert_list = CertificatesList(filename=filename)
        return len(self.cert_list) > 0

    def stations(self):
        """ Return a list of stations related to the certificates """
        return [] if self.cert_list is None else self.cert_list.stations()

    # Internal functions

    def _set_year(self, year):
        """ Set both the start and finish year for certificates.

        :param year: Numeric year to set
        :returns: True or False
        :rtype: boolean
        """
        if self.set_start_year(year) is False:
            return False
        return self.set_finish_year(year)

    def _set_month(self, month):
        """ Set both the start and finish months for certificates

        :param month: Numeric month number
        :returns: True or False
        :rtype: boolean
        """
        if self.set_start_month(month) is False:
            return False
        return self.set_finish_month(month)

