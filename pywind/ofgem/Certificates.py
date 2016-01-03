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

from datetime import datetime
from lxml import etree

from pywind.ofgem.Base import set_attr_from_xml, to_string, as_csv


class Certificates(object):
    """ Certificate Number Fact Sheet
        https://www.ofgem.gov.uk/sites/default/files/docs/roc_identifier_fact_sheet_dec_2015.pdf

    """
    FIELDS = ['generator_id', 'name', 'capacity', 'scheme', 'country',
              'technology', 'output', 'period', 'certs',
              'start_no', 'finish_no', 'factor', 'issue_dt',
              'status', 'status_dt', 'current_holder', 'reg_no']

    def __init__(self, node):
        """ Extract information from the supplied XML node.
            The factor figure is MWh per certificate.
        """
        mapping = [
            ['textbox4', 'generator_id'],
            ['textbox13', 'name'],
            ['textbox5', 'scheme'],
            ['textbox19', 'capacity', 0],
            ['textbox12', 'country'],
            ['textbox15', 'technology'],
            ['textbox31', 'output'],
            ['textbox18', 'period'],
            ['textbox21', 'certs', 0],
            ['textbox24', 'start_no'],
            ['textbox27', 'finish_no'],
            ['textbox37', 'factor', 0],
            ['textbox30', 'issue_dt'],
            ['textbox33', 'status'],
            ['textbox36', 'status_dt'],
            ['textbox39', 'current_holder'],
            ['textbox45', 'reg_no']
        ]

        for m in mapping:
            set_attr_from_xml(self, node, m[0], m[1])

        self.factor = float(self.factor)
        self.certs = int(self.certs) or 0
        self.capacity = float(self.capacity) or 0
        self.issue_dt = datetime.strptime(self.issue_dt.decode(), '%Y-%m-%dT%H:%M:00').date()
        self.status_dt = datetime.strptime(self.status_dt.decode(), '%Y-%m-%dT%H:%M:00').date()

        if self.period.startswith(b"01"):
            dt = datetime.strptime(self.period[:10].decode(), '%d/%m/%Y')
            self.period = dt.strftime("%b-%Y")

    def __str__(self):
        return "        {}  {}  {:5d}  {}".format(self.issue_dt.strftime("%Y %b %d"), self.start_no,
                                                  self.certs, self.current_holder)

    @property
    def digits(self):
        return 10 if self.scheme == 'REGO' else 6

    @property
    def start(self):
        return int(self.start_no[10:10 + self.digits])

    @property
    def finish(self):
        return int(self.finish_no[10:10 + self.digits])

    def generation_type(self):
        return self.start_no[-3:-1]

    def as_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    def as_list(self):
        return [getattr(self, f) for f in self.FIELDS]

    def as_csvrow(self):
        return [as_csv(self, f) for f in self.FIELDS]

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self.period, self.name, self.certs,
                                                 self.capacity, perc)

    def station_details(self):
        S_FIELDS = ['generator_id', 'name', 'scheme', 'capacity', 'country', 'technology', 'output']
        return {fld: getattr(self, fld) for fld in S_FIELDS}
          
    def as_string(self):
        s = ''
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), to_string(self, f))
        return s


def _scheme_from_generator_id(gen_id):
    if gen_id[0] == 'G':
        return 'REGO'
    elif gen_id[0] == 'R':
        return 'RO'
    return None


class CertificateStation(object):
    """ We are normally interested in knowing about certificates issued to
        a station, so this class attempts to simplify this process.
        Once issued all certificates will be accounted for, but the final
        owner and status may change. This class attempts to take a bunch of
        Certificate objects and simplify them into a final set, with ownership
        and status correctly attributed.
    """
    def __init__(self, name, g_id, capacity):
        self.name = name
        self.generator_id = g_id
        self.scheme = _scheme_from_generator_id(g_id)
        self.capacity = capacity      
        self.certs = []
        
    def __len__(self):
        return len(self.certs)

    def __iter__(self):
        for c in self.certs:
            yield c

    def add_cert(self, cert):
        self.certs.append(cert)

    @classmethod
    def csv_title_row(cls):
        titles = []
        for f in Certificates.FIELDS:
            titles.append(" ".join([x.capitalize() for x in f.split(' ')]))
        return titles

    def as_csvrow(self):
        rows = []
        for s in sorted(self.certs):
            rows.extend([c.as_csvrow() for c in self.certs[s]])
        return rows


class CertificatesList(object):
    NSMAP = {'a': 'CertificatesExternalPublicDataWarehouse'}

    def __init__(self, filename=None, data=None):
        self.station_data = {}
        if filename is None and data is None:
            return

        if filename is not None:
            xml = etree.parse(filename)
        elif data is not None:
            xml = etree.fromstring(data)
        else:
            raise Exception("fiename or data MUST be provided.")

        for node in xml.xpath('.//a:Detail', namespaces=self.NSMAP):
            _cert = Certificates(node)
            self.station_data.setdefault(_cert.generator_id,
                                         CertificateStation(_cert.name, _cert.generator_id, _cert.capacity)).add_cert(_cert)

    def __len__(self):
        return len(self.station_data)

    def stations(self):
        for s in sorted(self.station_data.keys()):
            yield self.station_data[s]

