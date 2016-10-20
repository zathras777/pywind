# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

""" To get data from the Ofgem website we need to use one of their web forms. These use
    MS javascript to work and were originally only usable in IE 8 or IE9. Modern versions
    are usable in more browsers but the forms themselves have also evolved and are more
    complex than is ideal.

"""
from __future__ import print_function

import logging
import os
from lxml import etree

try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

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
        OFGEM = 'https://www.renewablesandchp.ofgem.gov.uk'
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
        is_set, upd = self.form_data.set_value_by_label('Page Size', '25')
        if is_set is False:
            return False
        response = self._do_post(True)
        if response is None:
            return False
        if self.form_data.update(response.content) is False:
            self.logger.warning("Submit failed :-(")
            return False

        if self.form_data.export_url is None:
            self.logger.warning("Unable to find the export url. Cannot continue.")
            return False

        export_url = _make_url(self.form_data.export_url) + 'XML'
        response = get_or_post_a_url(export_url, cookies=self.cookies)
        self.raw_data = response.content
        return True

    def save_original(self, filename):
        """ Save the original, downloaded source into the filename provided.

        :param filename: Filename to save the file to.
        :returns: True or False
        :rtype: boolean
        """
        if self.raw_data is None:
            return False
        etree.write(filename, self.raw_data, encoding='utf-8')
        return True

    def set_value(self, lbl, value):
        is_set, cb_rqd = self.form_data.set_value_by_label(lbl, value)
        self.logger.debug("set_value_by_label [%s] -> %s, %s", lbl, is_set, cb_rqd)
        if is_set and cb_rqd:
            return self.update()
        return is_set

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
