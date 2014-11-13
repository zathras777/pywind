# -*- coding: utf-8 -*-
"""Run all the sample scripts in test mode
"""

import importlib
import sys
import os.path
from datetime import datetime
# this script must be in the same directory as all the test scripts
sys.path.insert(0,os.path.dirname(__file__))

def logmessage(txt):
    with open('abatch.log','a') as logfile:
        logfile.write(txt)
    print(txt)
    
def runtest(testname, testargs):
    for i in range(1,4):
        try:
            test = importlib.import_module(testname)
            if 'test' in dir(test):
                test.test(testargs)
            logmessage('\n %s finished without an Exception on attempt %d' % (testname, i) )
            break
        except Exception as e:
            logmessage('\n %s attempt %d had Exception: %s' % (testname, i, str(e) ) )

testlist = [
        ['bm_unit_list', [] ],
        ['bmdata', [] ],
        ['decc', [] ],
        ['derived_unit_data', [] ],
        ['gendata', [] ],
        ['offwind', [] ],
        ['powerpack', [] ],
        ['rocprice', [] ],
        # and now the slower ones
        ['annual_output', ['--year', '2014', '--technology', 'off' ] ],
        ['ofgem_certificate_search', [] ],
        ['ofgem_station_search', [] ],
        ['onestation', [] ],
        # and this one is producing the wrong numbers:
        #['capacity_ro', ['--name','ormonde','--start','Jan-2014','--end','Apr-2014'] ],
        ]

logmessage("\n\n =================================" +
           "====================================" +
           "\n New test batch started %s \n" %
           datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S') +
           "==================================" +
           "====================================\n"
           )

for thistest in testlist:
    logmessage("\n =============================\n Starting %s \n" % thistest[0])
    runtest(thistest[0], thistest[1])
