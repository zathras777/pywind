""" Utility functions for pywind.bmreports. """
# pylint: disable=E1101

from lxml import etree


def yesno(val):
    """ Convert yes/no into True/False """
    return val.lower() in ['yes', 'true']


def xpath_gettext(elm, path, default):
    """ Get text from an element. """
    poss = elm.xpath(path)
    if len(poss) == 0:
        return default
    return poss[0].text


def parse_response_as_xml(request):
    """ Given a request/response object, attempt to parse it's contents as XML.

        Nov 2014
          Using parser with recover=True was the suggestion of energynumbers

    """
    try:
        parser = etree.XMLParser(recover=True)
        return etree.XML(request.read(), parser).getroottree()
    except etree.XMLSyntaxError:
        return None
