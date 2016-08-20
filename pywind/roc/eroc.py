""" eroc.py """

from datetime import datetime
import html5lib

from pywind.utils import get_or_post_a_url, _convert_type


class EROCPrices(object):
    """
    The EROCPrices class provides access to the auction data from the eRIC website.
    Once created the :func:`get_prices()` is called to get the latest information from their
    website and parse the results into period prices.

    Once parsed period information can be accessed by using the class object as a dict, i.e. \
    eroc[200701] would return the average proce for auction(s) held in Jan 2007.

    .. :code:

    >>> from pywind.roc.eroc import EROCPrices
    >>> eroc = EROCPrices()
    >>> eroc.get_prices()
    True
    >>> eroc[200701]
    46.17
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
        :rtype: bool
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
        :rtype: bool
        """
        resp = get_or_post_a_url(self.URL)
        self._parse_content(resp.content)
        return True

    def rows(self):
        """ Generator to return the full auction data as rows.

        :returns: Dict of price data
        :rtype: dict
        """
        for auction in sorted(self.auctions, key=lambda x: x['date']):
            yield {'Auction': {"@{}".format(key): auction[key] for key in auction}}

    def prices(self):
        """ Generator to return the calculated price data.

        :return: Tuple of period, price
        :rtype: tuple
        """
        for prc in sorted(self.periods.keys()):
            yield (prc, self.periods[prc])

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
                                'average_price': _convert_type(row_data[1].text.strip()[1:], 'float'),
                                'lowest_price': _convert_type(row_data[2].text.strip()[1:], 'float'),
                                'total_volume': _convert_type(row_data[3].text or '0', 'int'),
                                'co_fired_volume': _convert_type(row_data[4].text or '0', 'int'),
                                'period': "{}{:02d}".format(dtt.year, dtt.month)}
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
