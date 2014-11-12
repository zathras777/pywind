import urllib2
import sys


def _geturl(url):
    for t in range(0,3):
        try:
            return urllib2.urlopen(url)
        except:
            e = sys.exc_info()[0]
            print("Failed {0} of 3, retrying...".format(t))
            print(e)
    return None


def xpath_gettext(el, path, default):
    poss = el.xpath(path)
    if len(poss) == 0:
        return default
    return poss[0].text
