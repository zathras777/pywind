from pywind.elexon.api import DERBMDATA


class BalancingPeriodData(object):
    """ Class that holds the volume and cashflow totals for a single station/period. """
    def __init__(self):
        self.bid_cashflow = 0.0
        self.bid_volume = 0.0
        self.offer_cashflow = 0.0
        self.offer_volume = 0.0

    def add_data(self, element, item):
        if element == 'ipbav':
            self.bid_volume = item['total']
        elif element == 'ipoav':
            self.offer_volume = item['total']
        elif element == 'ipbc':
            self.bid_cashflow = item['total']
        elif element == 'ipoc':
            self.offer_cashflow = item['total']

    @property
    def bid_rate(self):
        if self.bid_volume == 0:
            return 0
        return self.bid_cashflow / self.bid_volume

    @property
    def offer_rate(self):
        if self.offer_volume == 0:
            return 0
        return self.offer_cashflow / self.offer_volume


class BalancingUnitData(object):
    """ Class to hold information about a single station for multiple periods """
    def __init__(self, item):
        self.unit = item['ngcbmunitname']
        self.lead = item['leadpartyname']
        self.type = item['bmunitid'][0]
        self.periods = {}

    def add_data(self, element, item):
        period = self.periods.setdefault(item['settlementperiod'],
                                         BalancingPeriodData())
        period.add_data(element, item)


class BalancingData(object):
    """ Parent class to hold data from the :mod:DERBMDATA API. """
    def __init__(self, api_key):
        self.api = DERBMDATA(api_key)
        self.units = {}

    def get_data(self, **params):
        if self.api.get_data(**params) is False:
            return False

        for element in self.api.multi:
            for item in self.api.multi[element]:
                if item['total'] == 0:
                    continue
                unit = self.units.setdefault(item['ngcbmunitname'],
                                             BalancingUnitData(item))
                unit.add_data(element, item)
        return True

