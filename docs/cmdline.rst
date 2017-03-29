Command Line App
================

Starting with the version 1.x releases there will be a simple command line application provided with :mod:`pywind`.

Commands
--------

The app uses a command to determine the function to perform. If no command is supplied a list of available commands will be displayed.

.. code::

  $ pywind

    decc_extract                    DECC Monthly Planning Extract
    elexon_b1320                    Congestion Management Measures Countertrading
    elexon_b1330                    Congestion Management Measures Costs of Congestion Management Service
    elexon_b1420                    Installed Generation Capacity per Unit
    elexon_bm_data                  Derived System Prices from Elexon
    elexon_bm_unit                  Balancing Mechanism Unit information from Elexon
    elexon_generation_inst          Generation Data from the Elexon Data Portal
    elexon_sbp                      Derived System Prices from Elexon
    ofgem_certificate_search        Ofgem Certificate Search
    ofgem_station_search            Ofgem Station Search
    roc_prices                      eROC Auction Prices


============================  ===================================================================
Command                       Description
============================  ===================================================================
----------------------------  -------------------------------------------------------------------
**decc_extract**              Obtain the latest DECC monthly planning extract.
----------------------------  -------------------------------------------------------------------
**elexon_bm1320**             Extract data from the Elexon API
**elexon_bm1330**             Extract data from the Elexon API
**elexon_bm1420**             Extract data from the Elexon API
----------------------------  -------------------------------------------------------------------
**elexon_bm_data**            Get derived data for the Balancing Mechanism using the Elexon API
----------------------------  -------------------------------------------------------------------
**elexon_bm_unit**            Balancing Mechanism unit data from Elexon
----------------------------  -------------------------------------------------------------------
**elexon_generation_inst**    Generation volume by fuel type from Elexon
----------------------------  -------------------------------------------------------------------
**elexon_sbp**                System Buy & Sell price data from Elexon
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
**--apikey**                  The elexon API key. If a filename is specified the contents will be
                              read and used.
----------------------------  --------------------------------------------------------------------
**--fromdate**                First date to filter
----------------------------  --------------------------------------------------------------------
**--todate**                  Last date to filter
----------------------------  --------------------------------------------------------------------
**--year**                    Filter for a year. Only used by elexon commands
----------------------------  --------------------------------------------------------------------
**--month**                   Filter for a month. Only used for elexon commands.
----------------------------  --------------------------------------------------------------------
**--unit-type**               Letter specifying the type of unit. Only used for elexon_bm_unit.
----------------------------  --------------------------------------------------------------------
**--period**                  Specify a period for commands that need it. Format is **YYYYMM**
----------------------------  --------------------------------------------------------------------
**--all-periods**             Try and get data for all available periods
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


.. code::

  $pywind elexon_sbp --apikey elexon.api.key

  Reading API Key from elexon.api.key

  Derived System Prices from Elexon
  =================================

  System adjustments are included in the figures shown below where '*' is shown.

  Date              Settlement Period    Sell Price       Buy Price        Adj?
  ---------------  --------------------  ---------------  ---------------  ----
  2017 Mar 28               1                    29.0020          29.0020
  2017 Mar 28               2                    29.0000          29.0000
  2017 Mar 28               3                    29.1100          29.1100
  2017 Mar 28               4                    29.1119          29.1119
  2017 Mar 28               5                    29.1124          29.1124
  2017 Mar 28               6                    28.4936          28.4936
  2017 Mar 28               7                    29.4324          29.4324
  2017 Mar 28               8                    29.1132          29.1132
  2017 Mar 28               9                    29.1100          29.1100
  2017 Mar 28               10                   29.0874          29.0874
  2017 Mar 28               11                   29.0534          29.0534
  2017 Mar 28               12                   29.3217          29.3217
  2017 Mar 28               13                   30.1473          30.1473
  2017 Mar 28               14                   29.9129          29.9129
  2017 Mar 28               15                   30.3665          30.3665
  2017 Mar 28               16                  158.9650         158.9650
  2017 Mar 28               17                  160.0000         160.0000
  2017 Mar 28               18                  151.1268         151.1268
  2017 Mar 28               19                   33.0000          33.0000
  2017 Mar 28               20                  110.0000         110.0000
  2017 Mar 28               21                   31.3086          31.3086
  2017 Mar 28               22                   30.5500          30.5500
  2017 Mar 28               23                   30.5593          30.5593
  2017 Mar 28               24                   30.3133          30.3133
  2017 Mar 28               25                   30.2979          30.2979
  2017 Mar 28               26                   30.1066          30.1066
  2017 Mar 28               27                   30.0175          30.0175
  2017 Mar 28               28                   29.7841          29.7841
  2017 Mar 28               29                   30.3187          30.3187
  2017 Mar 28               30                   30.5830          30.5830
  2017 Mar 28               31                   30.6778          30.6778
  2017 Mar 28               32                   31.0000          31.0000
  2017 Mar 28               33                   65.5367          65.5367
  2017 Mar 28               34                  114.4993         114.4993
  2017 Mar 28               35                  113.1707         113.1707
  2017 Mar 28               36                   76.6555          76.6555
  2017 Mar 28               37                   30.7676          30.7676
  2017 Mar 28               38                   30.9852          30.9852
  2017 Mar 28               39                   31.1493          31.1493
  2017 Mar 28               40                   31.1500          31.1500
  2017 Mar 28               41                   31.1500          31.1500
  2017 Mar 28               42                   31.0000          31.0000
  2017 Mar 28               43                   31.0000          31.0000
  2017 Mar 28               44                   29.5678          29.5678
  2017 Mar 28               45                   30.1783          30.1783
  2017 Mar 28               46                   30.7737          30.7737
  2017 Mar 28               47                   51.9000          51.9000
  2017 Mar 28               48                   30.5000          30.5000


Available Commands
------------------

Some commands allow additional filtering:

.. code::

  $ pywind elexon_sbp --apikey elexon.api.key --period 5
  Reading API Key from elexon.api.key

  Derived System Prices from Elexon
  =================================

  System adjustments are included in the figures shown below where '*' is shown.

    Date              Settlement Period    Sell Price       Buy Price        Adj?
    ---------------  --------------------  ---------------  ---------------  ----
    2017 Mar 28               5                    29.1124          29.1124


.. code::

  $ pywind elexon_bm_unit --apikey elexon.api.key --unit-type I

  Total of 373 units


    NGC ID        BM ID         Active ?  BM Type                         Lead Party Name
    ------------  ------------  --------  ------------------------------  --------------------------------------------------
    EAD-BRTN1     I_EAD-BRTN1      Y      I, Interconnector               NGET plc
    EAD-EWIC1     I_EAD-EWIC1      Y      I, Interconnector               NGET plc
    EAD-FRAN1     I_EAD-FRAN1      Y      I, Interconnector               NGET plc
    EAD-MOYL1     I_EAD-MOYL1      Y      I, Interconnector               NGET plc
    EAD-SCOT1     I_EAD-SCOT1      Y      I, Interconnector               NGET plc
    ...
    iMD-SSIR1     I_IMD_SSIR1      Y      I, Interconnector               SSE (IRELAND) LIMITED
