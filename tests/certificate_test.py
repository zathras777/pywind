from unittest import TestCase

from pywind.ofgem.Certificates import Certificates
from pywind.ofgem.CertificateSearch import CertificateSearch


class CertificateTest(TestCase):
    def test_01(self):
        cs = CertificateSearch()
        cs.set_period(2013, 1)
        cs.filter_technology("Wind")
        cs.filter_scheme('REGO')

        self.assertTrue(cs.get_data())
        self.assertIsInstance(cs[0], Certificates)
        self.assertEqual(cs[0].period, 'Jan-2013')
