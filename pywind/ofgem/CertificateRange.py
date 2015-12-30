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


"""
    When Ofgem issues certificates it does so in ranges, but they can be
    bought/sold/transferred/revoked and so keeping track of the final
    quantity issued and who owns them is not as easy as it first appears.
    To solve this problem the classes in this file can be used.

    As an example, assume the following certificate issuances have been recorded
    for a given period for a station (assuming a factor of .25).

        25 Oct 2012  Issued       0-2896    Npower Renewables Ltd (Wind)
 	    25 Oct 2012	 Revoked	334-2896
 	    25 Oct 2012  Issued	      0-333	    Npower Renewables Ltd (Wind)
 	    28 Nov 2012  Issued    2897-5459    Npower Renewables Ltd (Wind)
 	    28 Nov 2012  Revoked   2897-5459

    The final outcome would be obtained as follows

    >> from pywind.ofgem.CertificateRange import *
    >> from datetime import date

    >> ct = CertificateTree()
    >> ct.add_range(CertificateRange(0, 2896, 'Npower Renewables Ltd (Wind)', .25, date(2012,10,25)))
    >> ct.add_range(CertificateRange(334, 2896, None, .25, date(2012,10,25)))
    >> ct.add_range(CertificateRange(0, 333, 'Npower Renewables Ltd (Wind)', .25, date(2012,10,25)))
    >> ct.add_range(CertificateRange(2897, 5459, 'Npower Renewables Ltd (Wind)', .25, date(2012,11,28)))
    >> ct.add_range(CertificateRange(2897, 5459, None, .25, date(2012,11,28)))
    >> ct.finalise()
    >> final = ct.get_final_ranges()
    >> final
    [0-333 owned by Npower Renewables Ltd (Wind)]
    >> len(final[0])
    334
    >> final[0].mwh()
    84

    Another example.

        4 Oct 2012   Issued    0-144    SmartestEnergy Ltd
 	    19 Feb 2013  Issued	   0-0      SmartestEnergy Ltd
 	    12 Mar 2013  Issued    1-144    Power4All Limited

    >> from pywind.ofgem.CertificateRange import *
    >> from datetime import date

    >> ct = CertificateTree()
    >> ct.add_range(CertificateRange(0, 144, 'SmartestEnergy Ltd', 1, date(2012, 10, 4)))
    >> ct.add_range(CertificateRange(0, 0, 'SmartestEnergy Ltd', 1, date(2013, 2, 19)))
    >> ct.add_range(CertificateRange(1, 144, 'Power4All Limited', 1, date(2013, 3, 12)))
    >> ct.finalise()
    >> final = ct.get_final_ranges()
    >> final
    [0-0 owned by SmartestEnergy Ltd, 1-144 owned by Power4All Limited]

"""
import math


class CertificateRange(object):
    """ Class to represent a range of issued certificates. The
        range is numeric and has an owner and the date of issuance.
        Created ranges are intended to be used with a CertificateTree
        object to determine the final allocations of certificates.
    """
    def __init__(self, start, finish, owner, factor=1.000, date=None):
        self.start = start
        self.finish = finish
        self.owner = owner
        self.factor = factor
        self.date = date

    def __repr__(self):
        return "%d-%d owned by %s" % (self.start, self.finish, self.owner)

    def __len__(self):
        return (self.finish - self.start) + 1

    def mwh(self):
        """ Use the factor to calculate the MWh that would have resulted in
            the number of certificates being issued. Use math.ceil to round
            up to the nearest whole number.
        """
        return math.ceil(((self.finish - self.start) + 1) * self.factor)

    def __gt__(self, other):
        if self.start < other.start: return False
        if self.start == other.start and self.finish < other.finish: return False
        return True

    def datesort(self):
        """ Return the string to be used when date sorting ranges. Ranges where
            owner is None should go at the end of the date ranges.
        """
        if self.date is None:
            return ''
        return self.date.strftime('%y%m%d') + '%s' % (self.owner or 'ZZZZZZZZZZ')


class CertificateTree(object):
    """ This class stores a series of CertificateRange objects and then
        builds an overlap tree based on their ranges. Finally it assigns
        ownership based on the ranges provided allowing a definitive list
        of ranges and ownership to be extracted.
    """

    class CertificateNode(object):
        """ Each CertificateNode marks a position in a the sequence. Optionally
            it has links to nodes below (left) and above (right) of it.
            Each node also has an optional owner associated with it.
        """
        def __init__(self, value, left=None, right=None, owner=None, factor=1.00):
            self.value = value
            self.left = left
            self.right = right
            self.owner = owner
            self.factor = factor

        def __str__(self):
            print("CertificateNode: {}, {}, {}, {}".format(self.value, self.left, self.right, self.owner))

    def __init__(self):
        self.top_node = None
        self.flattened_nodes = None
        self.ranges = []
        self.center = 0

    def add_range(self, range):
        """ Add a CertificateRange object. We keep the list correctly
            sorted and update the center value for the tree as we go.
        """
        print(range)
        self.ranges.append(range)
        self.ranges = sorted(self.ranges)
        self.center = self.ranges[-1].finish / 2

    def finalise(self):
        self._build_tree()

    def min(self):
        if len(self.ranges) == 0:
            return 0
        return self.ranges[0].start

    def max(self):
        if len(self.ranges) == 0:
            return 0
        return self.ranges[-1].finish

    def find_nodes_by_range(self, start, finish):
        results = []
        self._scan(self.top_node, start, finish, results)
        return results

    def get_final_ranges(self, node=None):
        if self.flattened_nodes is None:
            self.flattened_nodes = self._flatten()
        ranges = []
        owners = []
        r = None

        if len(self.flattened_nodes) == 0:
            return 0

        for n in sorted(self.flattened_nodes):
            v = self.flattened_nodes[n]
            if v:
                if r is None:
                    r = CertificateRange(n, n, v['owner'], v['factor'])
                    owners.append(v['owner'])
                elif r.owner == v:
                    r.finish = n
                elif len(owners) > 0:
                    start = n
                    if len(owners) > 1 and v == owners[-2]:
                        start = r.finish + 1
                        owners = owners[:-1]
                    else:
                        r.finish = n - 1
                        owners.append(v['owner'])
                    ranges.append(r)
                    r = CertificateRange(start, n, v['owner'], v['factor'])

            elif r is not None:
                ranges.append(r)
                r = None
                owners = []

        if r is not None:
            ranges.append(r)
        return ranges

    def final_output(self):
        if self.flattened_nodes is None:
            self.flattened_nodes = self._flatten()

        if len(self.flattened_nodes) == 0:
            return 0

        for n in sorted(self.flattened_nodes):
            v = self.flattened_nodes[n]
            print(v)

    def _insert(self, value, node):
        if node.value == value:
            return
        if value < node.value:
            if node.left:
                self._insert(value, node.left)
            else:
                node.left = self.CertificateNode(value)
        elif value > node.value:
            if node.right:
                self._insert(value, node.right)
            else:
                node.right = self.CertificateNode(value)

    def _scan(self, node, start, finish, results):
        if start <= node.value <= finish:
            results.append(node)
        if node.left and start < node.value:
            self._scan(node.left, start, finish, results)
        if node.right and finish > node.value:
            self._scan(node.right, start, finish, results)

    def _build_tree(self):
        """ Actually build the tree. Start by adding the center node
            and then add the start/finish nodes for each of our ranges.
            Finally go through the ranges and assign/remove ownership based
            on the dates that the awards were made.
        """
        if len(self.ranges) == 0:
            return
        self.top_node = self.CertificateNode(self.center)
        for r in self.ranges:
            self._insert(r.start, self.top_node)
            self._insert(r.finish, self.top_node)

        for r in sorted(self.ranges, key=lambda x: x.datesort()):
            nodes = self.find_nodes_by_range(r.start, r.finish)
            for n in nodes:
                n.owner = r.owner
                n.factor = r.factor

    def _add_nodes(self, node, nodes):
        nodes[node.value] = {'owner': node.owner, 'factor': node.factor}
        if node.left:
            self._add_nodes(node.left, nodes)
        if node.right:
            self._add_nodes(node.right, nodes)

    def _flatten(self):
        nodes = {}
        if self.top_node is not None:
            self._add_nodes(self.top_node, nodes)
        print("    _flatten:")
        for n in nodes.values():
            print("        {}".format(str(n)))

        return nodes
