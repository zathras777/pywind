from datetime import timedelta, time, datetime, date

from pywind.elexon.api import B1420, B1330, B1320, FUELINST, DERSYSDATA, DERBMDATA, BMUNITSEARCH
from pywind.utils import StdoutFormatter, args_get_datetime


def check_api_key(args):
    if args.apikey is None:
        print("You MUST supply an API key to access Elexon data.")
        print("Registration is free, but you need to go to the URL below and register.")
        print("https://www.elexonportal.co.uk/registration/newuser")
        return False
    return True


def get_check_data(api, params):
    if not api.get_data(**params):
        print("No data returned.")
        return False
    return True


def elexon_generation_inst(args):
    """ Generation Data at 5 minute intervals from the Elexon Data Portal """
    if not check_api_key(args):
        return None

    api = FUELINST(args.apikey)
    args_get_datetime(args)
    params = {}
    if args.fromdatetime is not None or args.todatetime is not None:
        params['FromDateTime'] = args.fromdatetime if args.fromdatetime else args.todatetime - timedelta(days=1)
        params['ToDateTime'] = args.todatetime if args.todatetime else args.fromdatetime + timedelta(days=1)
    else:
        print("Getting data for yesterday as no dates specified.")
        params['FromDateTime'] = datetime.combine(date.today() - timedelta(days=2), time(23, 59))
        params['ToDateTime'] = datetime.combine(date.today() - timedelta(days=1), time(23, 59))

    if get_check_data(api, params) is False:
        return None

    fmt = StdoutFormatter("10s", "6s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s", "7s")
    print("\n" + fmt.titles('Date', 'Time', 'Period', 'CCGT', 'Oil', 'Coal', 'Nuclear', 'Wind', 'PS', 'NPSHYD', 'OCGT',
                            'Other', 'Int Fr', 'Int Irl', 'Int Ned', 'Int E/W'))
    for item in api.items:
        print(fmt.row(item['date'].strftime("%Y-%m-%d"),
                      item['time'].strftime("%H:%M"),
                      item['settlementperiod'],
                      item['ccgt'],
                      item['oil'],
                      item['coal'],
                      item['nuclear'],
                      item['wind'],
                      item['ps'],
                      item['npshyd'],
                      item['ocgt'],
                      item['other'],
                      item['intfr'],
                      item['intirl'],
                      item['intned'],
                      item['intew'],
                      ))
    return api


def elexon_b1320(args):
    """ Congestion Management Measures Countertrading """
    if not check_api_key(args):
        return None

    print("This report has *VERY* sparse data.")

    api = B1320(args.apikey)
    if args.date is None:
        print("You MUST supply a date for this report.")
        return None

    if args.period is None:
        print("You MUST supply a period for this report, from 1 to 50")
        return None

    params = {'SettlementDate': args.date,
              'Period': args.period}

    if get_check_data(api, params) is False:
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

    if get_check_data(api, params) is False:
        return None

    fmt = StdoutFormatter("4d", "5s", "40s", "8s")
    print("\n" + fmt.titles('Year', 'Mon', 'Document Id', 'Rev. Num'))
    for item in api.items:
        print(fmt.row(item['year'], item['month'], item['documentid'], item['documentrevnum']))
    return api


def elexon_b1420(args):
    """ Installed Generation Capacity per Unit """
    if not check_api_key(args):
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


def elexon_sbp(args):
    """ Derived System Prices from Elexon """
    if not check_api_key(args):
        return None

    api = DERSYSDATA(args.apikey)

    params = {
        'FromSettlementDate': args.fromdate or date.today() - timedelta(days=1),
        'ToSettlementDate': args.todate or args.fromdate or (date.today()) - timedelta(days=1)
    }

    if get_check_data(api, params) is False:
        return None

    fmt = StdoutFormatter("15s", "20s", "15.4f", "15.4f", "4s")
    print("\nSystem adjustments are included in the figures shown below where '*' is shown.\n")
    print("\n" + fmt.titles('Date', 'Settlement Period', 'Sell Price', 'Buy Price', 'Adj?'))
    for item in api.items:
        print(fmt.row(item['settlementdate'].strftime("%Y %b %d"),
                      item['settlementperiod'],
                      item['systemsellprice'] + item['sellpriceadjustment'],
                      item['systembuyprice'] + item['buypriceadjustment'],
                      "*" if item['sellpriceadjustment'] + item['buypriceadjustment'] > 0 else ''
                      ))

    return api


def elexon_bm_data(args):
    """ Derived System Prices from Elexon """
    if not check_api_key(args):
        return None

    api = DERBMDATA(args.apikey)

    params = {
        'SettlementDate': args.date or date.today() - timedelta(days=1),
        'SettlementPeriod': args.period or 1
    }

    if not get_check_data(api, params):
        return None

    return api


def elexon_bm_unit(args):
    """ Derived System Prices from Elexon """
    if not check_api_key(args):
        return None

    api = BMUNITSEARCH(args.apikey)
    params = {
        'BMUnitType': args.unit_type or '*'
    }
    if not get_check_data(api, params):
        return None

    print("Total of {} units\n".format(len(api.items)))

    fmt = StdoutFormatter('12s', '12s', '^8s', '30s', '50s')
    print("\n" + fmt.titles('NGC ID', 'BM ID', 'Active ?', 'BM Type', 'Lead Party Name'))
    for item in sorted(api.items, key=lambda x: x['ngcbmunitname']):
        print(fmt.row(item['ngcbmunitname'],
                      item['bmunitid'],
                      'Y' if item['activeflag'] else 'N',
                      "{}, {}".format(item['bmunittype'], item['category']),
                      item['leadpartyname']))

    return api
