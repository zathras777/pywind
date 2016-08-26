"""Planning information provided by the DECC.
.. module:: pywind.decc

.. note::
   Following the announcements in July 2016 about the future of the DECC the future of this module is uncertain.

:Example:

To following code gets the current monthly and extracts the data into :class:DeccRecord objects.

>>> from pywind.decc import MonthlyExtract
>>> extract = MonthlyExtract()
>>> extract.available
{'url': 'https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/545257/Public_Database_-_Jul_2016.csv', 'period': 'July 2016'}
>>> extract.get_data()
True
>>> len(extract)
4898

"""
from .extract import MonthlyExtract, DeccRecord

__all__ = ['MonthlyExtract', 'DeccRecord']
