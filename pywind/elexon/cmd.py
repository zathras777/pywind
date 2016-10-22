import requests

from pywind.elexon.api import B1420, B1330, B1320
from pywind.utils import StdoutFormatter


def elexon_b1320(args):
    """ Congestion Management Measures Countertrading """
    if args.apikey is None:
        print("You MUST supply an API key to access Elexon data")
        return None

    print("This report has very sparse data.")

    api = B1320(args.apikey)
    if args.date is None:
        print("You MUSt supply a date for this report.")
        return None

    if args.period is None:
        print("You MUST supply a period for this report, from 1 to 50")
        return None

    params = {'SettlementDate': args.date,
              'Period': args.period}

    if api.get_data(**params) is False:
        print("No data returned")
        return None

    fmt = StdoutFormatter("12s", "8s", "10.4f", "9s", "6s", "20s", "10s")
    print("\n" + fmt.titles('Date', 'Period', 'Quantity', 'Direction', 'Active', 'Reason', 'Resolution'))
    for item in api.items:
        print(fmt.row(item['settlementdate'],
                      item['settlementperiod'],
                      item['quantity'],
                      item['flowdirection'],
                      str(item['activeflag']),
                      item['reasoncode'],
                      item['resolution']))

    return api


def elexon_b1330(args):
    """ Congestion Management Measures Costs of Congestion Management Service """
    if args.apikey is None:
        print("You MUST supply an API key to access Elexon data")
        return None

    if args.year is None:
        print("You MUST supply a year for this report.")
        return None

    if args.month is None:
        print("You MUST supply a month for this report.")
        return None

    MONTHS = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    api = B1330(args.apikey)
    params = {'Year': args.year or 2016,
              'Month': MONTHS[args.month - 1 or 8]}
    if not api.get_data(**params):
        print("No data returned.")
        return None

    fmt = StdoutFormatter("4d", "5s", "40s", "8s")
    print("\n" + fmt.titles('Year', 'Mon', 'Document Id', 'Rev. Num'))
    for item in api.items:
        print(fmt.row(item['year'], item['month'], item['documentid'], item['documentrevnum']))
    return api


def elexon_b1420(args):
    """ Installed Generation Capacity per Unit """
    if args.apikey is None:
        print("You MUST supply an API key to access Elexon data")
        return None

    api = B1420(args.apikey)
    if not api.get_data(**{'Year': args.year or 2016}):
        print("No data returned.")
        return None

    fmt = StdoutFormatter("30s", "8s", "10s", "6s", "10.1f", "20s")
    print("\n" + fmt.titles('Resource Name', 'NGC Id', 'BM Unit Id', 'Active', 'Output', 'Type'))
    for item in sorted(api.items, key=lambda xxx: xxx['ngcbmunitid']):
        print(fmt.row(item['registeredresourcename'],
                      item['ngcbmunitid'],
                      item['bmunitid'],
                      str(item['activeflag']),
                      float(item['nominal']),
                      item.get('powersystemresourcetype', 'n/a')))

    return api
