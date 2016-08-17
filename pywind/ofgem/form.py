""" To get data from the Ofgem website we need to use one of their web forms. These use
    MS javascript to work and were originally only usable in IE 8 or IE9. Modern versions
    are usable in more browsers but the forms themselves have also evolved and are more
    complex than is ideal.

"""
from __future__ import print_function

import logging
import os
from pprint import pprint
from urllib import unquote

from pywind.log import setup_logging
from pywind.ofgem.form_data import FormData
from pywind.utils import get_or_post_a_url


def _make_url(url, public=True):
    OFGEM = 'https://www.renewablesandchp.ofgem.gov.uk'
    if url.startswith('http'):
        return url

    if url.startswith('/'):
        return os.path.join(OFGEM, url[1:])

    if url.startswith('./'):
        url = url[2:]
    if public is True:
        return os.path.join(OFGEM, 'Public', url)
    return os.path.join(OFGEM, url)


class OfgemForm(object):
    """ Class to represent an instance of an Ofgem form. """

    def __init__(self, url):
        self.start_url = _make_url(url)
        self.cookies = None
        self.action_url = None
        self.form_data = None
        self.export_url = None
        self.raw_data = None
        self.logger = logging.getLogger(__name__)

    def get(self):
        """ Attempt to get the initial version of the form from the website. """
        if self.cookies is None:
            get_or_post_a_url(_make_url('Default.aspx', False))
            response = get_or_post_a_url(_make_url('ReportManager.aspx?ReportVisibility=1&ReportCategory=0'))
            self.cookies = {'ASP.NET_SessionId': response.cookies.get('ASP.NET_SessionId')}

        response = get_or_post_a_url(self.start_url, cookies=self.cookies)
        self.form_data = FormData(response.content)
        if self.action_url is None:
            self.action_url = _make_url(self.form_data.action)
        return True

    def update(self):
        """ Submit the form data and update based on response.
            Given how slow the parsing of a 3M HTML page is, try and use the
            X-MicrosoftAjax: Delta=true header to get smaller blocks for processing.
        """
        response = self._do_post()
        if response is None:
            return False
        return self.form_data.update(response.content)

    def submit(self):
        """ Submit the form data and update based on response.
            Given how slow the parsing of a 3M HTML page is, try and use the
            X-MicrosoftAjax: Delta=true header to get smaller blocks for processing.
        """
        self.form_data.set_value_by_label('Page Size', 25)
        response = self._do_post(True)
        if response is None:
            return False
        if self.form_data.update(response.content) is False:
            self.logger.warning("Submit failed :-(")
            return False
        print(self.form_data.export_url)
        if self.form_data.export_url is None:
            self.logger.warning("Unable to find the export url. Cannot continue.")
            return False
        export_url = _make_url(self.form_data.export_url) + 'XML'
        response = get_or_post_a_url(export_url, cookies=self.cookies)
        self.raw_data = response.content
        return True



    def set_value(self, lbl, value):
        is_set, cb_rqd = self.form_data.set_value_by_label(lbl, value)
        self.logger.info("set_value_by_label -> %s, %s", is_set, cb_rqd)
        if is_set and cb_rqd:
            return self.update()
        return is_set

    def export_data(self, formt='XML'):
        """ Try and get the export data in the requested format. """
        pass

    def _do_post(self, submit=False):
        """ Submit the form data and update based on response.
            Given how slow the parsing of a 3M HTML page is, try and use the
            X-MicrosoftAjax: Delta=true header to get smaller blocks for processing.
        """
        if self.form_data.action is None:
            self.logger.info("Unable to post due no action URL available. Did you call get()?")
            return None

        action_url = _make_url(self.form_data.action)
        form_hdrs = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                     'User-Agent': 'Mozilla',
                     'X-Requested-With': 'XMLHttpRequest',
                     'X-MicrosoftAjax': 'Delta=true',
                     'Referer': unquote(action_url)
                     }
        post_dict = self.form_data.as_post_data(submit=submit)
        post_data = "&".join(["{}={}".format(key, post_dict[key]) for key in post_dict.keys()])

        response = get_or_post_a_url(action_url,
                                     post=True,
                                     cookies=self.cookies,
                                     headers=form_hdrs,
                                     data=post_data)
        return response


def main():
    START_URL = 'ReportViewer.aspx?ReportPath=/DatawarehouseReports/' + \
                'CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2'

    setup_logging(True)
    off = OfgemForm(START_URL)
    if off.get() is False:
        print("Failed to get form")

    print("setting year to...")
    if off.set_value("Output Period \"Year To\"", "2016") is False:
        print("Failed")
        return
    print("setting month from...")
    if off.set_value("Output Period \"Month From\"", "Mar") is False:
        print("Failed")
        return
    print("setting month to...")
    if off.set_value("Output Period \"Month To\"", "Apr") is False:
        print("Failed")
        return
    print("submit = {}".format(off.submit()))


#main()
