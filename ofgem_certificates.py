#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'david reid'
__version__ = '0.1'

import argparse

from Ofgem.certificate import OfgemCertificateData

def do_search(month, year):
    ocd = OfgemCertificateData(month = month, year = year)
    if ocd.get_data():
        for c in ocd.certificates:
            print c.as_string()
    else:
        print "No certificates returned."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Ofgem certificates for a given month & year')
    parser.add_argument('month', type=int, action='store', help='Month')
    parser.add_argument('year', type=int, action='store', help='Year')

    args = parser.parse_args()

    do_search(args.month, args.year)
