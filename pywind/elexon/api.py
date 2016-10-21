from pywind.elexon.utils import make_elexon_url, map_children_to_dict
from pywind.utils import get_or_post_a_url, parse_response_as_xml


class ElexonAPI(object):
    XML_MAPPING = None

    def __init__(self, apikey=None, report=None):
        self.report = report
        self.version = 'v1'
        self.apikey = apikey
        self.items = []

    def get_data(self, **params):
        if self.report is None:
            raise Exception("ElexonAPI objects require the report be set before use.")
        if self.apikey is None:
            raise Exception("An API key is required to use the Elexon API accessor functionality")

        url = make_elexon_url(self.report, self.version)
        params.update({'APIKey': self.apikey, 'ServiceType': 'xml'})
        req = get_or_post_a_url(url, params=params)
        xml = parse_response_as_xml(req)
        http = xml.xpath('/response/responseMetadata/httpCode')
        if int(http[0].text) != 200:
            return False

        for item in xml.xpath('/response/responseBody/responseList/item'):
            item_dict = map_children_to_dict(item, self.XML_MAPPING)
            if hasattr(self, 'post_item_cleanup'):
                getattr(self, 'post_item_cleanup')(item_dict)
            self.items.append(item_dict)

        return True


class B1320(ElexonAPI):
    def __init__(self, apikey):
        super(B1320, self).__init__(apikey, 'B1320')


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
