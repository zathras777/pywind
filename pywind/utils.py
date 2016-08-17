# coding=utf-8
"""
Utility functions used by more than one module within pywind.
"""
#
# Copyright 2013-2016 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# pylint: disable=E1101

import argparse
from datetime import datetime
from lxml import etree

import requests


def get_or_post_a_url(url, post=False, **kwargs):
    """
    Use the requests library to either get or post to a specified URL. The return code is checked
    and exceptions raised if there has been a redirect or the status code is not 200.

    :param url: The URL to be used.
    :param post: True if the request should be a POST. Default is False which results in a GET request.
    :param kwargs: Optional keyword arguments that are passed directly to the requests call.
    :returns: The requests object is returned if all checks pass.
    :rtype: Request
    :raises: Raises :class:`Exception` for various errors.

    .. :note:: Normally the returned URL is compared with the URL requested. In cases \
    where this may change using the :param:ignore_url_check=True parameter will avoid this \
    check. It will not be passed to requests.

    Example

    .. :code:: python

    >>> from pywind.utils import get_or_post_a_url
    >>> qry = {'q': 'rst document formatting'}
    >>> response = get_or_post_a_url('http://www.google.com/search', params=qry)
    >>> response.content
    ...

    """
    ignore_req_check = kwargs.pop('ignore_url_check', False)

    try:
        if post:
            req = requests.post(url, **kwargs)
        else:
            req = requests.get(url, **kwargs)
    except requests.exceptions.SSLError as err:
        raise Exception("SSL Error\n  Error: {}\n    URL: {}".
                        format(err.message[0], url))
    except requests.exceptions.ConnectionError:
        raise Exception("Unable to connect to the server.\nURL: {}".
                        format(url))
    if req.status_code != 200:
        raise Exception("Request was completed, but status code is not 200.\n"+
                        "URL: {}\nStatus Code: {}".format(url, req.status_code))

    if ignore_req_check is False and req.url != url:
        if 'params' not in kwargs or not req.url.startswith(url):
            raise Exception("Returned URL was from a different URL than requested.\n" +
                            "Requested: {}\nActual:  {}".format(url, req.url))
    return req


def valid_date(dtstr):
    """ Parse a string into a date using the YYYY-MM-DD format. Used by the :func:`commandline_parser` function.

    :param dtstr: Date string to be parsed
    :returns: datetime.date object
    :raises: :mod:`argparse.ArgumentTypeError` if the date string is not formatted as YYYY-MM-DD
    """
    try:
        return datetime.strptime(dtstr, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: '{0}'.".format(s))


def commandline_parser(help_text):
    """
    Simple function to create a command line parser with some generic options.

    :param help_text: The script description
    :returns: An ArgumentParser object
    """
    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument('--debug', action='store_true', help='Enable debugging')
    parser.add_argument('--request-debug', action='store_true', help='Enable debugging of requests')
    parser.add_argument('--log-filename', action='store', help='Filename to write logging to')
    parser.add_argument('--date', type=valid_date, help='Date. (yyyy-mm-dd format)')

    return parser


def parse_response_as_xml(request):
    """Given a the response object from requests, attempt to parse it's contents as XML.

    :param request: The requests object
    :returns: The root XML node or None if there is a parser error

    .. note::
      - Nov 2014 Using parser with recover=True was the suggestion of energynumbers

    """
    try:
        parser = etree.XMLParser(recover=True)
        return etree.XML(request.content, parser).getroottree()
    except etree.XMLSyntaxError:
        return None


def multi_level_get(the_dict, key, default=None):
    """
    Given the level of nested data contained in some of the results, this function performs an iterative get.

    :param the_dict: The multi-level dict to get the key from.
    :param key: The key to look for, with each level separated by '.'
    :param default: The default to return if the key is not found. (None if not supplied)
    :returns: The value of the key or default if key does not exist in the dict.
    """
    if not isinstance(the_dict, dict):
        return default
    lvls = key.split('.')
    here = the_dict
    for lvl in lvls[:-1]:
        if lvl in here:
            here = here[lvl]
        else:
            return default
        if not isinstance(here, dict):
            return default

    return here.get(lvls[-1], default)

