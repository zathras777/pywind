# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
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
from pywind.ofgem.CertificateRange import CertificateTree, CertificateRange


class Certificates(object):
    FIELDS = ['accreditation', 'name','capacity','scheme','country',
              'technology','output','period','certs',
              'start_no','finish_no','factor','issue_dt',
              'status','status_dt','current_holder','reg_no']

    def __init__(self, node):
        """ Extract information from the supplied XML node.
        """

        mapping = [
            ['textbox4', 'accreditation'],
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

        def set_attr_from_xml(obj, node, mapping):
            val = node.get(mapping[0], None)
            if val is not None and val.isdigit():
                val = int(val)
            if val is None and len(mapping) == 3:
                val = mapping[2]
            setattr(obj, mapping[1], val)

        for m in mapping:
            set_attr_from_xml(self, node, m)

        self.factor = float(self.factor)
        self.certs = int(self.certs) or 0
        self.capacity = float(self.capacity) or 0
        self.issue_dt = datetime.strptime(self.issue_dt, '%Y-%m-%dT%H:%M:00').date()
        self.status_dt = datetime.strptime(self.status_dt, '%Y-%m-%dT%H:%M:00').date()

        if self.period.startswith("01"):
            dt = datetime.strptime(self.period[:10], '%d/%m/%Y')
            self.period = dt.strftime("%b-%Y")

    @property
    def digits(self):
        return 10 if self.scheme == 'REGO' else 6

    @property
    def start(self):
        return int(self.start_no[10:10 + self.digits])

    @property
    def finish(self):
        return int(self.finish_no[10:10 + self.digits])

    def as_string(self):
        s = '\n'
        for f in self.FIELDS:
            s += "    %-30s: %s\n" % (f.capitalize(), getattr(self, f))
        return s

    def as_range(self):
        return CertificateRange(self.start, self.finish, self.current_holder, self.factor, self.status_dt)

    def as_dict(self):
        return {f: getattr(self, f) for f in self.FIELDS}

    def as_list(self):
        return [getattr(self, f) for f in self.FIELDS]

    def output_summary(self):
        perc = (float(self['certs']) / self['capacity']) * 100
        return "%s: %s   %s vs %s => %.02f%%" % (self['period'], self['name'], self['certs'],
                                                 self['capacity'], perc)


class StationCertificates(object):
    """ We are normally interested in knowing about certificates issued to
        a station, so this class attempts to simplify this process.
        Once issued all certificates will be accounted for, but the final
        owner and status may change. This class attempts to take a bunch of
        Certificate objects and simplify them into a final set, with ownership
        and status correctly attributed.
    """
    def __init__(self):
        self.certs = []

    def __len__(self):
        return len(self.certs)

    def __iter__(self):
        for c in self.certs:
            yield c

    def add_cert(self, cert):
        self.certs.append(cert)

    def finalise(self):
        final = []
        start = finish = -1
        overlaps = 0
        # Go through certificate records in order of status_dt.
        for c in sorted(self.certs, key=lambda x: "{}{}".format(x.status_dt, x.start)):
#            print("{} [{}]: {}: {} - {} -- {}".format(c.name, c.scheme, c.status_dt, c.start, c.finish, c.status))
            if start == -1:
                start = c.start
                finish = c.finish
            else:
                if c.start < finish and c.finish > start:
                    overlaps += 1
#                    print("OVERLAP!!! {} [{}] ({}-{} vs {}-{})".format(c.name, c.scheme, c.start, c.finish, start, finish))
    #                for cc in self.certs:
    #                    print("{}: {} - {} -- {}".format(cc.status_dt, cc.start, cc.finish, cc.status))

                if c.finish > finish:
                    finish = c.finish
                if c.start < start:
                    start = c.start
        if overlaps > 0:
            print("OVERLAPS: {} [{}]".format(self.certs[0].name, self.certs[0].scheme))

#            if ranges == []:
#                ranges.append(())


#            print(c.as_string())


class CertificatesList(object):
    NSMAP = {'a': 'CertificatesExternalPublicDataWarehouse'}

    def __init__(self, filename=None, data=None):
        self.certificates = []
        self.station_data = {}
        if filename is None and data is None:
            return

        if filename is not None:
            xml = etree.parse(filename)
        elif data is not None:
            xml = etree.fromstring(data)

        for node in xml.xpath('.//a:Detail', namespaces=self.NSMAP):
            self.certificates.append(Certificates(node))

    def __len__(self):
        return len(self.certificates)

    def stations(self):
        if self.station_data == {}:
            self._collate_stations()
        for s in sorted(self.station_data.keys()):
            yield self.station_data[s]

    def _collate_stations(self):
        for c in self.certificates:
            if c.name not in self.station_data:
                self.station_data[c.name] = {'accreditation': c.accreditation, 'name': c.name}
#            self.station_data[c.name].setdefault(c.scheme, CertificateTree()).add_range(c.as_range())
            self.station_data[c.name].setdefault(c.scheme, StationCertificates()).add_cert(c)

        # finalise...
        for s in self.station_data:
            for ss in ['REGO', 'RO']:
                if ss in self.station_data[s]:
                    self.station_data[s][ss].finalise()
