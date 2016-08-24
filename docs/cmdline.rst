Command Line App
================

Starting with the version 1.x releases there will be a simple command line application provided with :mod:`pywind`.

Commands
--------

The app uses a command to determine the function to perform. If no command is supplied a list of available commands will be displayed.

============================  ===================================================================
Command                       Description
============================  ===================================================================
**bm_generation_type**        Obtains the current report of electricity generation from the
                              BM Reports website, categorised by Generation Type.
----------------------------  -------------------------------------------------------------------
**bm_system_prices**          Obtains the system electricity prices report from BMReports.
----------------------------  -------------------------------------------------------------------
**bm_unitdata**               Obtains a list of the generation units that are directly monitored
                              by the National Grid.
----------------------------  -------------------------------------------------------------------
**decc_extract**              Obtain the latest DECC monthly planning extract.
----------------------------  -------------------------------------------------------------------
**ofgem_certificate_search**  Performs a search of Ofgem Certificate records. The number of
                              criteria is limited compared with direct use of the module
                              :class:`CertificateSearch`.
----------------------------  -------------------------------------------------------------------
**ofgem_station_search**      Perform a search of Ofgem Station information. The number of
                              criteria is limited compared with direct use of the
                              :class:`StationSearch` class.
----------------------------  -------------------------------------------------------------------
**roc_prices**                Obtain the latest eROC auction information.
============================  ===================================================================

Optional Arguments
------------------

The following optional arguments are also available.

============================  ====================================================================
Argument                      Description
============================  ====================================================================
**--debug**                   Enable debugging mode.
----------------------------  --------------------------------------------------------------------
**--request-debug**           Enable logging of requests made to a remote server
----------------------------  --------------------------------------------------------------------
**--log-filename**            Filename to use for the logfile
----------------------------  --------------------------------------------------------------------
**--date**                    Specify a date for commands that use it. Format is **YYYY-MM-DD**
----------------------------  --------------------------------------------------------------------
**--period**                  Specify a period for commands that need it. Format is **YYYYMM**
----------------------------  --------------------------------------------------------------------
**--scheme**                  The Ofgem Scheme used to filter searches. This is only used by the
                              Ofgem commands. Options are REGO or RO.
----------------------------  --------------------------------------------------------------------
**--export** filename         Export the results. Available formats are CSV, XML and XSLX.
----------------------------  --------------------------------------------------------------------
**--output** filename         Filename to export data to. If not supplied the export will be saved
                              to a generated filename.
----------------------------  --------------------------------------------------------------------
**--input** filename          Process the saved file
----------------------------  --------------------------------------------------------------------
**--save**                    Save the downloaded data to a local file. Filename to use should be
                              specified using the **--original** parameter.
----------------------------  --------------------------------------------------------------------
**--original** filename       The filename to save downloaded into.
============================  ====================================================================

Sample Usage
------------

To download the monthly DECC Planning extract and save it as a CSV file,

.. code::

  $ pywind decc_extract --export csv
  DECC Monthly Planning Extract

  Total of 4896 planning records received for July 2016
  Output will be saved in monthlyextract.csv
  Total of 4896 data rows written
  CSV export to monthlyextract.csv completed

To obtain the latest eROC auction data as an Excel spreadsheet,

.. code::

  $ pywind roc_prices --export xlsx
  eROC Auction Prices

  /usr/lib/python2.7/dist-packages/html5lib/ihatexml.py:262: DataLossWarning: Coercing non-XML name
    warnings.warn("Coercing non-XML name", DataLossWarning)
    Period         Average Price
    ------------   -------------
    200210              47.12
    200301              47.46
    200304              46.76
    200307              48.21
    200310              45.93
    200401              47.46
    200404              49.11
    200407              52.07
    200410              46.12
    200501              47.18
    200504              46.07
  ...
    201606              41.35
    201607              41.65
  Output will be saved in erocprices.xlsx
  XLSX export to erocprices.xlsx completed
