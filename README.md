pywind
======

Python files related to public information for Energy production, with
a particular focus on Wind Energy.

Background
----------

The files in this repository have been developed during development of
http://www.variablepitch.co.uk/ and are being made available to try and
assist others.

BMReports
---------

http://www.bmreports.com/

This site provides data about electricity usage in the UK.

    generation_type.py

    This will get the current data from the BM Reports website and parse it
    into useful objects. It is used to generate the daily statistics shown 
    at http://www.variablepitch.co.uk/data/summary/

Ofgem
-----

http://www.ofgem.gov.uk/Pages/OfgemHome.aspx

The Ofgem site has a lot of information, but much of it is in places
or formats that aren't obvious. The Ofgem module contains code designed
to help extract that data.

    station.OfgemStationData

    This class can be used to query the Accredited Stations via the
    Ofgem website. The results can be returned as a list of dicts or
    as OfgemStation objects.

    certificate.OfgemCertificateData

    Setting the month and year allows the Ofgem Certificate report
    to be queried and the results returned as dicts or OfgemCertificate
    objects.

