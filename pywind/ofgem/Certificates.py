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

from pywind.utils import map_xml_to_dict


class Certificates(object):
    """ Certificate Number Fact Sheet
        https://www.ofgem.gov.uk/sites/default/files/docs/roc_identifier_fact_sheet_dec_2015.pdf

    """
    XML_MAPPING = (
            ('textbox4', 'generator_id'),
            ('textbox13', 'name'),
            ('textbox5', 'scheme'),
            ('textbox19', 'capacity', 'float', 0),
            ('textbox12', 'country'),
            ('textbox15', 'technology'),
            ('textbox31', 'generation_type'),
            ('textbox18', 'period'),
            ('textbox21', 'certs', 'int', 0),
            ('textbox24', 'start_no'),
            ('textbox27', 'finish_no'),
            ('textbox37', 'factor', 'float', 0),
            ('textbox30', 'issue_dt', 'date'),
            ('textbox33', 'status'),
            ('textbox36', 'status_dt', 'date'),
            ('textbox39', 'current_holder'),
            ('textbox45', 'reg_no')
        )

    def __init__(self, node):
        """ Extract information from the supplied XML node.
            The factor figure is MWh per certificate.
        """
        self.attrs = map_xml_to_dict(node, self.XML_MAPPING)

        if self.attrs['period'].startswith(b"01"):
            dt = datetime.strptime(self.attrs['period'][:10].decode(), '%d/%m/%Y')
            self.attrs['period'] = dt.strftime("%b-%Y")

    def __str__(self):
        return "        {}  {}  {:5d}  {}".format(self.issue_dt.strftime("%Y %b %d"), self.start_no,
                                                  self.certs, self.current_holder)

    def __getattr__(self, item):
        if item in self.attrs:
            return self.attrs[item]

    @property
    def digits(self):
        return 10 if self.scheme == 'REGO' else 6

    @property
    def start(self):
        """ Return the numeric start number for the certificates.
        Each certificate number contains the station, period and the number of the certificate,
        so this function extracts the numeric part.

        :returns: Start number of the certificates referenced
        :rtype: integer
        """
        return int(self.start_no[10:10 + self.digits])

    @property
    def finish(self):
        """ Return the numeric finish number for the certificates.
        Each certificate number contains the station, period and the number of the certificate,
        so this function extracts the numeric part.

        :returns: Finish number of the certificates referenced
        :rtype: integer
        """
        return int(self.finish_no[10:10 + self.digits])

    def as_dict(self):
        return self.attrs

    def as_list(self):
        return [getattr(self, f) for f in self.FIELDS]

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self.period, self.name, self.certs,
                                                 self.capacity, perc)

    def station_details(self):
        """ Get a dict object with the station information for these certificates.

        :returns: Dict with just information relevant to identifying the station
        :rtype: dict
        """
        S_FIELDS = ['generator_id', 'name', 'scheme', 'capacity', 'country', 'technology', 'output']
        return {fld: self.attrs[fld] for fld in S_FIELDS}

    @property
    def output(self):
        """ Calculate the output based on the number of certs issued and factor.

        :returns: Numeric output or 0
        :rtype: float
        """
        return self.certs / self.factor

    def append_xml_node(self, parent_node):
        """ Create an XML node and append it to the parent node,
        which is assumed to be a station node for this function.

        .. :note::

        This is not Python 3 compatible :-(

        :param parent_node: XML parent node
        :returns: None
        """
        node = etree.Element('CertificateRecord',
                             issued=self.issue_dt.strftime("%Y-%m-%d"),
                             status=self.status,
                             country=self.country,
                             scheme=self.scheme,
                             start_no=self.start_no,
                             finish_no=self.finish_no,
                             no_certs=str(self.certs),
                             factor=str(self.factor),
                             output=str(self.output),
                             status_dt=self.status_dt.strftime("%Y-%m-%d"),
                             technology=self.technology,
                             generation_type=self.generation_type or '')
        parent_node.append(node)

    def as_row(self):
        return {'CertificateRecord': {'@{}'.format(key): self.attrs[key] for
                                      key in sorted(self.attrs.keys())}}


class CertificateStation(object):
    """ We are normally interested in knowing about certificates issued to
        a station, so this class attempts to simplify this process.
        Once issued all certificates will be accounted for, but the final
        owner and status may change. This class attempts to take a bunch of
        Certificate objects and simplify them into a final set, with ownership
        and status correctly attributed.
    """
    def __init__(self, name, g_id, capacity, scheme):
        self.name = name
        self.generator_id = g_id
        self.scheme = scheme
        self.capacity = capacity
        self.certs = []

    def __len__(self):
        return len(self.certs)

    def __iter__(self):
        for c in self.certs:
            yield c

    def add_cert(self, cert):
        self.certs.append(cert)

    def as_row(self):
        return [cert.as_row() for cert in self.certs]


class CertificatesList(object):
    """ Parse a file or string for Certificate information as returned by the Ofgem webform.
    """
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
            cert = Certificates(node)
            station = CertificateStation(cert.name, cert.generator_id, cert.capacity, cert.scheme)
            self.station_data.setdefault(cert.generator_id, station).add_cert(cert)

    def __len__(self):
        return len(self.station_data)

    def as_xml(self):
        """ Return the data as formatted XML.
        :returns: String
        """
        # Create the root element
        root = etree.Element('CertificateList')
        # Make a new document tree
        doc = etree.ElementTree(root)
        for stat in sorted(self.station_data.keys()):
            self.station_data[stat].append_xml_node(root)
        return etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding='utf-8')

    def rows(self):
        """ Generator that returns station dicts.

        :returns: Dict of station data.
        :rtype: dict
        """
        for s in sorted(self.station_data.keys()):
            for info in self.station_data[s].as_row():
                yield info

