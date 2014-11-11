#! /usr/bin/env python
# coding=utf-8
#
# Copyright 2013 david reid <zathrasorama@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pywind.ofgem import CertificateSearch
cs = CertificateSearch()
cs.set_month(1)
cs.set_year(2012)
cs.filter_technology('off-shore')
cs.get_data()
print(str(len(cs))+' certificates found. This is the first: ')
print(cs.certificates[0].as_string())