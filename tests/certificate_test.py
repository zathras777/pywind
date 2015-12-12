import os
from unittest import TestCase

from pywind.ofgem.Certificates import Certificates, CertificatesList
from pywind.ofgem.CertificateSearch import CertificateSearch


class CertificateTest(TestCase):
    def test_01(self):
#        cs = CertificateSearch()
#        cs.set_period(2013, 1)
#        cs.filter_technology("Wind")
#        cs.filter_scheme('REGO')

#        self.assertTrue(cs.get_data())
 #       self.assertIsInstance(cs[0], Certificates)
 #       self.assertEqual(cs[0].period, 'Jan-2013')
        pass

    def test_02(self):
        xml_file = os.path.join(os.path.dirname(__file__), 'cert_test.xml')
        cl = CertificatesList(xml_file)
        print(cl)
        self.assertEqual(len(cl), 5)

        s0, s1 = cl.stations()
        print(s0)
        print(s1)
        print(dir(s1['REGO']))
        print(s1['REGO'].final_output())
        print(s1['REGO'].get_final_ranges())