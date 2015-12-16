# coding=utf-8
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
import html5lib
import re
import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import sys

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def set_attr_from_xml(obj, node, attr, name):
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
    if type(val) is str:
        return val
    elif type(val) is int:
        return str(val)
    elif type(val) is float:
        return "{:.02f}".format(val)
    elif hasattr(val, 'strftime'):
        return val.strftime("%Y-%m-%d")
    return val.decode()


def as_csv(obj, f):
    """ Return the given field as a value suitable for inclusion in a CSV file for Python 2 or 3 """
    val = getattr(obj, f)
    if sys.version_info >= (3, 0) and type(val) is bytes:
        return val.decode()
    return val


def as_csv_title(m):
    return (m[0] if len(m) == 1 else m[1]).capitalize().replace('_', ' ')


class OfgemField(object):
    def __init__(self, el=None):
        self.name = None
        self.id = None
        self.label = None
        self.type = None
        self.value = None
        self.disabled = False
        self.options = []
        self.postback = False
        self.separator = ','
        self.dropdown = None

        if el is not None:
            self._from_element(el)

    def _from_element(self, el):
        self.type = el.get('type')
        self.id = el.get('id')
        self.name = el.get('name')
        if self.type == 'checkbox':
            self.checked = True if el.get('checked', '') == 'checked' else False
        self.value = el.get('value')
        self.disabled = el.get('disabled', '') == 'disabled'

    @property
    def has_options(self):
        return len(self.options) > 0

    def value_from_list(self, _list):
        self.value = self.separator.join(_list)

    def set_value(self, what):
        if self.has_options:
            self.set_option(what)
        elif self.dropdown is not None:
            self.dropdown.set_value(what)
        else:
            self.value = what

    def __str__(self):
        return "type {}, id {}, postback {}".format(self.type, self.id, self.postback)


class SelectOption(object):
    def __init__(self, opt):
        self.value = opt.get('value')
        self.selected = opt.get('selected', '') == 'selected'
        self.label = opt.text.replace(u'\u00a0', ' ')

    def __str__(self):
        return "{}: {}".format(self.value, self.label)


class OfgemSelectField(OfgemField):
    def __init__(self, el):
        OfgemField.__init__(self, el=el)
        self.type = 'select'
        for opt in el.xpath('./option'):
            self.options.append(SelectOption(opt))
        for opt in self.options:
            if opt.selected:
                self.value = opt.value

    def set_option(self, what):
        if type(what) is int:
            if what < 10:
                what = "{:02d}".format(what)
            else:
                what = "{}".format(what)
        for opt in self.options:
            if opt.label == what:
                self.value = opt.value
                opt.selected = True
            else:
                opt.selected = False


class OfgemDropdown(object):
    def __init__(self, mgr, fld):
        """ The fld should point to the $HiddenIndices field. """
        self.opts = {}
        self.current = []
        self.field = fld
        self.parent = mgr.by_name(fld.name.replace('$divDropDown$ctl01$HiddenIndices', '$txtValue'))
        if self.parent is None:
            return

        if fld.value is not None:
            for i in [int(x) for x in fld.value.split(',')]:
                opt_name = fld.name.replace('ctl01$HiddenIndices', 'ctl{:02d}'.format(i + 2))
                opt_fld = mgr.by_name(opt_name)
                if opt_fld is not None:
                    self.opts[opt_fld.label] = i
                    if opt_fld.checked:
                        self.current.append(opt_fld.label)
        self.parent.dropdown = self
        self._set_value()

    def set_value(self, val):
        """ We expect the val to be one or more of the possible options, i.e. text not indices. """
        self.current = []
        for v in [x.strip() for x in val.split(",")]:
            if v in self.opts:
                self.current.append(v)
        self._set_value()

    def _set_value(self):
        if self.parent is None:
            return
        self.parent.value = ",".join(self.current)
        self.field.value = ",".join([str(self.opts[v]) for v in self.current])


class OfgemRadioField(OfgemField):
    class RadioOption(object):
        def __init__(self):
            self.value = None
            self.label = None
            self.checked = False

    def __init__(self, el):
        OfgemField.__init__(self, el=el)
        self.type = 'radio'
        self.options = []
        self.add_option(el)

    def add_option(self, el):
        opt = self.RadioOption()
        opt.value = el.get('value')
        opt.checked = el.get('checked', '') == 'checked'
        lbls = el.xpath('../label')
        if len(lbls) > 0:
            opt.label = lbls[0].text
        self.options.append(opt)
        if opt.checked:
            self.value = opt.value


class FieldManager(object):
    def __init__(self):
        self.names = {}
        self.ids = {}
        self.labels = {}

    def add_or_update(self, fld):
        if fld.name is not None:
            self.names[fld.name.lower()] = fld
        self.ids[fld.id] = fld

    # needs renaming...
    def get_or_create(self, name, value=None):
        fld = self.by_name(name)
        if fld is not None:
            if fld is not None:
                fld.set_value(value)
            return fld
        node = etree.Element("input", value=value or '', type="hidden", name=name, id=name)
        of = OfgemField(node)
        self.add_or_update(of)
        return of

    def by_id(self, _id):
        return self.ids.get(_id)

    def by_name(self, nm):
        return self.names.get(nm.lower())

    def by_label(self, lbl):
        return self.labels.get(lbl.lower())

    def set_label_by_id(self, lbl, _id):
        fld = self.by_id(_id)
        if fld is not None:
            self.labels[lbl.lower()] = fld
            fld.label = lbl.lower()

    def do_postback(self, _id):
        fld = self.by_id(_id)
        if fld is not None:
            fld.postback = True

    def set_separator(self, _id, sep):
        fld = self.by_id(_id)
        if fld is not None:
            fld.separator = sep

    def post_data(self):
        """ Generate the data to post to server, as a string.
            NB quote is used as quote_plus fails.
        """
        p_d = []
        for f in self:
            if 'divDropDown$ctl' in f.name and 'HiddenIndices' not in f.name:
                continue
            val = f.value or ''
            if f.type == 'checkbox':
                # Only checkboxes that are ticked are expected to be posted.
                if f.value is False:
                    continue
                val = 'on'
            p_d.append("{}={}".format(quote(f.name), quote(val)))
        return "&".join(p_d)

    def __iter__(self):
        for nm in sorted(self.names):
            yield self.names[nm]


class TLSv1Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class OfgemForm(object):
    OFGEM_BASE = 'https://www.renewablesandchp.ofgem.gov.uk/Public/'

    def __init__(self, url):
        """ Create an instance of OfgemForm found at the url provided. """
        if not url.startswith('http'):
            url = self.OFGEM_BASE + url

        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.mount('https://', TLSv1Adapter())

        self.n = 1
        self.url = url
        self.export_url = None
        self.data = None
        self.action = None
        self.cookies = None
        self.fields = FieldManager()
        self._get()

    def set_value(self, lbl, what):
        fld = self.fields.by_label(lbl)
        if fld is None:
            raise Exception("Unknown label '{}'".format(lbl))

        if '$txtValue' in fld.name:
            # Some fields have a checkbox that is set when the field is blank,
            # so as we're setting the value, clear the checkbox.
            cb = fld.name.replace('$txtValue', '$cbNull')
            cb_obj = self.fields.by_name(cb)
            if cb_obj is not None:
                cb_obj.value = False

        fld.set_value(what)

        if fld.postback:
            self._update(fld.name)

    def get_data(self):
        self.set_value('page size', 25)
        self._update('ReportViewer$ctl04$ctl00')

        if self.export_url is None:
            return False
        r = self.session.get(self.export_url + 'XML', cookies=self.cookies)
        if r.status_code != 200:
            raise
        self.data = r.content
        return True

    #
    # Private functions
    #
    def _get(self):
        """ Get the form without trying to update it. Used for initial retrieval. """
        try:
            r = self.session.get(self.url)
        except requests.exceptions.SSLError as e:
            raise Exception("SSL Error\n  Error: {}\n    URL: {}".format(e.message[0], self.url))
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to the Ofgem server.\nURL: {}".format(self.url))

        self._process_response(r)

    def _update(self, name=''):
        self.fields.get_or_create('__EVENTTARGET', name)
        self.fields.get_or_create('ScriptManager1', "ScriptManager1|{}".format(name))

        try:
            r = self.session.post(self.action,
                                  cookies=self.cookies,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                  data=self.fields.post_data())
        except requests.exceptions.SSLError as e:
            raise Exception("SSL Error\n  Error: {}\n    URL: {}".format(e.message, self.url))
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ofgem server")

        document = self._process_response(r)

        for nm in ['__VIEWSTATE', '__EVENTVALIDATION']:
            poss = document.xpath('//input[@name="{}"]'.format(nm))
            if len(poss) == 1:
                self.fields.get_or_create(nm, poss[0].get('value'))

        for scr in document.xpath('//script'):
            if scr.text is None or 'Sys.Application' not in scr.text:
                continue
            for js in re.findall(r"Sys.Application.add_init\(function\(\) \{\n(.*)\n\}\);", scr.text):
                xpb = re.search('\"ExportUrlBase\":\"(.*?)\",', js)
                if xpb is not None:
                    self.export_url = xpb.group(1)
                    if not self.export_url.startswith('http'):
                        self.export_url = self.OFGEM_BASE + self.export_url

    def _process_response(self, response):
        if response.status_code != 200:
            raise Exception("Unable to get the Ofgem form from '{}'\nGot {} expected a 200".format(self.url, response.status_code))

        self.cookies = response.cookies
        document = html5lib.parse(response.content,
                                  treebuilder="lxml",
                                  namespaceHTMLElements=False)

        forms = document.xpath('//form')
        if len(forms) == 0:
            raise Exception("No form found in returned data from '{}'".format(self.url))

        _form = forms[0]
        labels = {}
        self.action = _form.get('action', self.url)
        if not self.action.startswith('http'):
            self.action = self.OFGEM_BASE + self.action

        for el in _form.xpath('//tr[@isparameterrow="true"]/td'):
            lbls = el.xpath('./label')
            if len(lbls) > 0:
                txt = lbls[0].xpath('./span/font')[0].text
                labels[lbls[0].get('for')] = txt.replace(':', '')
                continue

            for inp in el.xpath('.//input'):
                t = inp.get('type')
                if t in [None, 'image']:
                    continue
                if t == 'radio':
                    o_fld = self.fields.by_name(inp.get('name'))
                    if o_fld is None:
                        o_fld = OfgemRadioField(inp)
                    else:
                        o_fld.add_option(inp)
                else:
                    o_fld = OfgemField(el=inp)
                self.fields.add_or_update(o_fld)

            for inp in el.xpath('.//select'):
                o_fld = OfgemSelectField(el=inp)
                self.fields.add_or_update(o_fld)

        for el in _form.xpath('//td[@nowrap="nowrap"]'):
            inps = el.xpath('.//input')
            if len(inps) == 0:
                continue
            o_fld = OfgemField(el=inps[0])
            lbls = el.xpath('.//label')
            if len(lbls) > 0:
                o_fld.label = lbls[0].text.replace(u"\u00a0", ' ')
            self.fields.add_or_update(o_fld)

        for _id in labels:
            self.fields.set_label_by_id(labels[_id], _id)

        for el in _form.xpath('//input[@type="hidden"]'):
            self.fields.add_or_update(OfgemField(el=el))

        for scr in _form.xpath('//script'):
            if scr.text is None or 'Sys.Application' not in scr.text:
                continue
            for js in re.findall(r"Sys.Application.add_init\(function\(\) \{\n(.*)\n\}\);", scr.text):
                tid = re.search('\"(DropDownId|TextBoxId|FalseCheckId|NullCheckBoxId)\":\"(.*?)\",', js)
                if tid is None:
                    continue
                if '"PostBackOnChange":true' in js:
                    self.fields.do_postback(tid.group(2))
                ls = re.search('\"ListSeparator\":\"(.*?)\",', js)
                if ls is not None:
                    self.fields.set_separator(tid.group(2), ls.group(1))

        for fld in self.fields:
            if 'HiddenIndices' in fld.name:
                OfgemDropdown(self.fields, fld)

        self.fields.get_or_create('ReportViewer$ctl10', 'ltr')
        self.fields.get_or_create('ReportViewer$ctl11', 'standards')
        self.fields.get_or_create('__ASYNCPOST', 'True')
        self.fields.get_or_create('__EVENTARGUMENT')
        self.fields.get_or_create('__LASTFOCUS')

        return document
