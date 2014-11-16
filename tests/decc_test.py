from unittest import TestCase
from pywind.decc.Report import *


class DeccTest(TestCase):
    def test_01(self):
        me = MonthlyExtract()
        self.assertTrue(me.get_data())
        self.assertGreater(len(me), 7400)