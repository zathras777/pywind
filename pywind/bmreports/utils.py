from lxml import etree


def xpath_gettext(el, path, default):
    poss = el.xpath(path)
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
