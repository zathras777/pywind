""" Information taken from the Elexon API User Guide.

https://www.elexon.co.uk/wp-content/uploads/2016/10/Application-Programming-Interfaces-API-and-Data-Push-user-guide.pdf

"""
from datetime import datetime

from pywind.elexon.utils import make_elexon_url, map_children_to_dict
from pywind.utils import get_or_post_a_url, parse_response_as_xml


class ElexonAPI(object):
    XML_MAPPING = None
    MULTI_RESULTS = None

    def __init__(self, apikey=None, report=None):
        self.report = report
        self.version = 'v1'
        self.apikey = apikey
        self.items = []
        self.multi = {}

    def get_data(self, **params):
        if self.report is None:
            raise Exception("ElexonAPI objects require the report be set before use.")
        if self.apikey is None:
            raise Exception("An API key is required to use the Elexon API accessor functionality")

        url = make_elexon_url(self.report, self.version)
        params.update({'APIKey': self.apikey, 'ServiceType': 'xml'})
        req = get_or_post_a_url(url, params=params)
        print(req.content)
        xml = parse_response_as_xml(req)
        http = xml.xpath('/response/responseMetadata/httpCode')
        if int(http[0].text) != 200:
            return False

        if self.MULTI_RESULTS is None:
            for item in xml.xpath('/response/responseBody/responseList/item'):
                item_dict = map_children_to_dict(item, self.XML_MAPPING)
                print(item_dict)
                if 'activeFlags' in item_dict:
                   item_dict['activeflag'] = item_dict['activeflag'] == 'Y'
                self.post_item_cleanup(item_dict)
                self.items.append(item_dict)
        else:
            for result_set in self.MULTI_RESULTS:
                self.multi[result_set[0]] = []
                for item in xml.xpath(result_set[1]):
                    item_dict = map_children_to_dict(item, self.XML_MAPPING)
                    if 'activeFlags' in item_dict:
                       item_dict['activeflag'] = item_dict['activeflag'] == 'Y'

                    self.post_item_cleanup(item_dict)
#                    print(item_dict)
                    self.multi[result_set[0]].append(item_dict)

        return True

    def post_item_cleanup(self, item):
        return


class B1320(ElexonAPI):
    XML_MAPPING = [
        'timeSeriesID',
        'settlementDate',
        'settlementPeriod',
        'quantity',
        'flowDirection',
        'reasonCode',
        'documentType',
        'processType',
        'resolution',
        'curveType',
        'activeFlag',
        'documentID',
        'documentRevNum'
    ]

    def __init__(self, apikey):
        super(B1320, self).__init__(apikey, 'B1320')

    def post_item_cleanup(self, item):
        if 'activeflag' in item:
            item['activeflag'] = item['activeflag'] == 'Y'
        if 'quantity' in item:
            item['quantity'] = float(item['quantity'])

    def rows(self):
        for item in self.items:
            row = item.copy()
            row['quantity'] = "{:10.4f}".format(item['quantity']).strip()
            row['activeflag'] = str(item['activeflag'])
            yield {'CongestionCounterTrade': row}


class B1330(ElexonAPI):
    XML_MAPPING = [
        'timeSeriesID',
        'year',
        'month',
        'congestionAmount',
        'documentType',
        'processType',
        'businessType',
        'resolution',
        'activeFlag',
        'documentID',
        'documentRevNum'
    ]

    def __init__(self, apikey):
        super(B1330, self).__init__(apikey, 'B1330')

    def post_item_cleanup(self, item):
        if 'activeflag' in item:
            item['activeflag'] = item['activeflag'] == 'Y'
        if 'year' in item:
            item['year'] = int(item['year'])

    def rows(self):
        for item in self.items:
            row = item
            row['year'] = str(item['year'])
            row['activeflag'] = str(item['activeflag'])
            yield {'CongestionCosts': row}


class B1420(ElexonAPI):
    XML_MAPPING = [
        'documentType',
        'businessType',
        'processType',
        'timeSeriesID',
        'powerSystemResourceType',
        'year',
        'bMUnitID',
        'registeredResourceEICCode',
        'nominal',
        'nGCBMUnitID',
        'registeredResourceName',
        'activeFlag',
        'documentID',
        'implementationDate',
        'powerSystemResourceType'
    ]

    def __init__(self, apikey):
        super(B1420, self).__init__(apikey, 'B1420')

    def post_item_cleanup(self, item):
        if 'nominal' in item:
            item['nominal'] = float(item['nominal'])
        if 'powersystemresourcetype' in item:
            item['powersystemresourcetype'] = item['powersystemresourcetype'].replace('\"', '')
        if 'activeflag' in item:
            item['activeflag'] = item['activeflag'] == 'Y'

    def rows(self):
        for item in self.items:
            row = item.copy()
            row['year'] = str(item['year'])
            row['nominal'] = "{:10.1f}".format(item['nominal']).strip()
            row['activeflag'] = str(item['activeflag'])
            yield {'ConfigurationData': row}


class DERSYSDATA(ElexonAPI):
    XML_MAPPING = [
        'recordType',
        'settlementDate',
        'settlementPeriod',
        'systemSellPrice',
        'systemBuyPrice',
        'bSADDefault',
        'priceDerivationCode',
        'reserveScarcityPrice',
        'indicativeNetImbalanceVolume',
        'sellPriceAdjustment',
        'buyPriceAdjustment',
        'totalSystemAcceptedOfferVolume',
        'totalSystemAcceptedBidVolume',
        'totalSystemTaggedAcceptedOfferVolume',
        'totalSystemTaggedAcceptedBidVolume',
        'totalSystemAdjustmentSellVolume',
        'totalSystemAdjustmentBuyVolume',
        'totalSystemTaggedAdjustmentSellVolume',
        'totalSystemTaggedAdjustmentBuyVolume',
        'activeFlag'
    ]

    def __init__(self, apikey=None):
        super(DERSYSDATA, self).__init__(apikey, 'DERSYSDATA')

    def post_item_cleanup(self, item):
        item['settlementdate'] = datetime.strptime(item['settlementdate'], "%Y-%m-%d").date()
        item['activeflag'] = item['activeflag'] == 'Y'

        for key in item.keys():
            if key in ['recordtype', 'settlementdate', 'settlementperiod', 'pricederivationcode',
                       'bsaddefault', 'activeflag'] or item[key] == 'NULL':
                continue
            item[key] = float(item[key])


#class B1620(ElexonAPI):
#    def __init__(self, apikey=None):
#        super(B1620, self).__init__(apikey, 'B1620')


class FUELINST(ElexonAPI):
    XML_MAPPING = [
        'recordType',
        'startTimeOfHalfHrPeriod',
        'settlementPeriod',
        'publishingPeriodCommencingTime',
        'ccgt',
        'oil',
        'coal',
        'nuclear',
        'wind',
        'ps',
        'npshyd',
        'ocgt',
        'other',
        'intfr',
        'intirl',
        'intned',
        'intew',
        'activeFlag'
    ]

    def __init__(self, apikey=None):
        super(FUELINST, self).__init__(apikey, 'FUELINST')

    def post_item_cleanup(self, item):
        if 'activeflag' in item:
            item['activeflag'] = item['activeflag'] == 'Y'
        dttm = datetime.strptime(item['publishingperiodcommencingtime'], "%Y-%m-%d %H:%M:%S")
        item['date'] = dttm.date()
        item['time'] = dttm.time()


class DERBMDATA(ElexonAPI):
    XML_MAPPING = [
        'recordType',
        'settlementDate',
        'settlementPeriod',
        'bmUnitID',
        'bmUnitType',
        'leadPartyName',
        'ngcBMUnitName',
        'acceptanceID',
        'shortAcceptanceFlag',
        'volumeAcceptedforBidOfferPair-1',
        'volumeAcceptedforBidOfferPair-2',
        'volumeAcceptedforBidOfferPair-3',
        'volumeAcceptedforBidOfferPair-4',
        'volumeAcceptedforBidOfferPair-5',
        'volumeAcceptedforBidOfferPair-6',
        'volumeAcceptedforBidOfferPair1',
        'volumeAcceptedforBidOfferPair2',
        'volumeAcceptedforBidOfferPair3',
        'volumeAcceptedforBidOfferPair4',
        'volumeAcceptedforBidOfferPair5',
        'volumeAcceptedforBidOfferPair6',
        'cashflowAcceptedforBidOfferPair-1',
        'cashflowAcceptedforBidOfferPair-2',
        'cashflowAcceptedforBidOfferPair-3',
        'cashflowAcceptedforBidOfferPair-4',
        'cashflowAcceptedforBidOfferPair-5',
        'cashflowAcceptedforBidOfferPair-6',
        'cashflowAcceptedforBidOfferPair1',
        'cashflowAcceptedforBidOfferPair2',
        'cashflowAcceptedforBidOfferPair3',
        'cashflowAcceptedforBidOfferPair4',
        'cashflowAcceptedforBidOfferPair5',
        'cashflowAcceptedforBidOfferPair6',
        'total',
        'activeFlag'
    ]

    MULTI_RESULTS = (
        ('bav', '/response/responseBody/bav/responseList/item'),
        ('ipbav', '/response/responseBody/ipbav/responseList/item'),
        ('ipbc', '/response/responseBody/ipbc/responseList/item'),
        ('ipoc', '/response/responseBody/ipoc/responseList/item'),
    )

    def __init__(self, apikey=None):
        super(DERBMDATA, self).__init__(apikey, 'DERBMDATA')

    def post_item_cleanup(self, item):
        item['activeflag'] = item['activeflag'] == 'Y'


class BMUNITSEARCH(ElexonAPI):
    XML_MAPPING = [
        'recordType',
        'bmUnitID',
        'bmUnitType',
        'leadPartyName',
        'ngcBMUnitName',
        'activeFlag',
    ]

    CATEGORIES = {
        '2': 'Supplier',
        'C': 'Additional Supplier',
        'E': 'Embedded',
        'G': 'Unknown',
        'I': 'Interconnector',
        'M': 'Miscellaneous',
        'S': 'Unknown',
        'T': 'Directly connected'
    }

    def __init__(self, apikey=None):
        super(BMUNITSEARCH, self).__init__(apikey, 'BMUNITSEARCH')

    def post_item_cleanup(self, item):
        item['activeflag'] = item['activeflag'] == 'Y'
        item['category'] = self.CATEGORIES[item['bmunittype']]
