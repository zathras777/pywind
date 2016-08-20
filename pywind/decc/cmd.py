import sys

from pywind.decc import MonthlyExtract


def decc_extract(args):
    """ Function to provide command line DECC functionality.

    :param args: The command line args
    :returns: DECC :mod:`MonthlyExtract` object
    :rtype: MonthlyExtract
    """
    print("DECC Monthly Planning Extract\n")

    decc = MonthlyExtract(args.input)
    if decc.get_data() is False:
        print("Unable to get data from DECC")
        sys.exit(0)

    print("Total of {} planning records received for {}".format(len(decc), decc.available['period']))

    return decc

