import os
from unittest import TestCase
from pywind.decc.extract import *


class DeccTest(TestCase):
    """ DECC access tests. """
    HERE = os.path.dirname(__file__)
    def test_01(self):
        """ Monthly Extract test """
        dme = MonthlyExtract(filename=os.path.join(self.HERE, 'files', 'decc_extract.csv'))
        self.assertTrue(dme.get_data())
        self.assertEqual(len(dme), 4896)
