import unittest
from pywind.decc.geo import *


class GeoTest(unittest.TestCase):
    def test_01(self):
        pos = osGridToLatLong(313585, 543564)
        self.assertEqual(pos.as_string(), "N54 46'45.8864\" W3 20'37.3521\"")
        pos.convert(LatLon.WGS84)
        self.assertEqual(pos.as_string(), "N54 46'46.1729\" W3 20'42.2343\"")
        pos.convert(LatLon.OSGB36)
        self.assertEqual(pos.as_string(), "N54 46'45.8864\" W3 20'37.3523\"")

