# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from .Base import OfgemForm
from .Station import Station
from lxml import etree


class StationSearch(object):

    START_URL = 'ReportViewer.aspx?ReportPath=/Renewables/Accreditation/AccreditedStationsExternalPublic&ReportVisibility=1&ReportCategory=1'

    def __init__(self):
        self.form = OfgemForm(self.START_URL)
        self.stations = []

    def __len__(self):
        return len(self.stations)

    def get_data(self):
        self.form.set_output_type('xml')

        if self.form.get_data():
            with open("station_search.xml", "wb") as fh: fh.write(self.form.data)

            data_str = self.form.data.decode('utf-8').replace("&#0xD;", ", ")
            doc = etree.fromstring(data_str)
            for detail in doc.xpath("//*[local-name()='Detail']"):
                self.stations.append(Station(detail))

            return True
        return False

    def filter_technology(self, what):
        return self.form.add_filter("technology", what)

    def filter_scheme(self, scheme):
        return self.form.add_filter("scheme", scheme.upper())

    def filter_name(self, name):
        return self.form.set_text_value("Generating Station Search", name)

    def filter_accreditation(self, accno):
        return self.form.set_text_value("Accreditation Search", accno)
