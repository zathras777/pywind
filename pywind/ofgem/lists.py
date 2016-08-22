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

"""
.. moduleauthor:: david reid <zathrasorama@gmail.com>

"""
from lxml import etree

from pywind.ofgem.objects import Certificates, CertificateStation


class CertificatesList(object):
    """
    Class to parse a list of certificate records. This builds a list of the stations
    referenced, which is normally what we're interested in.
    """
    NSMAP = {'a': 'CertificatesExternalPublicDataWarehouse'}

    def __init__(self, filename=None, data=None):
        self.station_data = {}
        self.certs = []
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
            self.certs.append(cert)

    def __len__(self):
        return len(self.station_data)

    def rows(self):
        """ Generator that returns station dicts.

        :returns: Dict of station data.
        :rtype: dict
        """
        for s in sorted(self.station_data.keys()):
            for info in self.station_data[s].as_row():
                yield info


