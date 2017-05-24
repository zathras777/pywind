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

"""
Utility functions used by more than one module within pywind.
"""

# pylint: disable=E1101

import sys
import argparse
from datetime import datetime, date
from lxml import etree
import requests


def get_or_post_a_url(url, post=False, **kwargs):
    """
    Use the requests library to either get or post to a specified URL.
    The return code is checked and exceptions raised if there has been
    a redirect or the status code is not 200.

    :param url: The URL to be used.
    :param post: True if the request should be a POST. Default is False which results in a
                 GET request.
    :param kwargs: Optional keyword arguments that are passed directly to the requests call.
    :returns: The requests object is returned if all checks pass.
    :rtype: :class:`requests.Response`
    :raises: Raises :exc:`Exception` for various errors.

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
    """ Parse a string into a date using the YYYY-MM-DD format. Used by the
    :func:`commandline_parser` function.

    :param dtstr: Date string to be parsed
    :returns: Valid date
    :rtype: :class:`datetime.date`
    :raises: :exc:`argparse.ArgumentTypeError` if the date string is not formatted as
             YYYY-MM-DD
    """
    try:
        return datetime.strptime(dtstr, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: '{0}'. Should be in format YYYY-MM-DD".format(dtstr))


def valid_time(dtstr):
    """ Parse a string into a date using the YYYY-MM-DD format. Used by the
    :func:`commandline_parser` function.

    :param dtstr: Date string to be parsed
    :returns: Valid date
    :rtype: :class:`datetime.date`
    :raises: :exc:`argparse.ArgumentTypeError` if the date string is not formatted as
             YYYY-MM-DD
    """
    try:
        return datetime.strptime(dtstr, "%H:%M").time()
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid time: '{0}'. Should be in format HH:MM".format(dtstr))


def commandline_parser(help_text, epilog=None):
    """
    Simple function to create a command line parser with some generic options.

    :param help_text: The script description
    :param epilog: Epilog text
    :returns: Argument parser
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(description=help_text,
                                     epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--debug', action='store_true', help='Enable debugging')
    parser.add_argument('--request-debug', action='store_true',
                        help='Enable debugging of requests')
    parser.add_argument('--log-filename', action='store', help='Filename to write logging to')
    parser.add_argument('--date', type=valid_date, help='Date. (yyyy-mm-dd format)')
    parser.add_argument('--fromdate', type=valid_date, help='Date. (yyyy-mm-dd format)')
    parser.add_argument('--todate', type=valid_date, help='Date. (yyyy-mm-dd format)')
    parser.add_argument('--fromtime', type=valid_time, help='24 hour time. (HH:MM)')
    parser.add_argument('--totime', type=valid_time, help='24 hour time. (HH:MM)')
    parser.add_argument('--unit-type', help='Elexon Unit Type (only one type can be given)')
    parser.add_argument('--year', type=int, help='Year (used for Elexon)')
    parser.add_argument('--month', type=int, help='Month (used for Elexon)')
    parser.add_argument('--period', type=int, help='Period (format is YYYYMM)')
    parser.add_argument('--all-periods', action='store_true', help='Get data for all available periods')
    parser.add_argument('--settlement-period', help='Settlement period (1-50)')
    parser.add_argument('--scheme', choices=['REGO', 'RO'], help='Ofgem Scheme')
    parser.add_argument('--export', choices=['csv', 'xml', 'xlsx'], help='Data Export Format')
    parser.add_argument('--output', help='Export filename')
    parser.add_argument('--input', help='Filename to parse')
    parser.add_argument('--save', action='store_true',
                        help='Save downloaded file in original format')
    parser.add_argument('--original', help='Filename for original format file (use with --save)')
    parser.add_argument('--station', help='Station name to filter for (Ofgem only)')
    parser.add_argument('--apikey', default='elexon.api.key', help='API Key (Elexon only)')
    parser.add_argument('-v', '--version', action='store_true', help='Show version number')
    return parser


def args_get_datetime(args):
    if args.fromdate and args.fromtime:
        args.fromdatetime = datetime.combine(args.fromdate, args.fromtime)
    else:
        args.fromdatetime = None
    if args.todate and args.totime:
        args.todatetime = datetime.combine(args.todate, args.totime)
    else:
        args.todatetime = None


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
    Given the level of nested data contained in some of the results, this function
    performs an iterative get.

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


def xml_attr_or_element(xml_node, name):
    """ Attempt to get the value of name from the xml_node. This could be an attribute or
        a child element.
    """
    attr_val = xml_node.get(name, None)
    if attr_val is not None:
        return attr_val.encode('utf-8').strip()
    for child in xml_node.getchildren():
        if child.tag == name:
            return child.text.encode('utf-8').strip()
    return None


def map_xml_to_dict(xml_node, mapping=None):
    """
    Given an XML node, create a dict using the mapping of attributes/elements supplied.

    The format of each mapping item is a tuple of up to 3 components,
        - xml attribute
        - key for dict (optional)
        - type of data expected (optional)
        - default value for the mapping

    If the key name is not supplied, the lower cased xml attribute will be used.
    If the type is not given it will be assumed to be a string.

    :param xml_node: The XML node to parse
    :param mapping: Iterable of xml element
    :returns: Dict of successfully extracted data
    :rtype: dict
    """
    rv_dict = {}

    if mapping is None:
        for child in xml_node.iterchildren():
            key = child.tag.lower()
            val = _convert_type(child.text.strip().encode('utf-8'), 'str')
            if len(val) == 0:
                val = None
            rv_dict[key] = val
    else:
        for mapp in mapping:
            if isinstance(mapp, (list, set, tuple)):
                xml_name = mapp[0]
                dict_key = mapp[1] if len(mapp) > 1 and mapp[1] != '' else None
                data_typ = mapp[2] if len(mapp) > 2 and mapp[2] != '' else None
                dflt = mapp[3] if len(mapp) > 3 else None
            else:
                xml_name = mapp
                dict_key = None
                data_typ = None
                dflt = None

            val = xml_attr_or_element(xml_node, xml_name)
            dict_key = dict_key or xml_name.lower()
            if val is not None:
                if len(val) == 0:
                    val = dflt
                else:
                    val = _convert_type(val, data_typ or 'str')
            rv_dict[dict_key] = val
    return rv_dict


def _convert_type(val, typ):
    """ Helper function for :func:`map_xml_to_dict` to convert strings to correct type.
    If the conversion cannot be made will raise a ValueError exception.

    :param val: The string value to convert
    :param typ: The type to convert the string into.
    :return: Converted value
    :raises: ValueError
    """
    if sys.version_info >= (3, 0) and isinstance(val, bytes):
        val = val.decode()
    if typ in ['int', 'float'] and isinstance(val, str):
        val = val.replace(',', '')
    if typ == 'int':
        return int(val)
    elif typ == 'float':
        try:
            return float(val)
        except ValueError:
            return 0.0
    elif typ == 'date':
        # Incredibly Ofgem has several places where there are newlines in dates!
        if '\n' in val:
            val = val.split(b"\n")[0]
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%dT%H:%M:00']:
            try:
                if sys.version_info >= (3, 0):
                    return datetime.strptime(val, fmt).date()
                else:
                    return datetime.strptime(val.decode(), fmt).date()
            except ValueError:
                pass
        raise ValueError("Unable to parse date {}".format(val))
    elif typ == 'bool':
        if str(val).lower() in ['1', 'yes', 'y', 'true']:
            return True
        return False
    elif typ == 'address':
#        print(val)
#        print(type(val))
#        if sys.version_info < (3, 0):
#            return val.replace('\r', ', ')
        return val.replace('\r', ', ')
    elif typ == 'period':
        # Convert 201601 to 01-01-2016
        yyr = val / 100
        mon = val - yyr * 100
        return date(yyr, mon, 1)

    elif typ == 'str':
        if val[0] == "'" and val[-1] == "'":
            val = val[1:-1]
    return str(val)


class StdoutFormatter(object):
    """
    Small class to provide easier printing to stdout.

    .. code::

       >>> from pywind.utils import StdoutFormatter
       >>> sof = StdoutFormatter("5s", "6s", ">10s")
       >>> sof.titles("Hello", "World", "right")
         Hello  World        right
         -----  ------  ----------
       >>> sof.row("first", "row", "right")
         first  row          right

    .. note::

      The format detection doesn't allow all options :-( "10,d" is not yet supported.

    """
    def __init__(self, *args, **kwargs):
        self.columns = []
        for arg in args:
            ssz = arg[:-1] if arg[0].isdigit() else arg[1:-1]
            fmt = [arg[0] if not arg[0].isdigit() else '',
                   int(ssz) if arg[-1] != 'f' else float(ssz),
                   arg[-1],
                   int(ssz) if arg[-1] != 'f' else int(ssz.split('.')[0])]
            self.columns.append(fmt)
        self.spaces = kwargs.get('spaces', "  ")

    def formatter(self, titles=False):
        """ Return the format string for the columns configured.

        :param titles: True if the format will be used for titles (all strings)
        :returns: Format string
        :rtype: str
        """
        fmts = []
        for col in self.columns:
            ssz = col[1] if titles is False else col[3]
            fmts.append("{{:{}{}{}}}".format(col[0], ssz, col[2] if titles is False else 's'))
        return self.spaces + self.spaces.join(fmts)

    def titles(self, *args):
        """ Generate the title string block.

        :param args: List of titles to use. Should be at least as long as the number of columns
        :returns: Formatted title string
        :rtype: str
        """
        if len(args) < len(self.columns):
            raise AttributeError("Incorrect number of titles supplied. Should have {}, got {}".
                                 format(len(self.columns), len(args)))
        fmt = self.formatter(True)
        return fmt.format(*args) + "\n" + \
               fmt.format(*['-' * col[3] for col in self.columns])

    def row(self, *args):
        """ Use the column format to generate a string. This tries to truncate long strings.

        :param args: The column values.
        :returns: Formatted string using args
        :rtype: str
        """
        vals = []
        col = 0
        for arg in args:
            if self.columns[col][2] == 's' and len(arg) > self.columns[col][3]:
                vals.append(arg[:self.columns[col][3] - 3] + '...')
            else:
                vals.append(arg)
            col += 1
        return self.formatter().format(*vals)
