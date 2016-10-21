def make_elexon_url(report, version):
    return "https://api.bmreports.com/BMRS/{}/{}".format(report.upper(), version)


def map_children_to_dict(xml_parent, node_list):
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
    for child in xml_parent.getchildren():
        if child.tag in node_list:
            rv_dict[child.tag.lower()] = child.text
    return rv_dict

