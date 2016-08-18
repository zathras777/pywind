import sys

from pywind.ofgem.CertificateSearch import CertificateSearch
from pywind.ofgem.Certificates import CertificatesList


def ofgem_certificate_search(args):
    print("Ofgem Certificate Search\n")

    if args.period is None and args.scheme is None:
        print("You must supply at least a period or scheme.")
        sys.exit(0)

    ocs = CertificateSearch()
    if ocs.start() is False:
        print("Unable to get the form from Ofgem website.")
        sys.exit(0)

    if args.period is not None:
        if ocs.set_period(args.period) is False:
            print("There was an error setting the period.")
            sys.exit(0)
    if args.scheme is not None:
        if ocs.filter_scheme(args.scheme) is False:
            print("There was an error setting the scheme.")
            sys.exit(0)

    if ocs.get_data() is False:
        print("Unable to get the data from Ofgem.")
        sys.exit(0)

    print(ocs.form.raw_data)


def ofgem_certificates(args):
    print("Ofgem Certificate File Parser\n")

    if args.input is None:
        print("You must supply an input filename")
        sys.exit(0)

    ocl = CertificatesList(filename=args.input)
    print("Certificates for {} stations found.".format(len(ocl)))


def ofgem_station_search(args):
    print("Ofgem Station Search\n")



