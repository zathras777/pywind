# coding=utf-8
#

import sys
from lxml import etree
from pprint import pprint

from pywind.utils import map_xml_to_dict


class Station(object):
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
        self.attrs = map_xml_to_dict(node, self.XML_MAPPING)
        pprint(self.attrs)

        # catch/correct some odd results I have observed...
        if self.attrs['technology'] is not None and b'\n' in self.attrs['technology']:
            self.attrs['technology'] = self.attrs['technology'].split(b'\n')[0]

    def __getattr__(self, item):
        if item in self.attrs:
            return self.attrs[item]
        raise AttributeError(item)

    def as_row(self):
        """ Return the information in correct format for :func:`rows()` usage
        """
        return {'@{}'.format(key): self.attrs[key] for key in self.attrs.keys()}
