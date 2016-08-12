from unittest import TestCase
from pywind.decc.Report import *


class DeccTest(TestCase):
    """ DECC access tests. """
    def test_01(self):
        """ Monthly Extract test """
        me = MonthlyExtract()
        self.assertTrue(me.get_data())
        self.assertGreater(len(me), 4000)
