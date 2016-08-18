""" Tests for pywind.ofgem.form_data """
import os
from pprint import pprint
from unittest import TestCase

from pywind.ofgem.form import _make_url
from pywind.ofgem.form_data import FormData

FORM_ONE = """<form name="form1" method="post"
      action="./ReportViewer.aspx?ReportPath=%2fDatawarehouseReports%2f..." id="form1">
  <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJMT..." />
</form>"""

FORM_TWO = """
<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="75CF6949" />
"""

FORM_THREE = """<form name="form1" method="post"
      action="./ReportViewer.aspx?ReportPath=%2fDatawarehouseReports%2f..." id="form1">
  <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJMT..." />
  <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="75CF6949" />
</form>"""

RESPONSE_ONE = "1|#||4|76|pageRedirect||%2fLoggedIn%2fErrorPage.aspx%3faspxerrorpath%3d%2fPublic%2fReportViewer.aspx|"

FORM_FOUR = """<form name="form1" method="post"
      action="./ReportViewer.aspx?ReportPath=%2fDatawarehouseReports%2f..." id="form1">
  <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJMT..." />
  <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="75CF6949" />
  <table>
								<tr IsParameterRow="true">
									<td><label for="ReportViewer_ctl04_ctl03_txtValue"><span><font face="Verdana" size="1">Scheme:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl03"><font face="Verdana" size="1">
										<div onactivate="event.cancelBubble=true;" nowrap="nowrap">
											<input name="ReportViewer$ctl04$ctl03$txtValue" type="text" size="28" readonly="readonly" id="ReportViewer_ctl04_ctl03_txtValue" disabled="disabled" style="background-color:#ECE9D8;" /><input src="/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=11.0.3366.16&Name=Microsoft.Reporting.WebForms.Icons.MultiValueSelect.gif" name="ReportViewer$ctl04$ctl03$ddDropDownButton" type="image" id="ReportViewer_ctl04_ctl03_ddDropDownButton" alt="Select a value" title="Select a value" style="vertical-align:top;cursor:pointer;" disabled="disabled" />
										</div>
									</font></div></td><td width="22px"></td><td><label for="ReportViewer_ctl04_ctl05_txtValue"><span><font face="Verdana" size="1">Technology Group:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl05"><font face="Verdana" size="1">
										<div onactivate="event.cancelBubble=true;" nowrap="nowrap">
											<input name="ReportViewer$ctl04$ctl05$txtValue" type="text" size="28" readonly="readonly" id="ReportViewer_ctl04_ctl05_txtValue" disabled="disabled" style="background-color:#ECE9D8;" /><input src="/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=11.0.3366.16&Name=Microsoft.Reporting.WebForms.Icons.MultiValueSelect.gif" name="ReportViewer$ctl04$ctl05$ddDropDownButton" type="image" id="ReportViewer_ctl04_ctl05_ddDropDownButton" alt="Select a value" title="Select a value" style="vertical-align:top;cursor:pointer;" disabled="disabled" />
										</div>
									</font></div></td>
								</tr><tr IsParameterRow="true">
									<td><label for="ReportViewer_ctl04_ctl07_txtValue"><span><font face="Verdana" size="1">RO Order:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl07"><font face="Verdana" size="1">
										<div onactivate="event.cancelBubble=true;" nowrap="nowrap">
											<input name="ReportViewer$ctl04$ctl07$txtValue" type="text" size="28" readonly="readonly" id="ReportViewer_ctl04_ctl07_txtValue" disabled="disabled" style="background-color:#ECE9D8;" /><input src="/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=11.0.3366.16&Name=Microsoft.Reporting.WebForms.Icons.MultiValueSelect.gif" name="ReportViewer$ctl04$ctl07$ddDropDownButton" type="image" id="ReportViewer_ctl04_ctl07_ddDropDownButton" alt="Select a value" title="Select a value" style="vertical-align:top;cursor:pointer;" disabled="disabled" />
										</div>
									</font></div></td><td width="22px"></td><td><label for="ReportViewer_ctl04_ctl09_txtValue"><span><font face="Verdana" size="1">Generation Type:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl09"><font face="Verdana" size="1">
										<div onactivate="event.cancelBubble=true;" nowrap="nowrap">
											<input name="ReportViewer$ctl04$ctl09$txtValue" type="text" size="28" readonly="readonly" id="ReportViewer_ctl04_ctl09_txtValue" disabled="disabled" style="background-color:#ECE9D8;" /><input src="/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=11.0.3366.16&Name=Microsoft.Reporting.WebForms.Icons.MultiValueSelect.gif" name="ReportViewer$ctl04$ctl09$ddDropDownButton" type="image" id="ReportViewer_ctl04_ctl09_ddDropDownButton" alt="Select a value" title="Select a value" style="vertical-align:top;cursor:pointer;" disabled="disabled" />
										</div>
									</font></div></td>
								</tr><tr IsParameterRow="true">
									<td><label for="ReportViewer_ctl04_ctl11_txtValue"><span><font face="Verdana" size="1">Country:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl11"><font face="Verdana" size="1">
										<div onactivate="event.cancelBubble=true;" nowrap="nowrap">
											<input name="ReportViewer$ctl04$ctl11$txtValue" type="text" size="28" readonly="readonly" id="ReportViewer_ctl04_ctl11_txtValue" disabled="disabled" style="background-color:#ECE9D8;" /><input src="/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=11.0.3366.16&Name=Microsoft.Reporting.WebForms.Icons.MultiValueSelect.gif" name="ReportViewer$ctl04$ctl11$ddDropDownButton" type="image" id="ReportViewer_ctl04_ctl11_ddDropDownButton" alt="Select a value" title="Select a value" style="vertical-align:top;cursor:pointer;" disabled="disabled" />
										</div>
									</font></div></td><td width="22px"></td><td><label for="ReportViewer_ctl04_ctl13_ddValue"><span><font face="Verdana" size="1">Show Agent Groups:</font></span></label></td><td><div id="ReportViewer_ctl04_ctl13"><font face="Verdana" size="1">
										<select name="ReportViewer$ctl04$ctl13$ddValue" id="ReportViewer_ctl04_ctl13_ddValue" disabled="disabled">
											<option value="0">&lt;Select&nbsp;a&nbsp;Value&gt;</option>
											<option selected="selected" value="1">Generating&nbsp;Stations&nbsp;and&nbsp;Agent&nbsp;Groups</option>
											<option value="2">Agent&nbsp;Groups</option>
											<option value="3">Generating&nbsp;Stations</option>

										</select>
									</font></div></td>
								</tr><tr IsParameterRow="true">
  </table>
</form>
"""


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
    def test_01(self):
        """ Basic tests """
        fd_obj = FormData("")
        self.assertIsInstance(fd_obj, FormData)
        self.assertEqual(len(fd_obj.elements), 4)
        self.assertTrue('__ASYNCPOST' in fd_obj.elements)
        self.assertEqual(fd_obj.elements['__ASYNCPOST'], {'value': 'true'})

    def test_02(self):
        """ Basic tests """
        fd_obj = FormData(FORM_ONE)
        self.assertIsInstance(fd_obj, FormData)
        self.assertEqual(len(fd_obj.elements), 5)
        self.assertTrue('__ASYNCPOST' in fd_obj.elements)
        self.assertTrue('__VIEWSTATE' in fd_obj.elements)
        self.assertEqual(fd_obj.elements['__VIEWSTATE']['value'], "/wEPDwUJMT...")
        self.assertEqual(fd_obj.elements['__VIEWSTATE']['tag'], "input")
        self.assertEqual(fd_obj.elements['__VIEWSTATE']['type'], "hidden")
        self.assertTrue('__VIEWSTATE' in fd_obj.elements)

    def test_03(self):
        """ Update test """
        fd_obj = FormData()
        self.assertIsInstance(fd_obj, FormData)
        self.assertEqual(len(fd_obj.elements), 4)
        self.assertTrue(fd_obj.update(FORM_ONE))
        self.assertEqual(len(fd_obj.elements), 5)
        self.assertEqual(fd_obj.method, 'post')

    def test_04(self):
        """ Update test #2 """
        fd_obj = FormData(FORM_TWO)
        self.assertEqual(len(fd_obj.elements), 4)
        self.assertFalse('__VIEWSTATEGENERATOR' in fd_obj)
        self.assertTrue(fd_obj.update(FORM_THREE))
        self.assertEqual(len(fd_obj.elements), 6)

    def test_05(self):
        """ Failed update test """
        fd_obj = FormData()
        self.assertFalse(fd_obj.update(RESPONSE_ONE))

    def test_06(self):
        """ Direct set/get test """
        fd_obj = FormData()
        fd_obj['ABC'] = {'value': 'hello'}
        self.assertEqual(len(fd_obj.elements), 5)
        self.assertEqual(fd_obj['ABC'], {'value': 'hello'})
        self.assertEqual(fd_obj['__ASYNCPOST'], {'value': 'true'})
        with self.assertRaises(KeyError):
            dummy_val = fd_obj['foo']

    def test_08(self):
        """ Labels test """
        fd_obj = FormData(FORM_FOUR)
        self.assertEqual(len(fd_obj.elements), 12)
        self.assertEqual(len(fd_obj.labels), 6)
        self.assertEqual(fd_obj.value_for_label('Scheme'), "")

