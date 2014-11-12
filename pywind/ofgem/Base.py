# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
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

import re
import urllib
import urllib2
import cookielib
import html5lib
from lxml import etree


def get_and_set_from_xml(obj, element, attrs=[]):
    for a in attrs:
        val = element.get(a, None)
        if val is not None and val.isdigit():
            val = int(val)
        setattr(obj, a, val)


class OfgemField(object):
    def __init__(self, el):
        self.options = []
        self.label = ''
        self.tag = el.tag
        self.postback = False
        get_and_set_from_xml(self, el, ['id', 'name', 'type',
                                        'checked', 'value',
                                        'selected'])
#        if self.value is not None and self.value.isdigit():
#            self.value = int(self.value)
        oc = el.get('onclick')
        if oc is not None:
            if 'SetAutoPostBackOnHide' in oc:
                self.postback = True
            if 'MultiValidValuesSelectAll' in oc:
                self.setall = True

    def set_postback_flag(self):
        for o in self.options:
            if o.postback is True:
                self.postback = True
                break

    def raw_value(self):
        if self.tag == 'option':
            if self.selected is None or self.selected is False:
                return self.value
            else:
                return "%s SELECTED" % self.value
        if self.type == 'checkbox':
            return "%s" % "CHECKED" if self.checked else False
        if hasattr(self, 'value') and self.value is not None:
            if len(self.value) > 50:
                return self.value[:50] + '...'
            else:
                return self.value
        elif hasattr(self, 'checked'):
            return "checked: %s" % self.checked or False
        elif hasattr(self, 'selected'):
            return "selected: %s" % self.selected or False
        return ''

    def set_value(self, val):
        if self.type =='checkbox':
            self.checked = val
            return
        if len(self.options) == 0:
            self.value = val
        else:
            self.set_option(val)

    def set_option(self, val):
        if self.tag == 'select':
            for o in self.options:
                o.selected = (o.value == val)

    def set_value_by_label(self, val):
        if self.tag == 'select':
            for o in self.options:
                o.selected = (o.label == val)

    def set_values(self, vals):
        for opt in self.options:
            n = int(opt.name[-2:])
            if not n in vals:
                opt.checked = False
            else:
                opt.checked = True

    def set_text(self, txt):
        if self.type != 'text':
            return False
        self.value = txt
        return True

    def as_post_data(self):
        """ Return an array of fields that need to be set when posting
            this field.
        """
        rv = []
        f = {'name': self.name}
        if self.tag == "select":
            for o in self.options:
                if o.selected:
                    f['value'] = o.value
                    break
            rv.append(f)
        elif self.type == 'checkbox':
            if self.checked:
                f['value'] = 'on'
                rv.append(f)
        else:
            if len(self.options) == 0:
                f['value'] = self.value
                rv.append(f)
            else:
                for o in self.options:
                    if o.type == 'checkbox' and o.checked:
                        rv.append({'name': o.name, 'value': 'on'})
        return rv

    def option_value(self):
        if self.tag == 'select':
            for opt in self.options:
                if opt.selected:
                    return opt.value
        return None

    def filter_values(self, val):
        if not self.tag in ['input','text', 'select'] or len(self.options) == 0:
            return False

        for opt in self.options:
            if self.tag == 'select':
                opt.selected = val in opt.label
            else:
                if val in opt.label:
                    opt.checked = True
                else:
                    opt.checked = False
        return True


class OfgemForm(object):
    """ Class that represents a form from the Renewables & CHP Ofgem
        website.
        The url to the form should be supplied when creating the object.
    """

    SITE_URL = 'https://www.renewablesandchp.ofgem.gov.uk/Public/'
    def __init__(self, endpoint):
        self.cj = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cj)
        httpsHandler = urllib2.HTTPSHandler(debuglevel = 0)
        self.opener = urllib2.build_opener(cookie_handler, httpsHandler)

        self.action = None
        self.fields = {}
        self.field_labels = {}
        self.data = None
        self.get_form(endpoint)

    def _get_field_labels(self, root):
        """ Attempt to get the labels for the various fields on the
            webform. These are in table rows with a parameter of
            isparameterrow set to true. The format is usually for
            5 columns, with the contents
            label : field : spacer : label : field

        """
        for row in root.xpath("//tr[@isparameterrow='true']"):
            tds = row.xpath("td")
            for i in range(0, len(tds), 3):
                label = tds[i].xpath('span')[0].text
                if label is None:
                    label = tds[i].xpath('span//font')[0].text
                _id = tds[i + 1].xpath('span')[0].get('id')
                if _id is None:
                    _id = tds[i + 1].xpath('span//font')[0].getchildren()[0].get('id')
                if _id is not None:
                    if not _id.endswith('ctl00'):
                        _id += '$ctl00'
                    self.field_labels[_id.replace('_', '$')] = label

    def get_form(self, _url):
        """ get_form() is used to request the initial form. Subsequent
            calls are made as required using the update_form() function.
        """
        root = self._get_form_document(_url)
        form = root.xpath("//form")
        if len(form) == 0:
            raise Exception("Failed to get the form")

        get_and_set_from_xml(self, form[0], ["action", "method"])
        if not self.action.startswith('http'):
            self.action = self.SITE_URL + self.action

        self._get_field_labels(form[0])

        for inp in form[0].xpath("//input"):
            if inp.get('type', '') in ['', 'image']:
                continue

            of = OfgemField(inp)

            if len(of.id) > 30:
                # is it likely to be a multi value field input choice?
                if of.id[25:30] == "ctl03":
                    # multi value field input choice...
                    lbls = form[0].xpath("//label[@for='%s']" % of.id)
                    if len(lbls) > 0:
                        of.label = lbls[0].text
                        if of.label.isdigit():
                            of.label = int(of.label)
                    parent = of.id[:25].replace('_', '$') + 'ctl00'
                    if parent in self.fields:
                        self.fields[parent].options.append(of)
                    else:
                        print("Unknown parent...", parent)

            else:
                if of.type != 'radio' or not of.name in self.fields:
                    self.fields[of.name] = of

        selects = form[0].xpath("//select")
        for s in selects:
            of = OfgemField(s)
            self.fields[of.name] = of
            for opt in s.xpath("option"):
                oo = OfgemField(opt)
                oo.label = opt.text
                if oo.label.isdigit():
                    oo.label = int(oo.label)
                of.options.append(oo)

        for fld in self.fields.values():
            fld.set_postback_flag();

    def _get_or_create_field(self, name):
        if name in self.fields:
            return self.fields[name]
        node = etree.Element("input", value="", type="hidden", name=name)
        of = OfgemField(node)
        self.fields[of.name] = of
        return of

    def set_value(self, fld_lbl, val):
        fld = self._find_field_by_label(fld_lbl)
        if fld is None:
            return False

        fld.set_value(val)
        if fld.postback:
            self.update_validation(fld.name)
        return True

    def set_value_by_label(self, fld_lbl, opt):
        fld = self._find_field_by_label(fld_lbl)
        if fld is None:
            return False
        fld.set_value_by_label(opt)
        if fld.postback:
            self.update_validation(fld.name)
        return True

    def get_options(self, fld_lbl):
        fld = self._find_field_by_label(fld_lbl)
        if fld is None:
            return {}
        opts = {}
        for opt in fld.options:
            opts[opt.label] = opt.value
        return opts

    def set_options_by_label(self, lbl, vals):
        fld = self._find_field_by_label(lbl)
        if fld is None:
            return False
        fld.set_values(vals)
        if fld.postback:
            self.update_validation(fld.name)
        return True

    def as_post_data(self):
        post_data = {}
        for v in self.fields.values():
            for fld in v.as_post_data():
                post_data[fld['name']] = fld['value']
        return post_data

    def set_output_type(self, what):
        try:
            fld = self.fields['ReportViewer$ctl01$ctl05$ctl00']
        except KeyError:
            return False

        for opt in fld.options:
            if opt.value.lower() == what.lower():
                fld.set_value(opt.value)
                self.update_validation(fld.name)
                break
        return True

    def update_validation(self, name):
        self._get_or_create_field('__EVENTTARGET').value = name
        root = self._get_form_document()
        if root is None:
            return False
        ev = root.xpath("input[@name='__EVENTVALIDATION']")
        if len(ev):
            self.fields['__EVENTVALIDATION'].value = ev[0].get('value')
        vs = root.xpath("input[@name='__VIEWSTATE']")
        if len(vs):
            self.fields['__VIEWSTATE'].value = vs[0].get('value')
        return True

    def _get_form_document(self, url = None):
        if self.action is None:
            if url is None:
                return None
            if not url.startswith('http'):
                url = self.SITE_URL + url
            resp = self.opener.open(url)
        else:
            resp = self.opener.open(self.action, urllib.urlencode(self.as_post_data()))
        document = html5lib.parse(resp, treebuilder="lxml", namespaceHTMLElements=False)

        return document.getroot()

    def get_data(self):
        self._get_or_create_field('__EVENTTARGET').value = 'ReportViewer$ctl00$ctl05'
        root = self._get_form_document()
        if root is None:
            return False

        data_url = None
        for script in root.xpath("//script"):
            if script.text is None:
                continue
            if "RSToolbar(" in script.text:
                ck = re.search("new RSToolbar\((.*)\);", script.text)
                if ck is None:
                    return False

                data_url = ck.group(1).split(',')[-2].replace('"', '').strip()
                if not data_url.startswith('http'):
                    data_url = self.SITE_URL + data_url + \
                               self.fields['ReportViewer$ctl01$ctl05$ctl00'].option_value()
                break
        if data_url is None:
            return False

        docresp = self.opener.open(data_url)

        if docresp.code != 200:
            return False

        self.data = docresp.read()
        if len(self.data) == 0:
            return False

        if docresp.headers['content-type'] == 'text/plain':
            # data is sent as utf-16, so convert to utf-8
            self.data = self.data.decode('utf-16').encode('utf-8')

        return True

    def _find_field_by_label(self, lbl):
        for k, v in self.field_labels.iteritems():
            if lbl.lower() in v.lower():
                if k in self.fields:
                    return self.fields[k]
                return None
        return None

    def add_filter(self, what, val):
        """ Attempt to add a filter.
        """
        rv = False
        fld = self._find_field_by_label(what)
        if fld is not None:
            if len(fld.options) == 0:
                fld.value = val
                rv = True
            else:
                rv = fld.filter_values(val)
            if rv:
                self.update_validation(fld.name)
        return rv

    def set_text_value(self, fld_lbl, txt):
        fld = self._find_field_by_label(fld_lbl)
        if fld is None:
            return False

        poss = fld.name[:-2] + '01'
        # Some text fields have a $ctl01 which is a checkbox for
        # NULL, so check for it
        if poss in self.fields:
            self.fields[poss].set_value(False)
            self.update_validation(poss)

        fld.set_text(txt)
        self.update_validation(fld.name)
        return True

    def dump(self):
        for k,v in self.fields.iteritems():
            if k in self.field_labels:
                print(self.field_labels[k])
            else:
                print(k)
            for opts in v.options:
                print("      %50s : %s" % (opts.label, opts.raw_value()))

    def dump_post_data(self):
        for k, v in self.as_post_data().iteritems():
            print("%-30s: %s" % (k,v))
