from datetime import datetime
from lxml import html

from pywind.ofgem.utils import get_url


class EROCPrices(object):
    URL = 'http://www.epowerauctions.co.uk/erocrecord.htm'

    def __init__(self):
        self.periods = {}
        self.get_prices()

    def get_prices(self):
        try:
            resp = get_url(self.URL)
        except:
            return False

        def alltext(el):
            return (''.join(el.text_content())).strip()

        def process_table(tbl):
            for row in tbl.findall('.//tr'):
                if len(row) == 0:
                    continue
                datestr = alltext(row[0])
                if 'Auction Date' in datestr:
                    continue

                try:
                    avg = float(alltext(row[1])[1:])
                    dt = datetime.strptime(datestr, "%d %B %Y")
                except ValueError:
                    continue

                numperiod = dt.year * 100 + dt.month
                if numperiod in self.periods:
                    self.periods[numperiod] = (self.periods[numperiod] + avg) / 2
                else:
                    self.periods[numperiod] = avg

        doc = html.parse(resp)
        for t in doc.findall('.//table'):
            if 'Auction Date' in alltext(t.findall('.//tr')[0]):
                process_table(t)
        return True

    def __getitem__(self, item):
        if item in self.periods:
            return self.periods[item]
        raise KeyError("No such period available [%s]" % item)

    def as_table_string(self):
        s = ''
        for p in sorted(self.periods.keys()):
            s += "  {}       {:.02f}\n".format(p, self.periods[p])
        return s