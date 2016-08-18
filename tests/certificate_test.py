""" CertificateList tests """
import os
from unittest import TestCase

from pywind.ofgem.Certificates import CertificatesList


class CertificateListsTest(TestCase):
    """ CertificatesListTest """
    def test_02(self):
        """ Test certificate parsing. 5 entries for 3 stations. """
        xml_file = os.path.join(os.path.dirname(__file__), 'cert_test.xml')
        cl = CertificatesList(xml_file)
        self.assertIsInstance(cl, CertificatesList)
        self.assertEqual(len(cl), 3)
