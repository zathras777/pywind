""" Information taken from the Elexon API User Guide.

https://www.elexon.co.uk/wp-content/uploads/2016/10/Application-Programming-Interfaces-API-and-Data-Push-user-guide.pdf

"""
from datetime import datetime

from pywind.utils import get_or_post_a_url, parse_response_as_xml, map_xml_to_dict


def make_elexon_url(report, version):
    return "https://api.bmreports.com/BMRS/{}/{}".format(report.upper(), version)


class ElexonAPI(object):
    XML_MAPPING = None
    MULTI_RESULTS = None

    def __init__(self, apikey=None, report=None):
        self.report = report
        self.version = 'v1'
        self.apikey = apikey
        self.items = []
        self.multi = {}

    def __len__(self):
        """ Returns the number of items available. """
        return len(self.items)

    def get_data(self, **params):
        """ Get data from the Elexon servers and attempt to parse it into a series of
            dicts each representing a record. Parameters are passed as a dict.
            Multiple sets of data are created in the multi member, single sets in items.
        """
        if self.report is None:
            raise Exception("ElexonAPI objects require the report be set before use.")
        if self.apikey is None:
            raise Exception("An API key is required to use the Elexon API accessor functionality")

        url = make_elexon_url(self.report, self.version)
        params.update({'APIKey': self.apikey, 'ServiceType': 'xml'})
        req = get_or_post_a_url(url, params=params)
#        print(req.content)
        xml = parse_response_as_xml(req)
        http = xml.xpath('/response/responseMetadata/httpCode')
        response_code = int(http[0].text)
        if response_code == 204:
            print("No content returned, but no error reported.")
            return True
        elif response_code != 200:
            print("No data returned. Error reported.")
            err = xml.xpath('/response/responseMetadata/description')
            print(err[0].text)
            return False

        if self.MULTI_RESULTS is None:
            for item in xml.xpath('/response/responseBody/responseList/item'):
                item_dict = map_xml_to_dict(item, self.XML_MAPPING)

                if 'activeflag' in item_dict:
                   item_dict['activeflag'] = item_dict['activeflag'] == 'Y'
                if 'settlementperiod' in item_dict:
                    item_dict['settlementperiod'] = int(item_dict['settlementperiod'])

                self.post_item_cleanup(item_dict)
                self.items.append(item_dict)
        else:
            for result_set in self.MULTI_RESULTS:
                self.multi[result_set[0]] = []
                for item in xml.xpath(result_set[1]):
                    item_dict = map_xml_to_dict(item, self.XML_MAPPING)
                    if 'activeFlags' in item_dict:
                       item_dict['activeflag'] = item_dict['activeflag'] == 'Y'
                    if 'settlementperiod' in item_dict:
                        item_dict['settlementperiod'] = int(item_dict['settlementperiod'])

                    self.post_item_cleanup(item_dict)
#                    print(item_dict)
                    self.multi[result_set[0]].append(item_dict)

        return True

    def post_item_cleanup(self, item):
        """ Holder for a subclassed function to transform the members of the basic dict 
            into something more useful.
        """
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
#        if 'activeflag' in item:
#            item['activeflag'] = item['activeflag'] == 'Y'

    def rows(self):
        for item in self.items:
            row = item.copy()
            row['year'] = str(item['year'])
            row['nominal'] = "{:10.1f}".format(item['nominal']).strip()
            row['activeflag'] = str(item['activeflag'])
            yield {'ConfigurationData': row}


class B1610(ElexonAPI):
    def __init__(self, apikey):
        super(B1610, self).__init__(apikey, 'B1610')

    def post_item_cleanup(self, item):
        item['quantity'] = float(item['quantity'])

    def rows(self):
        for item in self.items:
            row = item.copy()
            row['activeflag'] = str(item['activeflag'])
            yield {'ConfigurationData': row}


class B1630(ElexonAPI):
    XML_MAPPING = [
        'documentType',
        'businessType',
        'processType',
        'timeSeriesID',
        'quantity',
        'curveType',
        'resolution',
        'settlementDate',
        'settlementPeriod',
        'PSRType',
        'powerSystemResourceType',
        'registeredResourceEICCode',
        'marketGenerationUnitEICCode',
        'activeFlag',
        'documentID',
        'documentRevNum'
    ]

    def __init__(self, apikey):
        super(B1630, self).__init__(apikey, 'B1630')

    def rows(self):
        for item in self.items:
            row = item.copy()
            row['activeflag'] = str(item['activeflag'])
            yield {'ConfigurationData': row}


class DERSYSDATA(ElexonAPI):
    """ Derived System Data """
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


class FUELINST(ElexonAPI):
    """ Instant Generation by Fuel Type """
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
        dttm = datetime.strptime(item['publishingperiodcommencingtime'], "%Y-%m-%d %H:%M:%S")
        item['date'] = dttm.date()
        item['time'] = dttm.time()


class DERBMDATA(ElexonAPI):
    """ Derived Balancing Mechanism Data """
    MULTI_RESULTS = (
        ('bav', '/response/responseBody/bav/responseList/item'),
        ('oav', '/response/responseBody/oav/responseList/item'),
        ('ipbav', '/response/responseBody/ipbav/responseList/item'),
        ('ipoav', '/response/responseBody/ipoav/responseList/item'),
        ('ipbc', '/response/responseBody/ipbc/responseList/item'),
        ('ipoc', '/response/responseBody/ipoc/responseList/item'),
    )

    def __init__(self, apikey=None):
        super(DERBMDATA, self).__init__(apikey, 'DERBMDATA')

    def post_item_cleanup(self, item):
        item['settlementperiod'] = int(item['settlementperiod'])
        for key in item:
            if 'volume' in key or 'cashflow' in key or 'total' in key:
                item[key] = float(item[key])


class BMUNITSEARCH(ElexonAPI):
    """ Balancing Mechanism Unit Search """
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
        item['category'] = self.CATEGORIES[item['bmunittype']]


class UOU2T52W(ElexonAPI):
    """ National Output Useable by Fuel Type and BM Unit (2-52 Weeks Ahead)"""
    def __init__(self, apikey=None):
        super(UOU2T52W, self).__init__(apikey, 'UOU2T52W')
