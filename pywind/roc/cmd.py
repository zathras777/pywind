import sys

from pywind.roc import EROCPrices


def roc_prices(args):
    print("eROC Auction Prices\n")

    roc = EROCPrices()
    if not roc.get_prices():
        print("Unable to get prices from eROC website.")
        sys.exit(0)

    print("  Period         Average Price ")
    print("  ------------   -------------")
    for price in roc.prices():
        print("  {:<12s}  {:>11.2f}".format(price[0], price[1]))

    return roc

