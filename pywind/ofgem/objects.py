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

from datetime import datetime
from pprint import pprint

from pywind.utils import map_xml_to_dict


class OfgemObjectBase(object):
    XML_MAPPING = None

    def __init__(self, node):
        """ Extract information from the supplied XML node.
            The factor figure is MWh per certificate.
        """
        if self.XML_MAPPING is None:
            raise NotImplementedError("Child classes should define their XML_MAPPING")

        self.attrs = map_xml_to_dict(node, self.XML_MAPPING)
#        pprint(self.attrs)

    def __getattr__(self, item):
        if item in self.attrs:
            return self.attrs[item]
        raise AttributeError(item)

    def as_row(self):
        """
        Return the information in correct format for :func:`rows()` usage

        :returns: Formatted attribute dict
        :rtype: dict
        """
        return {'@{}'.format(key): self.attrs[key] for key in self.attrs.keys()}


class Certificates(OfgemObjectBase):
    """ Certificate Number Fact Sheet
        https://www.ofgem.gov.uk/sites/default/files/docs/roc_identifier_fact_sheet_dec_2015.pdf

    """
    XML_MAPPING = (
            ('textbox4', 'generator_id'),
            ('textbox13', 'name'),
            ('textbox5', 'scheme'),
            ('textbox19', 'capacity', 'float', 0.0),
            ('textbox12', 'country'),
            ('textbox15', 'technology'),
            ('textbox31', 'generation_type'),
            ('textbox18', 'period'),
            ('textbox21', 'certs', 'int', 0),
            ('textbox24', 'start_no'),
            ('textbox27', 'finish_no'),
            ('textbox37', 'factor', 'float', 0.0),
            ('textbox30', 'issue_dt', 'date'),
            ('textbox33', 'status'),
            ('textbox36', 'status_dt', 'date'),
            ('textbox39', 'current_holder'),
            ('textbox45', 'reg_no')
        )

    def __init__(self, node):
        OfgemObjectBase.__init__(self, node)

        if self.attrs['period'].startswith("01"):
            dt = datetime.strptime(self.attrs['period'][:10], '%d/%m/%Y')
            self.attrs['period'] = dt.strftime("%b-%Y")

    def __str__(self):
        return "        {}  {}  {:5d}  {}".format(self.issue_dt.strftime("%Y %b %d"), self.start_no,
                                                  self.certs, self.current_holder)

    @property
    def digits(self):
        """ Number of digits that store the certificate number.

        :rtype: int
        """
        return 10 if self.scheme == 'REGO' else 6

    @property
    def certificates(self):
        """ Number of certificates covered by this object.

        :rtype: int
        """
        return self.finish - self.start + 1

    @property
    def start(self):
        """ Return the numeric start number for the certificates.
        Each certificate number contains the station, period and the number of the certificate,
        so this function extracts the numeric part.

        :returns: Start number of the certificates referenced
        :rtype: int
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

    def output_summary(self):
        """ Return a string with the output for the certificates.

        :rtype: str
        """
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self.period, self.name, self.certs,
                                                 self.capacity, perc)

    def station_details(self):
        """ Get a dict object with the station information for these certificates.

        :returns: Dict with just information relevant to identifying the station
        :rtype: dict
        """
        rv_dict = {fld: self.attrs[fld] for fld in ['generator_id',
                                                    'name',
                                                    'scheme',
                                                    'capacity',
                                                    'country',
                                                    'technology']}
        rv_dict['output'] = self.output
        return rv_dict

    @property
    def output(self):
        """ Calculate the output based on the number of certs issued and factor.

        :returns: Numeric output or 0
        :rtype: float
        """
        return self.certs / self.factor


class Station(OfgemObjectBase):
    """
    Store details of a single station using data from Ofgem.

    The exposed object makes the individual pieces of data available by \
    acting as a dict, i.e.
    .. :code::

            name = station['name']

    The convenience function :func:`as_string` will return a full list of the data \
    formatted for display in a terminal.

    """
    XML_MAPPING = (
        ('GeneratorID', 'generator_id'),
        ('StatusName', 'status'),
        ('GeneratorName', 'name'),
        ('SchemeName', 'scheme'),
        ('Capacity', '', 'float'),
        ('Country',),
        ('TechnologyName', 'technology'),
        ('OutputType', 'output'),
        ('AccreditationDate', 'accreditation_dt', 'date'),
        ('CommissionDate', 'commission_dt', 'date'),
        ('textbox6', 'developer'),
        ('textbox61', 'developer_address', 'address'),
        ('textbox65', 'address', 'address'),
        ('FaxNumber', 'fax')
    )

    def __init__(self, node):
        OfgemObjectBase.__init__(self, node)

        # catch/correct some odd results I have observed...
        if self.attrs['technology'] is not None and '\n' in self.attrs['technology']:
            self.attrs['technology'] = self.attrs['technology'].split('\n')[0]


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
