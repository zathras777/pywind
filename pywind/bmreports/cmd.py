# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>


import sys
from pprint import pprint

from pywind.bmreports.generation_type import GenerationData
from pywind.bmreports.prices import SystemPrices
from pywind.bmreports.unit import UnitData, UnitList, PowerPackUnits
from pywind.utils import multi_level_get, StdoutFormatter


def bm_generation_type(args):
    """ BMReport Generation Type """

    gdd = GenerationData()
    gdd.get_data()
    data = gdd.as_dict()

    fmt = StdoutFormatter("8s", "40s", "5s", "10d", "12.3f")
    row_titles = fmt.titles('Code', 'Generation Type', 'Intcr', 'Output', 'Percentage')

    print(data)
    for sect in data.keys():
        if 'start' in data[sect]:
            print("{} - started {}".format(sect.title(), data[sect]['start']))
        if 'finish' in data[sect]:
            print("{} - finished {}".format(" " * len(sect.title()), data[sect]['finish']))

        else:
            print(sect.title())

        print("\n" + row_titles)
        for typ in data[sect]['data']:
            print(fmt.row(typ['code'], typ['name'],
                              '  Y' if typ['interconnector'] else '  N',
                              typ['value'], typ['percent']))
        print("\n")
    return gdd


def bm_system_prices(args):
    """ BMReport System Price Data """
    if args.date is not None:
        spp = SystemPrices(dtt=args.date)
    else:
        spp = SystemPrices()
        print("\nNo date specified, using today.\n")
    if spp.get_data() is False:
        print("Failed to get data from remote server.")
        sys.exit(0)
    print("Date: {}".format(spp.dtt))
    fmt = StdoutFormatter('6s', '>10s', '>10s')
    print(fmt.titles("Period", 'SBP', 'SSP'))
    for prc in spp.prices:
        print(fmt.row(str(prc['period']), prc['sbp'], prc['ssp']))

    return spp


def bm_unitdata(args):
    """ BMReport Unit Constraint Data """

    udd = UnitData()
    if udd.get_data() is False:
        print("Unable to get unit data.")
        sys.exit(0)

    print("Data is for period {}, {}".format(udd.period, udd.date))
    fmt = StdoutFormatter('9s', '30s', '>10.4f', '>10s', '>10.4f', '>10s', '>10.4f', '>10.4f', '>10.4f', ">10.4f")
    print("{:43s}     Bid Volume              Offer Volume           Cashflow".format(' '))
    print(fmt.titles("NGC", 'Lead', 'Original', 'Tagged', 'Original', 'Tagged', 'Bid', 'Offer', 'Bid Rate', 'Offer Rate'))
    for bmu in udd.data:
        print(fmt.row(bmu.id, bmu.lead,
                      bmu.bid_volume,
                      multi_level_get(bmu.volume, 'bid_values.tagged.total.value', 'n/a'),
                      bmu.offer_volume,
                      multi_level_get(bmu.volume, 'offer_values.tagged.total.value', 'n/a'),
                      bmu.bid_cashflow,
                      bmu.offer_cashflow,
                      bmu.rate("bid"),
                      bmu.rate("offer")))
    return udd


def bm_unitlist(args):
    """ BMReport Unit List """

    ulist = UnitList()
    if ulist.get_list() is False:
        print("There was an error getting the list from the BMReports website")
        sys.exit(0)

    print("Total of {} units\n".format(len(ulist)))

    fmt = StdoutFormatter('12s', '12s', '10s', '12s', '12s')
    print(fmt.titles('NGC ID', 'Sett Id', 'Fuel Type',
                     'Eff. From', 'Eff. To'))
    for unit in ulist.units:
        vals = [unit['ngc_id'],
                unit.get('sett_id', ''),
                unit['fuel_type'],
                unit['eff_from'].strftime("%d %b %Y")]
        if unit['eff_to'] is not None:
            vals.append(unit['eff_to'].strftime("%d %b %Y"))
        else:
            vals.append('n/a')
        print(fmt.row(*vals))

    return ulist


def power_pack_units(args):
    """ National Grid Power Pack Units """

    ppu = PowerPackUnits()
    if ppu.get_list() is False:
        print("Unable to get an updated list of power pack units")
        sys.exit(0)

    print("Total of {} units".format(len(ppu)))
    fmt = StdoutFormatter('12s', '12s', '35s', '>10f', '12s', '8s', '>12f')
    print(fmt.titles("NGC Id", "Sett ID", "Station Name", "Reg Cap", "Date Added", "BM Unit?", "Capacity"))

    for unit in ppu.units:
        vals = [
            unit.get('ngc_id'),
            unit.get('sett_id', 'n/a'),
            unit.get('name'),
            unit.get('reg_capacity', ''),
            unit.get('date_added'),
            "Yes" if unit.get('bmunit') else "No",
            unit.get('cap', 0.0)
        ]
        if vals[4] is not None:
            vals[4] = vals[4].strftime("%d %b %Y")
        else:
            vals[4] = 'Unknown'
        print(fmt.row(*vals))

    return ppu
