import unittest

from pywind.decc.geo import *
from pywind.decc.points import Point
from pywind.decc.utils import latlon_as_string


class GeoTest(unittest.TestCase):
    def test_01(self):
        pos = os_grid_to_latlon(313585, 543564)
        self.assertEqual(pos.as_string(), "N54 46'45.8864\" W3 20'37.3521\"")
        pos.convert(LatLon.WGS84)
        self.assertEqual(pos.as_string(), "N54 46'46.1729\" W3 20'42.2343\"")
        pos.convert(LatLon.OSGB36)
        self.assertEqual(pos.as_string(), "N54 46'45.8864\" W3 20'37.3523\"")

    def test_02(self):
        """ Test parsing of different formats for os_grid_to_latlon """
        for case in [
            ('313585', '543564', True),
            ('313,585', '543,564', True),
            ('313.585', '5.43564', False),
            ('AB313585', '543564', False),
            ('313585,543564', '', False),
            (313585, 543564, True)
        ]:
            if case[2]:
                self.assertIsInstance(os_grid_to_latlon(case[0], case[1]), LatLon)
            else:
                with self.assertRaises(ValueError):
                    os_grid_to_latlon(case[0], case[1])


class PointTest(unittest.TestCase):
    def test_01(self):
        """ Basic Point tests """
        for case in [
            ('osref', 651409.903, 313177.270, [
                ('wgs84', 52.657977, 1.716038),
                ('osgb36', 52.657568, 1.717908),
                ('gridref', 'TG51SW26')
            ])
        ]:
            point = Point(case[0], case[1], case[2])
            self.assertTrue(case[0] in point.coords)
            for conv in case[3]:
                val = point[conv[0]]


class UtilsTest(unittest.TestCase):
    def test_01(self):
        for case in [
            (50.5, 2.5, "N50 30'00 E002 30'00"),
            (54.76644234207737, 0.2299483364627191, "N54 45'59 E000 13'47"),
            (-22.9068467, -43.1728965, "S22 54'24 W043 10'22")
        ]:
            self.assertEqual(latlon_as_string(case[0], case[1]), case[2])
