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

import copy
from lxml import etree

from pywind.ofgem.form import OfgemForm
from pywind.ofgem.lists import CertificatesList
from pywind.ofgem.objects import Station

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
        :rtype: bool
        """
        return self.form.set_value("output period \"year to\"", str(year))

    def filter_technology(self, what):
        """ Filter certificates by technology group """
        return self.form.set_value('technology group', what)

    def filter_generation_type(self, what):
        """ Filter certificates by generation type """
        return self.form.set_value('generation type', what)

    def filter_scheme(self, what):
        """ Filter certificates by scheme

        :param what: Scheme abbreviation [REGO, RO]
        :returns: True or False
        :rtype: bool
        """
        return self.form.set_value('scheme', what.upper())

    def filter_generator_id(self, acc_no):
        """ Filter certificates by generator id (accreditation number).
        .. note::

           Values supplied are upper cased automatically.

        :param acc_no: Accreditation/Generation number
        :returns: True or False
        :rtype: bool
        """
        return self.form.set_value('accreditation no', acc_no.upper())

    def get_data(self):
        """ Submit the form, get the results and parse them into :class:`Certificate` objects

        :returns: True or False
        :rtype: bool
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
        :rtype: bool
        """
        return self.form.save_original(filename)

    def rows(self):
        """ Generator function that returns a station each time it is called.

        :returns: A function that returns a dict containing information on one station.
        :rtype: generator
        """
        return self.cert_list.rows()

    def certificates(self):
        """ Generator that returns :class:`Certificates` objects.

        :returns: Certificates objects
        :rtype: Certificates
        """
        for cert in sorted(self.cert_list.certs, lambda x: x.start_no):
            yield cert

    def parse_filename(self, filename):
        """Parse an Ofgem generated file of certificates. This parses downloaded Ofgem files.

        :param filename: The filename to be parsed
        :returns: True or False
        :rtype: bool
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
        :rtype: bool
        """
        if self.set_start_year(year) is False:
            return False
        return self.set_finish_year(year)

    def _set_month(self, month):
        """ Set both the start and finish months for certificates

        :param month: Numeric month number
        :returns: True or False
        :rtype: bool
        """
        if self.set_start_month(month) is False:
            return False
        return self.set_finish_month(month)


class StationSearch(object):
    """ Performing a station search using the Ofgem website takes a while due to the 3.5M initial file and the
     2M replies that are sent. Parsing these takes time, so patience is needed.

     .. code::

       >>> from pywind.ofgem.StationSearch import StationSearch
       >>> oss = StationSearch()
       >>> oss.start()
       True
       >>> oss.filter_name('griffin')
       True
       >>> oss.get_data()
       True
       >>> len(oss)
       4

    """
    START_URL = 'ReportViewer.aspx?ReportPath=/Renewables/Accreditation/' + \
                'AccreditedStationsExternalPublic&ReportVisibility=1&ReportCategory=1'

    def __init__(self):
        self.form = OfgemForm(self.START_URL)
        self.stations = []

    def __len__(self):
        """ len(...) returns the number of stations available. """
        return len(self.stations)

    def __getitem__(self, item):
        """ Get a station by name. """
        if 0 >= item < len(self.stations):
            return self.stations[item]

    def start(self):
        """ Retrieve the form from Ofgem website so we can start updating it.
        """
        if self.form is not None:
            self.form.get()

    def get_data(self):
        """ Get data from form. """
        if not self.form.submit():
            return False

        doc = etree.fromstring(self.form.raw_data)
        # There are a few stations with multiple generator id's, separated by '\n' so
        # capture them and add each as a separate entry.
        for detail in doc.xpath("//*[local-name()='Detail']"):
            stt = Station(detail)
            if b'\n' in stt.generator_id:
                ids = [x.strip() for x in stt.generator_id.split(b'\n')]
                stt.generator_id = ids[0]
                for _id in ids[1:]:
                    _st = copy.copy(stt)
                    _st.generator_id = _id
                    self.stations.append(_st)
            self.stations.append(stt)
        return len(self.stations) > 0

    def filter_technology(self, what):
        """ Filter stations based on technology. """
        return self.form.set_value("technology", what)

    def filter_scheme(self, scheme):
        """ Filter stations based on scheme they are members of. """
        return self.form.set_value("scheme", scheme.upper())

    def filter_name(self, name):
        """ Filter stations based on name. The search will return all stations containing the supplied name.

        :param name: The name to filter for
        :returns: True or False
        :rtype: bool
        """
        return self.form.set_value("generating station search", name)

    def filter_generator_id(self, accno):
        """ Filter stations based on generator id. """
        return self.form.set_value("accreditation search", accno)

    def filter_organisation(self, org_name):
        """
        Filter stations based on generator id.

        :param org_name: Organisation name to filter
        :returns: True or False
        :rtype: bool
        """
        return self.form.set_value("organisation search", org_name)

    def save_original(self, filename):
        """ Save the downloaded station data into the filename provided.

        :param filename: Filename to save the file to.
        :returns: True or False
        :rtype: boolean
        """
        return self.form.save_original(filename)

    def rows(self):
        """ Generator to return dicts of station information.

         :returns: Dict of station information
         :rtype: dict
        """
        for station in self.stations:
            yield {'Station': station.as_row()}
