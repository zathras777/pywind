import unittest

from pywind.decc.geo import Coord
from pywind.decc.utils import latlon_as_string


class CoordTest(unittest.TestCase):
    def test_01(self):
        coord = Coord(651409.903, 313177.270)
        self.assertIsInstance(coord, Coord)
        self.assertIsNone(coord.lat)
        self.assertIsNone(coord.lon)
        self.assertEqual(coord.as_osgb36(1), (651409.9, 313177.3))
        self.assertEqual(coord.as_wgs84(), (52.6580, 1.7161))
        self.assertEqual(coord.as_wgs84(2), (52.66, 1.72))

    def test_02(self):
        with self.assertRaises(ValueError):
            Coord('651409', 313177)
            Coord(651409, '313177')
            Coord("651409, 313177")


class UtilsTest(unittest.TestCase):
    def test_01(self):
        for case in [
            (50.5, 2.5, "N50 30'00 E002 30'00"),
            (54.76644234207737, 0.2299483364627191, "N54 45'59 E000 13'47"),
            (-22.9068467, -43.1728965, "S22 54'24 W043 10'22")
        ]:
            self.assertEqual(latlon_as_string(case[0], case[1]), case[2])
