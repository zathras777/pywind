#pywind

This pywind python module retrieves
historic data on wind energy and other electricity generation in the UK.

##Background

The primary user of the original module is the [Variable Pitch website](http://www.variablepitch.co.uk/)
which uses it
to record data for wind farm stations in the UK. It has been released as an
open source module in the hope that it can help others.

This module uses data from the BM Reports, DECC, Elexon, eRoc, and Ofgem websites. You must comply
with their respective terms and conditions when using this module (or any other means)
to access their data.
The use of their names here does not indicate their endorsement of this software in any way.

####This fork

This particular fork is designed to work with Python 2.7 and Python 3.4.
I (EnergyNumbers) have removed the imports of `urllib`, `urllib2`, and replaced
them with the `requests` package. All of the sample scripts work; however, these
do not form a comprehensive set of test scripts, so **it's entirely possible that
things work in the original version on Python 2.7, that don't work in this fork
on any version of Python.** If you have used the original version of this library,
please do some testing before switching to this fork. If you find incompatibilities,
please raise an issue here, and let me know what the problem is. Ideally, include a small
program that reproduces the problem.

##Ofgem Station & Certificate Data

The ofgem module retrieves data from Ofgem's Renewables & CHP database, without the user having to
negotiate their webform which breaks in modern browsers.

The module provides the [StationSearch](pywind/ofgem/StationSearch.py#L24) and 
[CertificateSearch](pywind/ofgem/CertificateSearch.py#L22) classes that can
be used to search the Ofgem database.

Example 1: [sample script onestation.py](sample_scripts/onestation.py) gives an example of retrieving
information on stations with "Novar" in their name

Example 2: Getting all certificates issued to Off-Shore wind farms during Jan 2012:
see the [sample script offwind.py](sample_scripts/offwind.py)

Examples 3,4: Sample scripts are included to search for [certificates](sample_scripts/ofgem_certificate_search.py)
and [stations](sample_scripts/ofgem_station_search.py)

More information about the information available can be found at
http://www.ofgem.gov.uk/Pages/OfgemHome.aspx


##ROC Prices

These are obtained from the eROC auction site using the
[EROCPrices](pywind/roc/eroc.py#L5) class
within the roc module. The prices for the various periods listed are then
available by using the object as a `dict`. See, for example, the [ROC price
sample script](sample_scripts/rocprice.py).

The format for the period is `yyyymm` where `yyyy` is the 4 digit year and `mm`
is the 2 digit month. If there is more than one auction in a given period the
average of the results is calculated.

##DECC Planning Monthly Report

DECC has a report showing the renewable electricity planning applications
it knows about with their current status. It includes the capacity, address
and geographic information as well, together with various planning dates
and flags. See the [decc.py sample script](sample_scripts/decc.py) for a simple example.

Each record is a `DeccRecord` object (defined in the decc module) with a large number of attributes set. The
records have native python types set for dates and boolean types but additionally
have a lat & lon attribute set from the OS grid reference supplied in the
DECC data for each site.

As far as I can tell it is not possible to filter the data for a particular
date range, so the entire dataset is returned each time the `get_data()` function
is called. Filtering is left to the user.

---

##BM Reports on system prices and generation quantities

###First, a caveat on the use of BMReports data
The data provided by the BMReports website is owned by Elexon UK and permission needs
to be sought before reproducing it. The following functions in the bmreports module should only be used with
this restriction in mind when accessing the site and downloading data.


###Electricity Prices
To get the System Sell Price (SSP) and the System Buy Price (SBP) for a given date
the [SystemPrices](pywind/bmreports/prices.py#L22) class can be used.
See, for example, the [bmdata.py sample script](sample_scripts/bmdata.py)


###Derived Unit Data
The [UnitData](pywind/bmreports/unit.py#L33) class allows the BMReports reports
to be accessed.
Presently this class defaults to querying the Derived Data to extract information
on Constraint Payments made. See for example the
[sample script derived\_unit\_data.py](sample_scripts/derived_unit_data.py)


###Balancing Mechanism Units
The list of units (with their fuel types) is available as an Excel spreadsheet from the BMReports
website. The [UnitList](pywind/bmreports/unit.py#L177) class can be used to get and parse the current list.
See for example the [bm\_unit\_list.py sample script](sample_scripts/bm_unit_list.py)


###Power Pack Unit Data
Most smaller Onshore Wind stations do not supply their output directly to the
grid via High Voltage connections and as such are considered to be "embedded"
stations. The impact of this on the capacity data released is discussed in some
detail in a PDF document by James Hemingway (available at https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/65923/6487-nat-grid-metering-data-et-article-sep12.pdf)

To obtain a list of the wind stations that are connected to the grid via HV and as
such have their output considered the [PowerPackUnits](pywind/bmreports/unit.py#L225)
class should be used. The class downloads the Power Pack Modules spreadsheet and extracts its contents.

See [powerpack.py](sample_scripts/powerpack.py) for a simple example.

NB the `date_added` will be either a `datetime.date` object or `None`.


###Electricity Usage

The BM Reports website provides historic and realtime data about electricity usage within
the UK and can be accessed via the `bmreports` module.

To get the data, see e.g. the [gendata.py](sample_scripts/gendata.py) sample script

This will create a [GenerationData](pywind/bmreports/generation_type.py#L110)
object that will contain summary generation data covering the previous 24 hours,
30 minutes, and instantaneous observations.

Each period is available as a `dict` object containing the resultant values and
time periods, e.g.
```python
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
```
More information can be found at http://www.bmreports.com/