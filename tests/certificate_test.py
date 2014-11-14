from unittest import TestCase

from pywind.ofgem.Base import *
from pywind.ofgem.CertificateSearch import CertificateSearch
from pywind.ofgem.Station import Station
from pywind.ofgem.StationSearch import StationSearch

import sys

class StationTest(TestCase):
    def test_01(self):
        ss = StationSearch()
        ss.filter_name("Caynton")
        ss.filter_scheme("REGO")
        self.assertTrue(ss.get_data())
#print ss.form.data
        print len(ss)
        for s in ss.stations:
            print s.as_string()
