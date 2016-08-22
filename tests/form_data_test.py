""" Tests for pywind.ofgem.form_data """
import os
from pprint import pprint
from unittest import TestCase

from pywind.ofgem.form import _make_url
from pywind.ofgem.form_data import FormData


class UrlTest(TestCase):
    """
    Tests for the basic url function we use.
    """
    def test_01(self):
        """ URL Tests """
        for case in [
            ('Default.aspx', False, 'https://www.renewablesandchp.ofgem.gov.uk/Default.aspx'),
            ('/ReportViewer.aspx', True, 'https://www.renewablesandchp.ofgem.gov.uk/ReportViewer.aspx'),
            ('./ReportViewer.aspx', True, 'https://www.renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx')
        ]:
            self.assertEqual(_make_url(case[0], case[1]), case[2])


class FormDataTest(TestCase):
    """ Tests for the FormData class. """
    HERE = os.path.dirname(__file__)

    def test_01(self):
        """ Parse and test files/ofgem_station_search.html (this will take a while...) """
        fnn = os.path.join(self.HERE, 'files', 'ofgem_station_search.html')
        with open(fnn, 'r') as cfh:
            content = cfh.read()
        self.assertIsNotNone(content)

        ofd = FormData(content)
        self.assertIsInstance(ofd, FormData)
        self.assertEqual(len(ofd.elements), 117)
        # Check for some elements...
        for name in ['__VIEWSTATE',
                     'ReportViewer$ctl03$ctl00',
                     'ReportViewer$ctl11',
                     'ReportViewer$AsyncWait$HiddenCancelField',
                     'ReportViewer$ctl04$ctl03$ddValue',
                     'ReportViewer$ctl04$ctl05$txtValue',
                     'ReportViewer$ctl04$ctl25$cbNull']:
            self.assertTrue(name in ofd.elements)
            print(ofd.elements[name])

        print(ofd.as_post_data(False))

        self.assertTrue('__ASYNCPOST' in ofd.elements)
        self.assertEqual(ofd.elements['__ASYNCPOST'], {'value': 'true'})

    def test_02(self):
        """ Parse and test files/ofgem_certificate_search.html """
        fnn = os.path.join(self.HERE, 'files', 'ofgem_certificate_search.html')
        with open(fnn, 'r') as cfh:
            content = cfh.read()
        self.assertIsNotNone(content)
        ofd = FormData(content)
        self.assertIsInstance(ofd, FormData)

