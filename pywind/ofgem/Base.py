# coding=utf-8
""" Base module for all Ofgem forms. """
#
# Copyright 2013-2015 david reid <zathrasorama@gmail.com>
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
# pylint: disable=E0611

from __future__ import print_function

import re
import sys
from lxml import etree

import html5lib
from pprint import pprint

import requests

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def set_attr_from_xml(obj, node, attr, name):
    """ Given an object and an xml node, set an attribute on the object from an xml attribute. """
    val = node.get(attr, None)
    if val in [None, '']:
        val = None
    else:
        val = val.strip().encode('utf-8')
        if len(val) == 0:
            val = None
        else:
            # Yes, Ofgem data really did have a station name wrapped in single quotes...
            if val[0] == b"'" and val[-1] == b"'":
                val = val[1:-1]
    setattr(obj, name, val)


def to_string(obj, attr):
    """ This is long winded, but allows for as_string() to work for both Python 2 & 3 """
    val = getattr(obj, attr)
    if val is None:
        return ''
    if isinstance(val, str):
        return val
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, float):
        return "{:.02f}".format(val)
    elif hasattr(val, 'strftime'):
        return val.strftime("%Y-%m-%d")
    return val.decode()


def as_csv(obj, fld):
    """ Return the given field as a value suitable for inclusion in a CSV file for Python 2 or 3 """
    val = getattr(obj, fld)
    if sys.version_info >= (3, 0) and isinstance(val, bytes):
        return val.decode()
    return val


class OfgemField(object):
    """ Class to represent a field on an Ofgem form. """
    def __init__(self, elm=None):
        self.name = None
        self.idd = None
        self.label = None
        self.type = None
        self.value = None
        self.disabled = False
        self.options = []
        self.postback = False
        self.separator = ','
        self.dropdown = None

        if elm is not None:
            self._from_element(elm)

    def _from_element(self, elm):
        """ Update class from an XML element. """
        self.type = elm.get('type')
        self.idd = elm.get('id')
        self.name = elm.get('name')
        if self.type == 'checkbox':
            self.checked = True if elm.get('checked', '') == 'checked' else False
        self.value = elm.get('value')
        self.disabled = elm.get('disabled', '') == 'disabled'

    @property
    def has_options(self):
        """ Does this field have any options? """
        return len(self.options) > 0

    def value_from_list(self, _list):
        """ Set the value to the supplied list. """
        self.value = self.separator.join(_list)

    def set_value(self, what):
        """ Set a value for this field. """
        if self.dropdown is not None:
            return self.dropdown.set_value(what)
        self.value = what
        return True

    def __str__(self):
        return "type {}, id {}, postback {}".format(self.type, self.idd, self.postback)


class SelectOption(object):
    """ Class to represent an option in a select field. """
    def __init__(self, opt):
        self.value = opt.get('value')
        self.selected = opt.get('selected', '') == 'selected'
        self.label = opt.text.replace(u'\u00a0', ' ')

    def __str__(self):
        return "{}: {}".format(self.value, self.label)


class OfgemSelectField(OfgemField):
    """ Class to represent a select field """
    def __init__(self, elm):
        OfgemField.__init__(self, elm=elm)
        self.type = 'select'
        for opt in elm.xpath('./option'):
            self.options.append(SelectOption(opt))
        for opt in self.options:
            if opt.selected:
                self.value = opt.value

    def set_value(self, what):
        """ Set an option on the field. """
        if isinstance(what, int):
            what = "{:02d}".format(what)
        changed = False
        for opt in self.options:
            if opt.label == what:
                if self.value != opt.value:
                    self.value = opt.value
                    changed = True
                opt.selected = True
            else:
                opt.selected = False
        return changed


class OfgemDropdown(object):
    """ Ofgem Dropdown field. """
    def __init__(self, mgr, fld):
        """ The fld should point to the $HiddenIndices field. """
        self.opts = {}
        self.current = []
        self.field = fld
        self.parent = mgr.by_name(fld.name.replace('$divDropDown$ctl01$HiddenIndices', '$txtValue'))
        if self.parent is None:
            return

        if fld.value is not None:
            for val in [int(part) for part in fld.value.split(',')]:
                opt_name = fld.name.replace('ctl01$HiddenIndices', 'ctl{:02d}'.format(val + 2))
                opt_fld = mgr.by_name(opt_name)
                if opt_fld is not None:
                    self.opts[opt_fld.label] = val
                    if opt_fld.checked:
                        self.current.append(opt_fld.label)
        self.parent.dropdown = self
        self._set_value()

    def set_value(self, value):
        """ We expect the val to be one or more of the possible options, i.e. text not indices. """
        self.current = []
        update_rqd = False
        for val in [part.strip() for part in value.split(",")]:
            if val in self.current:
                continue
            update_rqd = True
            if val in self.opts:
                self.current.append(val)
        return self._set_value() if update_rqd else False

    def _set_value(self):
        """ Set the field value """
        if self.parent is None:
            return False
        self.parent.value = ",".join(self.current)
        self.field.value = ",".join([str(self.opts[key]) for key in self.current])
        return True


class OfgemRadioField(OfgemField):
    """ Ofgem Radio Field """
    class RadioOption(object):
        def __init__(self):
            self.value = None
            self.label = None
            self.checked = False

    def __init__(self, elm):
        OfgemField.__init__(self, elm=elm)
        self.type = 'radio'
        self.options = []
        self.add_option(elm)

    def add_option(self, elm):
        """ Add an option to the field. """
        opt = self.RadioOption()
        opt.value = elm.get('value')
        opt.checked = elm.get('checked', '') == 'checked'
        lbls = elm.xpath('../label')
        if len(lbls) > 0:
            opt.label = lbls[0].text
        self.options.append(opt)
        if opt.checked:
            self.value = opt.value


class FieldManager(object):
    """ Class to manage one or more fields. """
    def __init__(self):
        self.names = {}
        self.ids = {}
        self.labels = {}

    def add_or_update(self, fld):
        """ Add or update a field to the manager. """
        if fld.name is not None:
            self.names[fld.name.lower()] = fld
        self.ids[fld.idd] = fld

    # needs renaming...
    def get_or_create(self, name, value=None):
        """ Get a field or create a new one if it doesn't exist. """
        fld = self.by_name(name)
        if fld is not None:
            fld.set_value(value)
            return fld
        node = etree.Element("input", value=value or '', type="hidden", name=name, id=name)
        off = OfgemField(node)
        self.add_or_update(off)
        return off

    def by_id(self, _id):
        """ Get a field by ID """
        return self.ids.get(_id)

    def by_name(self, name):
        """ Get a field by name """
        return self.names.get(name.lower())

    def by_label(self, lbl):
        """ Get a field by a label """
        return self.labels.get(lbl.lower())

    def set_label_by_id(self, lbl, _id):
        """ Set a field lable by its id """
        fld = self.by_id(_id)
        if fld is not None:
            self.labels[lbl.lower()] = fld
            fld.label = lbl.lower()

    def do_postback(self, _id):
        """ Set the postback flag. """
        fld = self.by_id(_id)
        if fld is not None:
            fld.postback = True

    def set_separator(self, _id, sep):
        """ Set the seperator to use. """
        fld = self.by_id(_id)
        if fld is not None:
            fld.separator = sep

    def post_data(self):
        """ Generate the data to post to server, as a string.
            NB quote is used as quote_plus fails.
        """
        post_data = {}
        for fld in self:
            if 'divDropDown$ctl' in fld.name and 'HiddenIndices' not in fld.name:
                continue
            val = fld.value or ''
            if fld.type == 'checkbox':
                # Only checkboxes that are ticked are expected to be posted.
                if fld.value is False:
                    continue
                val = 'on'
#            print("{} => {}".format(fld.name, val))
            post_data[quote(fld.name)] = quote(val)
        print("\n\nDATA to be POSTed")
        pprint(post_data)
        print("\n\n")
        return "&".join(["{}={}".format(key, post_data[key]) for key in post_data.keys()])

    def __iter__(self):
        for name in sorted(self.names):
            yield self.names[name]


class OfgemForm(object):
    """ Class to represent an Ofgem form instance. """
    OFGEM_BASE = 'https://www.renewablesandchp.ofgem.gov.uk/Public/'

    def __init__(self, url):
        """ Create an instance of OfgemForm found at the url provided. """
        if not url.startswith('https'):
            url = self.OFGEM_BASE + url

        requests.packages.urllib3.disable_warnings()

        self.num = 1
        self.url = url
        self.export_url = None
        self.data = None
        self.action = None
        self.cookies = None
        self.fields = FieldManager()
        self._get()

    def set_value(self, lbl, what):
        """ Set a value by field. """
        fld = self.fields.by_label(lbl)
        if fld is None:
            raise Exception("Unknown label '{}'".format(lbl))
        if '$txtValue' in fld.name:
            # Some fields have a checkbox that is set when the field is blank,
            # so as we're setting the value, clear the checkbox.
            cbb = fld.name.replace('$txtValue', '$cbNull')
            cb_obj = self.fields.by_name(cbb)
            if cb_obj is not None:
                cb_obj.value = False

        if fld.set_value(what) is True:
            if fld.postback:
                self._update(fld.name)

    def get_data(self):
        """ Get data from the form. """
        self.set_value('page size', 25)
#        fld = self.fields.by_name("ReportViewer$ctl04$ctl00")
#        fld.value = 'View Report'
        self._update('ReportViewer$ctl04$ctl00')


#https://www.renewablesandchp.ofgem.gov.uk/Reserved.ReportViewerWebControl.axd?
## ReportSession=goiq4h452moinp554b0g1ln0
#&Culture=2057
#&CultureOverrides=True
#&UICulture=2057
#&UICultureOverrides=True
#&ReportStack=1
#&ControlID=81adeb57ee714e19a27f493c3791bd15
#&OpType=Export
#&FileName=CertificatesExternalPublicDataWarehouse
#&ContentDisposition=OnlyHtmlInline
#&Format=XML

        if self.export_url is None:
            return False
        print(self.export_url)
        req = requests.get(self.export_url + 'XML', cookies=self.cookies)
        if req.status_code != 200:
            raise
        self.data = req.content
        return True

    #
    # Private functions
    #
    def _get(self):
        """ Get the form without trying to update it. Used for initial retrieval. """
        try:
            req = requests.get(self.url)
        except requests.exceptions.SSLError as err:
            raise Exception("SSL Error\n  Error: {}\n    URL: {}".
                            format(err.message[0], self.url))
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to the Ofgem server.\nURL: {}".
                            format(self.url))

        self._process_response(req)

    def _update(self, name=''):
        """ Update the form. """
        print("\n_UPDATE!!! {}\n".format(name))
        print(self.action)
        self.fields.get_or_create('__EVENTTARGET', name)
        self.fields.get_or_create('ScriptManager1', "ScriptManager1|{}".format(name))

        form_hdrs = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                     'X-Requested-With': 'XMLHttpRequest',
                     'Referer': self.action}
        try:
            req = requests.post(self.action,
                                cookies=self.cookies,
                                headers=form_hdrs,
                                data=self.fields.post_data())
            if req.url != self.action:
                print("Asked for {}\ngot {}".format(self.action, req.url))
                return

        except requests.exceptions.SSLError as err:
            raise Exception("SSL Error\n  Error: {}\n    URL: {}".
                            format(err.message, self.url))
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ofgem server")

        document = self._process_response(req)

        for nmv in ['__VIEWSTATE', '__EVENTVALIDATION']:
            poss = document.xpath('//input[@name="{}"]'.format(nmv))
            if len(poss) == 1:
                self.fields.get_or_create(nmv, poss[0].get('value'))
            else:
                print("Unable to find {}".format(nmv))

        for scr in document.xpath('//script'):
#            print(scr.text)
            if scr.text is None or 'Sys.Application' not in scr.text:
                continue
            for jss in re.findall(r"Sys.Application.add_init\(function\(\) \{\n(.*)\n\}\);",
                                  scr.text):
#                print(jss)
                xpb = re.search('\"ExportUrlBase\":\"(.*?)\",', jss)
                if xpb is not None:
                    print("EXPORT_URL = {}".format(xpb.group(1)))
                    print(xpb.groups())
                    self.export_url = xpb.group(1)
                    if not self.export_url.startswith('http'):
                        self.export_url = self.OFGEM_BASE + self.export_url

    def _process_response(self, response):
        """ Process a request. """
        print("response:\n  {}\n  status_code = {}".format(response.url, response.status_code))
        if response.status_code != 200:
            raise Exception("Unable to get Ofgem form\nURL: {}\nGot {} but expected a 200".
                            format(self.url, response.status_code))

#        print("content = {}".format(response.content))
        self.cookies = response.cookies
        document = html5lib.parse(response.content,
                                  treebuilder="lxml",
                                  namespaceHTMLElements=False)

        forms = document.xpath('//form')
        if len(forms) == 0:
            raise Exception("No form found in returned data from '{}'".format(self.url))

        print(forms)
        _form = forms[0]
        labels = {}
        self.action = _form.get('action', self.url)
        if self.action.startswith('./'):
            self.action = self.OFGEM_BASE + self.action[2:]
        elif not self.action.startswith('http'):
            self.action = self.OFGEM_BASE + self.action

        for elm in _form.xpath('//tr[@isparameterrow="true"]/td'):
            lbls = elm.xpath('./label')
            if len(lbls) > 0:
                txt = lbls[0].xpath('./span/font')[0].text
                labels[lbls[0].get('for')] = txt.replace(':', '')
                continue

            for inp in elm.xpath('.//input'):
                typ = inp.get('type')
                if typ in [None, 'image']:
                    continue
                if typ == 'radio':
                    o_fld = self.fields.by_name(inp.get('name'))
                    if o_fld is None:
                        o_fld = OfgemRadioField(inp)
                    else:
                        o_fld.add_option(inp)
                else:
                    o_fld = OfgemField(elm=inp)
                self.fields.add_or_update(o_fld)

            for inp in elm.xpath('.//select'):
                o_fld2 = OfgemSelectField(elm=inp)
                self.fields.add_or_update(o_fld2)

        for elm in _form.xpath('//td[@nowrap="nowrap"]'):
            inps = elm.xpath('.//input')
            if len(inps) == 0:
                continue
            o_fld3 = OfgemField(elm=inps[0])
            lbls = elm.xpath('.//label')
            if len(lbls) > 0:
                o_fld3.label = lbls[0].text.replace(u"\u00a0", ' ')
            self.fields.add_or_update(o_fld3)

        for _id in labels:
            self.fields.set_label_by_id(labels[_id], _id)

        for elm in _form.xpath('//input[@type="hidden"]'):
            self.fields.add_or_update(OfgemField(elm=elm))

        for scr in _form.xpath('//script'):
            if scr.text is None or 'Sys.Application' not in scr.text:
                continue
            for jss in re.findall(r"Sys.Application.add_init\(function\(\) \{\n(.*)\n\}\);",
                                  scr.text):
                tid = re.search('\"(DropDownId|TextBoxId|FalseCheckId|NullCheckBoxId)\":\"(.*?)\",',
                                jss)
                if tid is None:
                    continue
                if '"PostBackOnChange":true' in jss:
                    self.fields.do_postback(tid.group(2))
                lss = re.search('\"ListSeparator\":\"(.*?)\",', jss)
                if lss is not None:
                    self.fields.set_separator(tid.group(2), lss.group(1))

        for fld in self.fields:
            if 'HiddenIndices' in fld.name:
                OfgemDropdown(self.fields, fld)

        self.fields.get_or_create('ReportViewer$ctl10', 'ltr')
        self.fields.get_or_create('ReportViewer$ctl11', 'standards')
        self.fields.get_or_create('__ASYNCPOST', 'True')
        self.fields.get_or_create('__EVENTARGUMENT')
        self.fields.get_or_create('__LASTFOCUS')

        return document
