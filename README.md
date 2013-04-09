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

The module provides the StationSearch and CertificateSearch classes that can
be used to search the Ofgem database.

e.g. Searching for stations with Novar in their name

```
>>> from pywind.ofgem import *
>>> ss = StationSearch()
>>> ss.station = 'Novar'
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
>>> print cs.certificates[0].as_string()

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
[{'lead': 'RWE NPOWER PLC', 'ngc': 'ABTH8',
  'cash': {'bid': '-1023.3200'},
  'volumes': {'tagged': '-57.3751', 'original': '-57.3750'}, 'type': 'T', 'id': 'T_ABTH8'},
 {'lead': 'RWE NPOWER PLC', 'ngc': 'ABTH9',
  'cash': {'bid': '-594.5200'},
  'volumes': {'tagged': '-60.0000', 'original': '-60.0000'}, 'type': 'T', 'id': 'T_ABTH9'},
 {'lead': 'Jade Power Generation Ltd', 'ngc': 'COTPS-1',
  'cash': {'bid': '-802.6000'},
  'volumes': {'originalpriced': '-25.0000', 'original': '-25.0000'}, 'type': 'T', 'id': 'T_COTPS-1'},
...
]
```
