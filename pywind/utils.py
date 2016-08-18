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
    parser.add_argument('--period', type=int, help='Period (format is YYYYMM)')
    parser.add_argument('--scheme', choices=['REGO', 'RO'], help='Ofgem Scheme')
    parser.add_argument('--output', help='Export filename')
    parser.add_argument('--format', choices=['csv', 'xml'], help='Data Export Format')
    parser.add_argument('--input', help='Filename to parse')
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


def map_xml_to_dict(xml_node, mapping):
    """
    Given an XML node, create a dict using the mapping of attributes/elements supplied.

    The format of each mapping item is a tuple of up to 3 components,
        - xml attribute
        - key for dict (optional)
        - type of data expected (optional)

    If the key name is not supplied, the lower cased xml attribute will be used.
    If the type is not given it will be assumed to be a string.

    :param xml_node: The XML node to parse
    :param mapping: Iterable of xml element
    :returns: Dict of successfully extracted data
    :rtype: dict
    """
    rv_dict = {}
    for map in mapping:
        val = xml_node.get(map[0], None)
        key = map[1] if len(map) > 1 and map[1] != '' else map[0].lower()
        if val is not None:
            val = val.strip().encode('utf-8')
            if len(val) == 0 or val == 'N/A':
                val = None if len(map) < 4 else map[3]
            else:
                typ = map[2] if len(map) > 2 and map[2] != '' else 'str'
                try:
                    val = _convert_type(val, typ)
                except ValueError:
                    print("Unable to convert {} into a {} from XML attribute {} [{}]".format(
                        val, typ, map[0], key
                    ))
        rv_dict[key] = val
    return rv_dict


def _convert_type(val, typ):
    """ Helper function for :func:`map_xml_to_dict` to convert strings to correct type.
    If the conversion cannot be made will raise a ValueError exception.

    :param val: The string value to convert
    :param typ: The type to convert the string into.
    :return: Converted value
    :raises: ValueError
    """
    if typ == 'int':
        return int(val)
    elif typ == 'float':
        return float(val)
    elif typ == 'date':
        # Incredibly Ofgem has several places where there are newlines in dates!
        if b'\n' in val:
            val = val.split(b"\n")[0]
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%dT%H:%M:00']:
            try:
                return datetime.strptime(val.decode(), fmt).date()
            except ValueError:
                pass
        raise ValueError("Unable to parse date {}".format(val))
    elif typ == 'str':
        if val[0] == b"'" and val[-1] == b"'":
            val = val[1:-1]

    return val
