import unittest
from lxml import etree
from pprint import pprint

import datetime

from pywind.ofgem.Certificates import Certificates
from pywind.utils import map_xml_to_dict

certificates_xml = """
<Report xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="CertificatesExternalPublicDataWarehouse"
        xsi:schemaLocation="CertificatesExternalPublicDataWarehouse https://colop-rodw-a01.corp.ofgem.gov.uk/ReportServer?%2FDatawarehouseReports%2FCertificatesExternalPublicDataWarehouse&amp;rs%3ACommand=Render&amp;rs%3AFormat=XML&amp;rs%3ASessionID=3ezqkv3jc0lqks55abnfuz55&amp;rc%3ASchema=True" Name="CertificatesExternalPublicDataWarehouse" textbox10="All Certificates by Accreditation (RO, REGO)"
        lblDate="Period of Generation :"
        textbox7="Jan 2016 - Jan 2016"
        textbox8="Total certificates:"
        textbox47="15994547">
  <table1>
    <Detail_Collection>
        <Detail textbox4="G01337HYEN"
                textbox13="Upwey Hydro Power"
                textbox19="15.00"
                textbox5="REGO"
                textbox12="England"
                textbox15="Hydro"
                textbox31="N/A"
                textbox18="Jan-2016"
                textbox21="10"
                textbox24="G01337HYEN0000000000010116310116GEN"
                textbox27="G01337HYEN0000000009010116310116GEN"
                textbox37="1.000000000000"
                textbox30="2016-01-31T00:00:00"
                textbox33="Issued"
                textbox36="2016-01-31T00:00:00"
                textbox39="Richard A Willett"
                textbox45=""/>
        <Detail textbox4="G04762PVEN"
                textbox13="Copdock Mill PV"
                textbox19="70.56"
                textbox5="REGO"
                textbox12="England"
                textbox15="Photovoltaic "
                textbox31="N/A"
                textbox18="Jan-2016"
                textbox21="1"
                textbox24="G04762PVEN0000000000010116310116GEN"
                textbox27="G04762PVEN0000000000010116310116GEN"
                textbox37="1.000000000000"
                textbox30="2016-02-01T00:00:00"
                textbox33="Issued"
                textbox36="2016-02-01T00:00:00"
                textbox39="H G Gladwell &amp; Sons Ltd"
                textbox45="655853"/>
    </Detail_Collection>
  </table1>
</Report>
"""


class UtilTest(unittest.TestCase):
    """
    ROC Tests
    """
    def test_map_xml_to_dict(self):
        """ Test mapping from XML to dict using a mapping tuple.
        """
        NSMAP = {'a': 'CertificatesExternalPublicDataWarehouse'}
        xml = etree.fromstring(certificates_xml)
        for detail in xml.getroottree().xpath('.//a:Detail', namespaces=NSMAP):
            rv_dict = map_xml_to_dict(detail, Certificates.XML_MAPPING)
            self.assertIsInstance(rv_dict, dict)
            self.assertEqual(len(rv_dict), 17)
            self.assertIsInstance(rv_dict['factor'], float)
            self.assertIsInstance(rv_dict['issue_dt'], datetime.date)


