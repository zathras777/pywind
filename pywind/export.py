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

# pylint: disable=E1101

""" Export functions for command line app. """

import csv
import os
import sys

from datetime import date
from pprint import pprint
from lxml import etree
import xlwt


def export_to_file(args, obj):
    """ Export a pywind object to a file based on command line arguments.
    The object supplied can be exported as CSV, XLSX or XML depending on the args.format
    option supplied.

    :param args: Command line args from :func:`argparse.parse_args`
    :param obj: The pywind object to export.
    """
    fmt = (args.export or 'xml').lower()
    if fmt.lower() not in ['xml', 'csv', 'xlsx']:
        print("Format must be xml, xlsx or csv, not {}".format(fmt))
        sys.exit(0)
    if args.output is None:
        fnn = obj.__class__.__name__
        fnn = fnn.lower() + '.' + fmt
    else:
        fnn = os.path.realpath(args.output)

    if os.path.exists(fnn):
        extra = 0
        ck_fn = fnn
        while os.path.exists(ck_fn):
            base, ext = os.path.splitext(fnn)
            ck_fn = base + '_{}'.format(extra) + ext
            extra += 1
        fnn = ck_fn

    if args.output is None or args.output not in fnn:
        print("Output will be saved in {}".format(fnn))

    export_fn = '_export_{}'.format(fmt)
    if export_fn not in globals():
        print("Unable to export to format {}".format(fmt))
        sys.exit(0)
    if globals()[export_fn](obj, fnn) is False:
        print("There was an error writing the file '{}'.".format(fnn))
        return False
    print("{} export to {} completed".format(fmt.upper(), fnn))
    return True


def _make_xml_string(val):
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    val = val.replace('(', '').replace(')', '').replace('/', '_')

    if sys.version_info >= (3, 0):
        return val
    return val.decode('utf-8')


def _export_xml(obj, filename):
    root = etree.Element(obj.__class__.__name__)

    def _walk_dict(node, data_dict):
        if isinstance(data_dict, dict):
            for attr in data_dict.keys():
                if data_dict[attr] is None:
                    continue
                if attr.startswith('@'):
                    node.attrib[_make_xml_string(attr[1:])] = _make_xml_string(data_dict[attr])
                else:
                    new_node = etree.Element(attr)
                    _walk_dict(new_node, data_dict[attr])
                    node.append(new_node)
        else:
            node.text = data_dict

    for info in obj.rows():
        for key in info.keys():
            node_data = info[key]
            node = etree.Element(key)
            _walk_dict(node, node_data)
            root.append(node)

    etree.ElementTree(root).write(filename, pretty_print=True)
    return True


def _order(info):
    """ Create the order and titles for CSV export from an information dict. """
    rv_list = [(0, 'Record Type')]
    for key in info.keys():
        key_title = key[1:] if key.startswith('@') else key
        title = " ".join([part.title() for part in key_title.split('_')])
        rv_list.append((key, title))
    return rv_list


def _export_csv(obj, filename):
    """ Export as CSV.

    .. todo::Doesn't handle sub rows.
    """
    order = []
    with open(filename, 'wt') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        rownum = 0
        for info in obj.rows():
            for key in info.keys():
                data_dict = info[key]
                if rownum == 0:
                    order = _order(data_dict)
                    csvwriter.writerow([col[1] for col in order])
                cols = [key]
                for col in order[1:]:
                    cols.append(data_dict[col[0]] or '')
                csvwriter.writerow(cols)
                rownum += 1
        print("Total of {} data rows written".format(rownum))

    return True


def _export_xlsx(obj, filename):
    """ Export as XLSX file.

    Top level keys are regarded as sheet names.
    :param obj: The object that is being exported.
    :param filename: The filename to export to.
    :returns: True or False
    :rtype: bool
    """
    int_style = xlwt.easyxf(num_format_str='#,##0')
    float_style = xlwt.easyxf(num_format_str='#,##0.00')
    date_style = xlwt.easyxf(num_format_str='yyyy-mm-dd')

    wbb = xlwt.Workbook(encoding='utf-8')
    sheets = {}

    for info in obj.rows():
        for key in info.keys():
            if key not in sheets:
                sheets[key] = [wbb.add_sheet(key), 0]
            sht = sheets[key]
            if len(sht) == 2:
                sht.append(_order(info[key]))
                col = 0
                for title in sht[2][1:]:
                    sht[0].write(0, col, title[1])
                    col += 1
                sht[1] += 1
            info_data = info[key]

            colnum = 0
            for col in sht[2][1:]:
                val = info_data[col[0]]
                style = None
                if isinstance(val, date):
                    style = date_style
                elif isinstance(val, int):
                    style = int_style
                elif isinstance(val, float):
                    style = float_style
                if style is not None:
                    sht[0].write(sht[1], colnum, val, style)
                else:
                    sht[0].write(sht[1], colnum, val)

                colnum += 1
            sht[1] += 1

    wbb.save(filename)
