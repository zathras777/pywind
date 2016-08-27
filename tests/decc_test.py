import os
from datetime import date
from unittest import TestCase

from pywind.decc.extract import *


class DeccTest(TestCase):
    """ DECC access tests. """
    HERE = os.path.dirname(__file__)

    def test_01(self):
        """ Monthly Extract test """
        exfn = os.path.join(self.HERE, 'files', 'decc_extract.csv')
        dme = MonthlyExtract(filename=exfn)
        self.assertTrue(dme.get_data())
        self.assertEqual(len(dme), 4896)

        for case in [
            (0, {'site_name': '10 Clares Farm Close',
                 'country': 'England',
                 'planning_application_withdrawn': date(2009, 5, 20)
                 }),
            (100, {'site_name': 'Altamuskin Extension',
                   'height_of_turbines_m': 110.0,
                   'installed_capacity_mwelec': 7.1,
                   }),
            (1000, {'chp_enabled': True,
                    'country': 'Scotland',
                    'lat': 55.8404
                    }),
            (4895, {'country': 'England',
                    'site_name': 'land off the A6006',
                    'ref_id': 2237})
        ]:
            obj = dme[case[0]]
            self.assertIsInstance(obj, DeccRecord)
            for key in case[1]:
                self.assertTrue(key in obj)
                self.assertEqual(getattr(obj, key), case[1][key])
        with self.assertRaises(IndexError):
            obj = dme[5000]
            obj = dme[-1]

        checked = 0
        for obj in dme:
            if obj.fit_tariff_p_kwh is not None:
                self.assertTrue(obj.fit_tariff_p_kwh in
                                [0.0, 1.4, 2.99, 3.07, 6.38, 7.24, 9.02, 10.96],
                                "FIT Rate {}".format(obj.fit_tariff_p_kwh))
                self.assertTrue(obj.fit_rate_mwh() in
                                [0.0, 14, 29.9, 30.7, 63.8, 72.4, 90.2, 109.6])
            checked += 1
        self.assertEqual(checked, len(dme))
