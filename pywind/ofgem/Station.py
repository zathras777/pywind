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
