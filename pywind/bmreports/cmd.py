import sys

from pywind.bmreports.generation_type import GenerationData
from pywind.bmreports.prices import SystemPrices
from pywind.bmreports.unit import UnitData
from pywind.utils import multi_level_get


def bm_generation_type(args):
    print("BMReport Generation Type\n")
    gdd = GenerationData()
    gdd.get_data()
    data = gdd.as_dict()

    ROW_FMT = "  {:8s} {:40s} {:5s} {:>10s} {:>12s}"
    row_titles = ROW_FMT.format('Code', 'Generation Type', 'Intcr',
                                'Output', 'Percentage') + "\n" + \
                 ROW_FMT.format('-' * 8, '-' * 40, '-' * 5, '-' * 10, '-' * 12)

    for sect in data.keys():
        if 'start' in data[sect]:
            print("{} - started {}".format(sect.title(), data[sect]['start']))
        if 'finish' in data[sect]:
            print("{} - finished {}".format(" " * len(sect.title()), data[sect]['start']))

        else:
            print(sect.title())

        print("\n" + row_titles)
        for typ in data[sect]['data']:
            print(ROW_FMT.format(typ['code'], typ['name'],
                                 '  Y' if typ['interconnector'] else '  N',
                                 typ['value'], typ['percent']))
        print("\n")
    return gdd


def bm_system_prices(args):
    print("BMReport System Price Data\n")
    if args.date is not None:
        spp = SystemPrices(dtt=args.date)
    else:
        spp = SystemPrices()
        print("\nNo date specified, using today.\n")
    if spp.get_data() is False:
        print("Failed to get data from remote server.")
        sys.exit(0)
    print("Date: {}".format(spp.dtt))
    ROW_FMT = "  {:6s}  {:>10s}  {:>10s}"
    print(ROW_FMT.format("Period", 'SBP', 'SSP') + "\n" +
          ROW_FMT.format('-' * 6, '-' * 10, '-' * 10))
    for prc in spp.prices:
        print(ROW_FMT.format(str(prc['period']), prc['sbp'], prc['ssp']))

    return spp


def bm_unitdata(args):
    print("BMReport Unit Constraint Data\n")
    udd = UnitData()
    if udd.get_data() is False:
        print("Unable to get unit data.")
        sys.exit(0)

    ROW_FMT = " {:7s}  {:30s} |{:>10s} {:>10s}|{:>10s} {:>10s}|{:>10s} {:>10s}|"
    print("{:41s}|     Bid Volume      |     Offer Volume    |     Cashflow        |".format(' '))
    print(ROW_FMT.format("NGC", 'Lead', 'Original', 'Tagged', 'Original', 'Tagged', 'Bid', 'Offer'))
    print(ROW_FMT.format('-' * 7, '-' * 30, '-' * 10, '-' * 10,'-' * 10, '-' * 10, '-' * 10, '-' * 10))

    for bmu in udd.data:
        print(ROW_FMT.format(bmu['ngc'], bmu['lead'],
                             multi_level_get(bmu, 'volume.bid_values.original.total.value', 'n/a'),
                             multi_level_get(bmu, 'volume.bid_values.tagged.total.value', 'n/a'),
                             multi_level_get(bmu, 'volume.offer_values.original.total.value', 'n/a'),
                             multi_level_get(bmu, 'volume.offer_values.tagged.total.value', 'n/a'),
                             multi_level_get(bmu, 'cashflow.bid_values.total.value', 'n/a'),
                             multi_level_get(bmu, 'cashflow.offer_values.total.value', 'n/a')))
    return udd
