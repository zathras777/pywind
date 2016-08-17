""" eroc.py """

from datetime import datetime
import html5lib

from pywind.utils import get_or_post_a_url


def price_to_float(txt):
    txt = txt.strip().replace(' ', '')
    return float(txt[1:])


def volume_to_int(txt):
    if txt is None:
        return 0
    return int(txt.replace(',', ''))


class EROCPrices(object):
    """
    The EROCProces class provides access to the auction data from the eRIC website. \
    Once created the :func:`get_prices()` is called to get the latest infrmation from their \
    website and parse the results into period prices.

    Once parsed period information can be accessed by using the class object as a dict, i.e. \
    eroc[200701] would return the average proce for auction(s) held in Jan 2007.

    .. :code:

    >>> from pywind.roc.eroc import EROCPrices
    >>> eroc = EROCPrices()
    >>> eroc.get_prices()
    True
    >>> eroc[200701]

    """
    URL = 'http://www.epowerauctions.co.uk/erocrecord.htm'

    def __init__(self):
        self.auctions = []
        self.periods = {}

    def process_file(self, local_file):
        """
        Process a local HTML file.

        .. :note::Mainly used in development/testing.

        :param local_file: Filename to be parsed.
        :returns: True or False
        :rtype: boolean
        """
        self.auctions = []
        self.periods = {}
        with open(local_file, "r") as lfh:
            self._parse_content(lfh.read())
        return True

    def get_prices(self):
        """
        Get the recent prices.

        :return: True or False
        :rtype: boolean
        """
        resp = get_or_post_a_url(self.URL)
        self._parse_content(resp.content)
        return True

    def _parse_content(self, content):
        document = html5lib.parse(content,
                                  treebuilder="lxml",
                                  namespaceHTMLElements=False)
        for tbl in document.xpath('.//table'):
            ths = tbl.xpath('.//tr//th')
            if len(ths) == 0 or ths[0].text != 'Auction Date':
                continue
            for row in tbl.xpath('.//tr')[1:]:
                row_data = row.xpath('td')
                if len(row_data) == 0 or row_data[0].text.strip() == '':
                    continue
                dtt = datetime.strptime(row_data[0].text.strip(), "%d %B %Y").date()
                auction_info = {'date': dtt,
                                'average_price': price_to_float(row_data[1].text),
                                'lowest_price': price_to_float(row_data[2].text),
                                'total_volume': volume_to_int(row_data[3].text),
                                'co_fired_volume': volume_to_int(row_data[4].text),
                                'period': int("{}{:02d}".format(dtt.year, dtt.month))}
                self.auctions.append(auction_info)
        for info in self.auctions:
            if info['period'] in self.periods:
                previous = self.periods[info['period']]
                if not isinstance(previous, list):
                    self.periods[info['period']] = [info['average_price'], previous]
                else:
                    self.periods[info['period']].append(info['average_price'])
            else:
                self.periods[info['period']] = info['average_price']
        for key in self.periods.keys():
            if isinstance(self.periods[key], list):
                self.periods[key] = sum(self.periods[key]) / len(self.periods[key])
        return True

    def __getitem__(self, item):
        if item in self.periods:
            return self.periods[item]
        raise KeyError("No such period available [%s]" % item)

    def as_table_string(self):
        """
        Function to return a nicely formatted period and average price.

        :returns: String representation of data as a table.
        """
        sss = ''
        for prd in sorted(self.periods.keys()):
            sss += "  {}       {:.02f}\n".format(prd, self.periods[prd])
        return sss
