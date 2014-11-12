import requests
import sys


def _geturl(url,**kwargs):
    for t in range(0,3):
        try:
            return requests.get(url,**kwargs)
        except:
            e = sys.exc_info()[0]
            print("Failed %d of 3, retrying..." % t)
            print(e)
    return None


def xpath_gettext(el, path, default):
    poss = el.xpath(path)
    if len(poss) == 0:
        return default
    return poss[0].text
