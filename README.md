pywind
======

The pywind module is intended to provide a python module that can be used
to access online information related to Wind Energy in the UK, though it can
be used to access information for any form of energy made available by the
agencies it provides access to.

Background
----------

The primary user of this module is the Variable Pitch website which uses it
to record data for wind farm stations in the UK. It has been released as an
open source module in the hope that it can help others.

http://www.variablepitch.co.uk/

Important Changes
-----------------
From version 0.9.6 onwards the Station object 'accreditation' field is now
more accurately named 'generator_id'.


Electricity Usage
-----------------

The BM Reports website provides realtime data about electricity usage within
the UK and can be accessed via the bmreports module.

To get the data,

```
>>> from pywind.bmreports import *
>>> gd = GenerationData()
```

This will create a GenerationData object that will contain summary generation
data covering the previous

    - 24 hours
    - 30 minutes
    - instant

Each period is available as a dict object containing the resultant values and
time periods, e.g.

    '24hours': {'start': datetime.datetime(2013, 3, 3, 10, 30),
                'finish': datetime.datetime(2013, 3, 4, 10, 30)
                'total': 945844,
                'data': [
        {'code': 'CCGT', 'percent': '24.2', 'name': 'Combined Cycle Gas Turbine', 'value': '229014'},
        {'code': 'OCGT', 'percent': '0.0', 'name': 'Open Cycle Gas Turbine', 'value': '0'},
        {'code': 'OIL', 'percent': '0.0', 'name': 'Oil', 'value': '0'},
        {'code': 'COAL', 'percent': '48.7', 'name': 'Coal', 'value': '460899'},
        {'code': 'NUCLEAR', 'percent': '18.0', 'name': 'Nuclear', 'value': '170693'},
        {'code': 'WIND', 'percent': '1.6', 'name': 'Wind', 'value': '15062'},
        {'code': 'PS', 'percent': '1.2', 'name': 'Pumped Storage', 'value': '11260'},
        {'code': 'NPSHYD', 'percent': '0.6', 'name': 'Non Pumped Storage Hydro', 'value': '5744'},
        {'code': 'OTHER', 'percent': '1.9', 'name': 'Other', 'value': '18442'},
        {'code': 'INTFR', 'percent': '1.4', 'name': 'Import from France', 'value': '13314'},
        {'code': 'INTIRL', 'percent': '0.0', 'name': 'Import from Ireland', 'value': '163'},
        {'code': 'INTNED', 'percent': '2.2', 'name': 'Import from the Netherlands', 'value': '21252'},
        {'code': 'INTEW', 'percent': '0.0', 'name': 'East/West Interconnector', 'value': '0'}
                ]
                }

More information can be found at http://www.bmreports.com/

Ofgem Station & Certificate Data
--------------------------------

By using the ofgem module it is possible to access the Renewables & CHP database from Ofgem
without needing to use their webform. It was developed to allow easy access to the data after
attempts to use their webform failed with some modern browsers. Additionally the filtering
options possible with the webform are unusable in many browsers.

Classes are provided to search the Certifcates and Stations databases.

Searching
---------
The module provides the StationSearch and CertificateSearch classes that can
be used to search the Ofgem database.

NB NB NB When setting the month/year these should be done after other parameters have been
         set due to the interaction of the form and the module.

e.g. Searching for stations with Novar in their name

```
>>> from pywind.ofgem import *
>>> ss = StationSearch()
>>> ss.filter_name('Novar')
>>> ss.get_data()
True
>>> print len(ss)
1
>>> print ss.stations[0].as_string()

    Accreditation                 : R00014SESC
    Status                        : Live
    Name                          : GLENN GLAS NOVAR EST
    Scheme                        : RO
    Capacity                      : 916.0
    Country                       : Scotland
    Technology                    : Hydro 20MW DNC or less (ROS code = SE)
    Generation                    : General
    Accreditation dt              : 2002-04-01 00:00:00
    Commission dt                 : 1997-03-01 00:00:00
    Developer                     : Glenglass Hydro Ltd
    Owner address                 : Novar Estate OfficeEvantonRoss-shireScotland,IV16 9XL
    Fax                           :
    Address                       : SRO Glenglass Hydro Limited,Glenglass Hydro LtdRiver Glass (Allt Graad),Novar,IV16 9XL,Scotland
```

e.g. Getting all certificates issued to Off-Shore wind farms during Jan 2012

```
>>> from pywind.ofgem import *
>>> cs = CertificateSearch()
>>> cs.set_month(1)
>>> cs.set_year(2012)
>>> cs.technology = [23]
>>> cs.get_data()
True
>>> len(cs)
76
```

The results show that certifcate data for 76 stations has been returned.

To show certificate data, you need to use the scheme for each station, i.e.
```
>>> print cs.stations()[0]['REGO'][0].as_string()

    Accreditation                 : G01164FWEN
    Name                          : Ormonde Wind Farm
    Capacity                      : 150000.0
    Scheme                        : REGO
    Country                       : England
    Technology                    : Off-shore Wind
    Generation                    : N/A
    Period                        : Jan-2012
    Certs                         : 44915
    Start_no                      : G01164FWEN0000000000010112310112GEN
    Finish_no                     : G01164FWEN0000044914010112310112GEN
    Factor                        : 1.0
    Issue_dt                      : 2012-03-27 00:00:00
    Status                        : Issued
    Status_dt                     : 2012-04-18 00:00:00
    Current_holder                : Vattenfall Energy Trading GmbH
    Reg_no                        : HRB 80335
```

While accessing the data may be slightly harder than in previous versions, it
is far easier to understand and manipulate.

More information about the information available can be found at
http://www.ofgem.gov.uk/Pages/OfgemHome.aspx

Sample scripts are included to search for certificates and stations.

ROC Prices
----------

These are obtained from the eROC auction site using the EROCPrices() class
within the roc module. The prices for the various periods listed are then
available by using the object as a dict.

```
>>> from pywind.roc import *
>>> er = EROCPrices()
>>> er[200701]
46.17
```

The format for the period is simply yyyymm where yyyy is the 4 digit year and mm
is the 2 digit month. If there is more than one auction in a given period the
average of the results is calculated.

BM Report Data Ownership
------------------------

The data provided by the BMReports website is owned by Elexon UK and permission needs
to be sought before reproducing it. The following functions should only be used with
this restriction in mind as they access the site and download data.

The exact restrictions on the data usage are unclear at this time.


Electricity Prices
------------------

To get the System Sell Price (SSP) and the System Buy Price (SBP) for a given date
the bmreports.SystemPrices class can be used.

```
>>> from pywind.bmreports import SystemPrices
>>> s = SystemPrices()
>>> s.get_data()
True
>>> s.prices
[{'sbp': '67.57225', 'period': '1', 'ssp': '48.90000'},
 {'sbp': '66.00000', 'period': '2', 'ssp': '49.70000'},
 {'sbp': '53.24000', 'period': '3', 'ssp': '40.50000'},
 {'sbp': '67.22574', 'period': '4', 'ssp': '53.53000'},
 {'sbp': '62.22428', 'period': '5', 'ssp': '53.36000'},
 {'sbp': '62.90939', 'period': '6', 'ssp': '53.12000'},
 {'sbp': '62.81903', 'period': '7', 'ssp': '50.68000'},
 {'sbp': '62.78963', 'period': '8', 'ssp': '51.10000'},
 {'sbp': '60.12207', 'period': '9', 'ssp': '50.98000'},
 {'sbp': '55.00000', 'period': '10', 'ssp': '50.63000'},
 {'sbp': '59.61707', 'period': '11', 'ssp': '51.40000'},
 {'sbp': '63.71989', 'period': '12', 'ssp': '51.80000'},
  ...
]
```

Derived Unit Data
-----------------
The pywind.bmreports.UnitData class allows the BMReports reports to be accessed.
Presently this class defaults to querying the Derived Data to extract information
on Constraint Payments made.

```
>>> from pywind.bmreports import UnitData
>>> ud = UnitData()
>>> ud.get_data()
True
>>> ud.data
[{'lead': 'RWE NPOWER PLC',
  'offer': {},
  'bid': {'volume': '-45.0000', 'cashflow': '-1788.0300'},
  'ngc': 'ABTH7',
  'type': 'T',
  'id': 'T_ABTH7'},
 {'lead': 'RWE NPOWER PLC',
  'offer': {},
  'bid': {'volume': '-22.0000', 'cashflow': '-871.9700'},
  'ngc': 'ABTH8',
  'type': 'T',
  'id': 'T_ABTH8'},
...
]
```

Balancing Mechanism Units
-------------------------
The list of units (with their fuel types) is available as an Excel spreadsheet from the BMReports
website. The pywind.bmreports.UnitList class can be used to get and parse the current list.


```
>>> from pywind.bmreports import UnitList
>>> ul = UnitList()
>>> len(ul)
365
>>> ul.by_fuel_type('wind')
[{'eff_from': datetime.date(2012, 11, 14),
  'ngc_id': u'ACHYW-1',
  'fuel_type': u'WIND',
  'eff_to': datetime.date(2050, 12, 31)},
 {'eff_from': datetime.date(2012, 11, 14),
  'ngc_id': u'AKGLW-1',
  'fuel_type': u'WIND',
  'eff_to': datetime.date(2050, 12, 31)},
...
]
```

Power Pack Unit Data
--------------------
Most smaller Onshore Wind stations do not supply their output directly to the
grid via High Voltage connections and as such are considered to be "embedded"
stations. The impact of this on the capacity data released is discussed in some
detail in a PDF document by James Hemingway (available at https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/65923/6487-nat-grid-metering-data-et-article-sep12.pdf)

To obtain a list of the wind stations that are connected to the grid via HV and as
such have their output considered the Power Pack spreadsheet can be used. This class
attempts to download and provide a list of it's contents.

```
>>> from pywind.bmreports import PowerPackUnits
>>> pp = PowerPackUnits()
>>> len(pp)
89
>>> pp.units
[{'ngc_id': u'ACHYW-1',
  'sett_id': u'',
  'name': u'Achany',
  'cap': 50.0,
  'bmunit': True,
  'date_added': None,
  'reg_capacity': 50.0
}, {
  'ngc_id': u'AKGLW-1',
...
]
```

The date_added will be either a datetime.date object or None.

DECC Planning Monthly Report
----------------------------
The DECC have a report showing the renewable electricity planning applications
it knows about with their current status. It includes the capacity, address
and geographic information as well, together with various planning dates
and flags.

```
>>> from pywind.decc import MonthlyExtract
>>> me = MonthlyExtract()
>>> me.get_data()
True
>>> len(me)
4988
>>> me.records[0]
<pywind.decc.Report.DeccRecord object at 0x1d150d0>
```

Each record is a DeccRecord object with a large number of attributes set. The
records have native python types set for dates and boolean types but additionally
have a lat & lon attribute set from the OS grid reference supplied in the
DECC data for each site.

```
>>> me.record[0].site_name
'Hunterston - cofiring'
>>> me.records[0].lat
55.735731298569
>>> me.records[0].lon
-4.888572411340284
```

As far as I can tell it is not possible to filter the data for a particular
date range, so the entire dataset is returned each time the get_data() function
is called. Filtering is left to the user.
