import os
import unittest
from lxml import etree

import datetime

from pywind.ofgem.objects import Certificates
from pywind.utils import map_xml_to_dict, StdoutFormatter


class UtilTest(unittest.TestCase):
    """
    ROC Tests
    """
    HERE = os.path.dirname(__file__)

    def test_map_xml_to_dict(self):
        """ Test mapping from XML to dict using a mapping tuple.
        """
        NSMAP = {'a': 'CertificatesExternalPublicDataWarehouse'}
        with open(os.path.join(self.HERE, 'files', 'certificate_test.xml'), 'r') as xfh:
            xml = etree.parse(xfh)

        for detail in xml.getroot().xpath('.//a:Detail', namespaces=NSMAP):
            rv_dict = map_xml_to_dict(detail, Certificates.XML_MAPPING)
            self.assertIsInstance(rv_dict, dict)
            self.assertEqual(len(rv_dict), 17)
            self.assertIsInstance(rv_dict['factor'], float)
            self.assertIsInstance(rv_dict['issue_dt'], datetime.date)
            self.assertTrue('name' in rv_dict)
            self.assertNotEqual(len(rv_dict['name']), 0)
            self.assertGreater(rv_dict['capacity'], 0)
            self.assertGreater(len(rv_dict['scheme']), 0)

    def test_stdout_formatter(self):
        """ Test StdoutFormatter class
        """
        for case in [
            (('5s', '5s'), ('abcde', 'abcde'), 2, "  abcde  abcde\n  -----  -----",
             ('hello', 'world'), '  hello  world'),
            (('5s', '5.1f'), ('abcde', 'abcde'), 2, "  abcde  abcde\n  -----  -----",
             ('world', 1.1), '  world    1.1'),
        ]:
            fmt = StdoutFormatter(*case[0])
            self.assertIsInstance(fmt, StdoutFormatter)
            self.assertEqual(len(fmt.columns), case[2])
            self.assertEqual(fmt.titles(*case[1]), case[3])
            self.assertEqual(fmt.row(*case[4]), case[5])

        fmt2 = StdoutFormatter("5.2f")
        with self.assertRaises(ValueError):
            fmt2.row("hello")
            fmt2.row(123)
            fmt2.row(None)
        self.assertEqual(fmt2.row(123.45), "  123.45")
