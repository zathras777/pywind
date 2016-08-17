# coding=utf-8
""" Module for performing a search of Ofgem Stations.
"""
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

import copy
from lxml import etree

from pywind.ofgem.form import OfgemForm
from .Station import Station


class StationSearch(object):
    """ Class that allows easy searching of Ofgem stations and manages results. """
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
        return True

    def filter_technology(self, what):
        """ Filter stations based on technology. """
        return self.form.set_value("technology", what)

    def filter_scheme(self, scheme):
        """ Filter stations based on scheme they are members of. """
        return self.form.set_value("scheme", scheme.upper())

    def filter_name(self, name):
        """ Filter stations based on name. """
        return self.form.set_value("generating station search", name)

    def filter_generator_id(self, accno):
        """ Filter stations based on generator id. """
        return self.form.set_value("accreditation search", accno)
