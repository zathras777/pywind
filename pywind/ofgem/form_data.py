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

""" Each Ofgem web form contains a lot of information. Classes in this file try to
    make managing the data easier.
"""
from __future__ import print_function

import logging
import html5lib

import re
from pprint import pprint

import sys


def element_attributes(elm):
    """ Return a dict of the basic attributes we want from an XML element. """
    return {'tag': elm.tag,
            'type': elm.get('type'),
            'name': elm.get('name'),
            'value': elm.get('value', ''),
            'readonly': elm.get('readonly', False),
            'disabled': elm.get('disabled', False)}


def selected_list(element):
    """ Given an element dict, return a list of the indexes. """
    if 'selected' in element:
        return element['selected']
    return [int(idx.strip()) for idx in element['value'].split(',')]


def quote(toquote):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    """
    # fastpath
    if not toquote:
        if toquote is None:
            raise TypeError('None object cannot be quoted')
        return toquote

    always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                   '0123456789_.-')
    quoted = []
    for char in toquote:
        ooo = ord(char)
        if ooo < 128 and char in always_safe:
            quoted.append(char)
        elif ooo < 0x7f:
            quoted.append('%{:02X}'.format(ooo))
        elif ooo < 0xbf:
            quoted.append('%C2%{:02X}'.format(ooo))
    return ''.join(quoted)


class FormData(object):
    """ Class to store and allow easy manipulation of data from an Ofgem form."""
    def __init__(self, initial_data="", stored_file=None):
        self.action = None
        self.method = None
        self.export_url = None
        self.logger = logging.getLogger(__name__)
        self.labels = {}
        self.elements = {}
        self.postbacks = {}
        self.seperators = {}

        if stored_file is not None:
            self.logger.debug("Initialising FormData from %s", stored_file)
            with open(stored_file, "r") as ofh:
                self._parse(ofh.read())
        elif len(initial_data) > 0:
            self.logger.debug("%d bytes of initial data supplied for FormData", len(initial_data))
            self._parse(initial_data)

        self._add_element('__EVENTARGUMENT', value='')
        self._add_element('__ASYNCPOST', value='true')
        self._add_element('__LASTFOCUS', value='')
        self._add_element('__EVENTTARGET', value='')

    def update(self, content=""):
        """ Given some content, update the form.

        :param content: The content to update the form from
        :returns: True or False
        :rtype: bool
        """
        content = content.strip()
        if sys.version_info >= (3,0):
            content = content.decode()

        if len(content) == 0:
            return False

        if '|' in content[:8]:
            # we have been sent a delta response...
            return self._parse_delta_content(content)

        return self._parse(content)

    def set_value_by_label(self, lbl, value):
        """ Set a value based on a label. """
        el_name = None
        for key in self.labels.keys():
            if key.lower() == lbl.lower():
                el_name = self.labels[key]
                break
        if el_name is None:
            self.logger.info("Unable to find label matching %s", lbl)
            return False, False
        self.logger.debug("Found label %s", lbl)
        return self._set_value_by_name(el_name, value)

    def as_post_data(self, quoted=True, submit=False):
        """
        Process the form elements and return in a dict suitable for using as POST data.

        :param quoted: If set the returned data will be fully quoted.
        :param submit: True only if this is a submission post.
        :returns: Dict of data to be posted as name: value pairs
        :rtype: dict
        """
        post_data = {}
        for name in sorted(self.elements.keys()):
            if 'divDropDown' in name and 'HiddenIndices' not in name:
                continue
            element = self.elements[name]
            if submit is False and element.get('type', '') == 'submit':
                continue
            if 'cbNull' in name and element['checked'] is False:
                continue
            post_data[name] = self._get_post_value(name, element)
#        pprint(post_data)
        if quoted:
            return {quote(key): quote(post_data[key]) for key in sorted(post_data.keys())}
        return post_data

    def value_for_label(self, lbl):
        if lbl not in self.labels:
            raise KeyError("Label {} does not exist".format(lbl))
        return self._get_post_value(self.labels[lbl])

    ### Private functions below

    def __contains__(self, item):
        return item in self.elements

    def __setitem__(self, key, key_value):
        if not isinstance(key_value, dict):
            self._add_element(key, value=key_value)
        else:
            self._add_element(key, dict=key_value)

    def __getitem__(self, item):
        if item in self.elements:
            return self.elements[item]
        raise KeyError(item)

    def _add_element(self, el_name=None, **kwargs):
        """
        Add an element to the class. This allows for direct setting by using
        passing in a keyword parameter of dict={...}. el_name is required
        unless a dict is passed that way.
        """
        el_name = kwargs['name'] if el_name is None else el_name
        if 'dict' in kwargs:
            self.elements[el_name] = kwargs['dict']
            return
        self.elements[el_name] = {key: kwargs[key] for key in kwargs}

    def _set_value_by_name(self, name, value):
        element = self.elements[name]
        if element['tag'] == 'select':
            sel = None
            if isinstance(value, int):
                if value not in element['options']:
                    self.logger.info("Unable to set %s to %s [not in options]", name, value)
                    pprint(element['options'])
                    return False, False
                sel = value
            else:
                for opt in element['options'].keys():
                    if element['options'][opt].lower() == value.lower():
                        sel = opt
                        break
            if sel is None:
                self.logger.info("Unable to find a matching option for %s", value)
                return False, False
            if sel in element['selected']:
                return True, False
            element['selected'] = [sel]
            return True, self._postback_needed(name)
        elif 'value' in element:
            element['value'] = value

            self._check_set_dropdown(name, value)

            if 'checkbox' in element and element['checkbox']:
                ckbox = self.elements[name.replace('txtValue', 'cbNull')]
                ckbox['checked'] = False
                return True, self._postback_needed(ckbox['name']) or self._postback_needed(name)

#            pprint(element)
            return True, self._postback_needed(name)

        return False, False

    def _check_set_dropdown(self, name, value):
        dd = name.replace('txtValue', 'divDropDown$ctl00')
        if dd not in self.elements:
            return
        options = []
        idxs = []
        idx_el = None
        for poss in self.elements:
            if dd[:-2] in poss:
                options.append(poss)
                if 'HiddenIndices' in poss:
                    idx_el = poss
        if idx_el is None:
            return
        options = sorted(options)
        for n in range(len(options) - 2):
            poss_el = self.elements.get(options[n + 2])
            if poss_el['label'] == value:
                idxs.append(str(n))
        self.elements[idx_el]['value'] = ",".join(idxs)
        return True

    def _postback_needed(self, name):
        """ If a postback is needed, set things up and return True. """
        if self.postbacks.get(name, False):
            self.elements['ScriptManager1'] = {'value': 'ScriptManager1|{}'.format(name)}
            self.elements['__EVENTTARGET'] = {'value': name}
            return True
        return False

    def _parse(self, content):
        document = html5lib.parse(content, treebuilder="lxml", namespaceHTMLElements=False)

        self._parse_scripts(document)
        forms = document.xpath('*//form[@id="form1"]')
        if len(forms) == 0:
            self.logger.info("No form with an id of 'form1' found in supplied data.")
            return False
        self._parse_form(forms[0])
        return True

    def _parse_form(self, form_root):
        """ If we have a complete form, process it. """
        self.action = form_root.get('action')
        self.method = form_root.get('method')

        self.logger.debug("Form: Action: %s", self.action)
        self.logger.debug("    : Method: %s", self.method)

        self._process_input(form_root)
        self._process_cbnull()
        self._process_select(form_root)
        self._process_labels(form_root)

    def _process_input(self, root):
        self.logger.debug("Processing INPUT elements...")
        for elm in root.xpath('.//input'):
            inp_data = element_attributes(elm)
            if inp_data['type'] in [None, 'image']:
                continue
            if 'cbNull' in inp_data['name']:
                inp_data['checked'] = elm.get('checked', '') == 'checked'
            if inp_data['type'] == 'radio':
                if elm.get('checked', '') != 'checked':
                    continue
            self._add_element(None, **inp_data)
            self.logger.debug("  - adding %s", inp_data['name'])

    def _process_cbnull(self):
        for key in self.elements.keys():
            if key.endswith('cbNull'):
                if key.replace('cbNull', 'txtValue') in self.elements:
                    self.elements[key.replace('cbNull', 'txtValue')]['checkbox'] = True

    def _process_select(self, root):
        self.logger.debug("Processing SELECT elements...")
        for elm in root.xpath('.//select'):
            inp_data = element_attributes(elm)
            inp_data['selected'] = []
            options = {}
            for opt in elm.iterchildren():
                options[opt.get('value')] = opt.text.strip()
                if opt.get('selected', '') == 'selected':
                    inp_data['selected'].append(opt.get('value'))
            inp_data['options'] = options
            self._add_element(None, **inp_data)
            self.logger.debug("  - adding %s with %d options",
                              inp_data['name'], len(options))

    def _process_labels(self, root):
        self.logger.debug("Processing labels...")
        for elm in root.xpath('*//tr/td//label'):
            if len(elm.getchildren()) == 0:
                txt = elm.text
            else:
                txt_nodes = elm.xpath('./span/font')
                if len(txt_nodes) == 0:
                    continue
                txt = txt_nodes[0].text.strip().replace(':', '')
            txt = txt.strip()#.replace(u'\u00a0', 'A0')
            name = elm.get('for').replace('_', '$')
            if 'rbTrue' in name or 'rbFalse' in name:
                continue
            if 'txtValue' not in name and 'ddValue' not in name:
                elem = self.elements.get(name, None)
                if elem is None:
                    self.logger.info("Unable to find an element to label : %s", name)
                    continue
                elem['label'] = txt
                continue
            self.labels[txt] = name
            self.logger.debug("  - adding %s for %s", txt, name)

    def _parse_scripts(self, root):
        """ Look for callback information. """
        for scr in root.xpath('*//script'):
            if scr.text is None or 'Sys.Application' not in scr.text:
                continue
            for jss in re.findall(r"Sys.Application.add_init\(function\(\) \{\n(.*)\n\}\);",
                                  scr.text):
                tid = re.search(r'\"(DropDownId|TextBoxId|FalseCheckId|NullCheckBoxId)\":\"(.*?)\",',
                                jss)
                if tid is None:
                    continue
                name = tid.group(2).replace('_', '$')
                if '"PostBackOnChange":true' in jss:
                    self.postbacks[name] = True
                lss = re.search('\"ListSeparator\":\"(.*?)\",', jss)
                if lss is not None:
                    self.seperators[name] = lss.group(1)

    def _parse_delta_content(self, content):
        """
        Function to parse the "delta" content that is returned. Each is a series of 4 elements seperated
        by a pipe symbol. The elements of the change appear to be
        - number of bytes for the "payload"
        - what the change relates to
        - field name or additional content information
        - change payload.
        The first element appears to always be 1|#||4|.
        """
        components = []
        comp = []
        consumed = 0
        pos = 0
        while pos < len(content):
            if content[pos] == '|':
                comp.append(content[consumed:pos])
                consumed = pos + 1
                if len(comp) == 3:
                    self.logger.debug("%d: %s, %s, %s [@%d]", pos, comp[0], comp[1], comp[2], consumed)
                    try:
                        length = int(comp[0])
                    except ValueError:
                        self.logger.warning("Inavlid length detected while parsing delta content :-("
                                            "%s is not a valid length", comp[0])
#                        with open('delta.txt', 'w') as ofh:
#                            ofh.write(content)
                        return False
                    comp.pop(0)
                    if consumed + length > len(content):
                        self.logger.info("Content buffer is not long enough")
                        break
                    val = content[consumed:consumed + length]
                    consumed += length
                    if content[consumed] != '|':
                        self.logger.info("Length appears wrong... Found %s instead of |",
                                         content[consumed])
                        # Small fudge factor if required
                        for poss in range(1, 10):
                            if content[consumed + poss] == '|':
                                val += content[consumed:consumed + poss]
                                consumed += poss
                                break
                        if poss == 10:
                            self.logger.warning("Unable to recover from invalid length. Exiting")
                            return False
                        self.logger.info("Length adjusted by %d bytes", poss)
                    comp.append(val)
                    components.append(comp)
                    comp = []
                    consumed += 1
                    pos = consumed
            pos += 1

        if components[0][0] != '#':
            self.logger.warning("Invalid delta response received.")
            return False

        if components[1][0] == 'pageRedirect':
            self.logger.info("Redirect received. Something went wrong :-(")
            return False

        self.logger.debug("Processing delta update with %s components", len(components))
        for comp in components[1:]:
            if comp[0] == 'hiddenField':
                element = self.elements.get(comp[1], None)
                if element is None:
                    self.elements[comp[1]] = {'value': comp[2]}
                    self.logger.debug(" - created element %s", comp[1])
                else:
                    element['value'] = comp[2]
                    self.logger.debug(" - updated value for %s", comp[1])
            elif comp[0] == 'formAction':
                self.action = comp[2]
                self.logger.debug(" - updated action URL to %s", self.action)
            elif 'script' in comp[0]:
                if 'ExportUrlBase' in comp[2]:
                    export_base = re.search('\"ExportUrlBase\":\"(.*?)\",', comp[2])
                    self.export_url = export_base.group(1).replace('\\u0026', '&')
                    self.logger.debug(" - found export url: %s", self.export_url)
        return True

    def _get_post_value(self, name, element=None):
        if element is None:
            element = self.elements[name]
        if 'txtValue' in name:
            self.logger.debug("building string from selected options for %s", name)
            related = self._get_related_txt_element(name)
            if related is None:
                self.logger.info("Unable to find related select for %s", name)
                return ''
            return self._build_text_value(related, element)
        if 'ddValue' in name:
            return ",".join([str(idx) for idx in element['selected']])
        if 'cbNull' in name:
            return 'on' if element['checked'] else ''
        if 'HiddenIndices' in name:
            return element['value']
        return element['value']

    def _get_related_txt_element(self, name):
        """ If we have a txtValue field then we need to find the element that contains the
            choices to build the required text. This could be a select element or one of the
            more complex multiple choice checkbox fields.
        """
#        print("_get_related_txt_element - {}".format(name))
        for poss in ['ddValue', 'cbNull', 'divDropDown$ctl01$HiddenIndices']:
            related = name.replace('txtValue', poss)
            rel_el = self.elements.get(related, None)
#            print("    {} => {}".format(related, rel_el))
            if rel_el is not None:
                return rel_el
        return None

    def _build_text_value(self, element, original):
        if 'cbNull' in element['name']:
            if element['checked']:
                return ''
            return original['value']
        sep = self.seperators.get(original['name'], ',')
        if element['tag'] == 'select':
            return sep.join([element['options'][idx] for idx in selected_list(element)])
        components = []
        if ',' in element['value']:
            for idx in element['value'].strip().split(','):
                num_idx = int(idx) + 2
                val_name = element['name'].replace('01$HiddenIndices', "{:02d}".format(num_idx))
                elem = self.elements.get(val_name, None)
                if elem is None:
                    self.logger.info("Unable to find a text value for %s -> %s", idx, val_name)
                    continue
                components.append(elem.get('label', 'unknown'))
#        print("        {}".format(components))
        return sep.join(components)

