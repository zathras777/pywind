def xpath_gettext(el, path, default):
    poss = el.xpath(path)
    if len(poss) == 0:
        return default
    return poss[0].text
