import unittest

from pywind.roc.eroc import *


class ROCTest(unittest.TestCase):
    def test_01(self):
        ep = EROCPrices()
        self.assertTrue(ep.get_prices())
        self.assertTrue(200704 in ep.periods)
        self.assertEqual(ep[200704], 47.51)
