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

""" Module for performing a search of Ofgem Stations.
"""
# pylint: disable=E1101

import copy
from lxml import etree

from pywind.ofgem.form import OfgemForm
from .Station import Station


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
