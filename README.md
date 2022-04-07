pywind
======

Documentation: [![Documentation Status](https://readthedocs.org/projects/pywind/badge/?version=latest)](http://pywind.readthedocs.io/en/latest/?badge=latest)

The pywind module is intended to provide a python module that can be used
to access online information related to Renewable Energy in the UK.

Following an extensive rewrite in Aug 2016 documentation is now available at [http://pywind.readthedocs.io/en/latest/]

7th April 2022 Update
---------------------

Ofgem Certificates can be retrieved but the scheme cannot be set or it will fail :-(

The period can be set and works as expected. I will try to debug this further over the next week or so. I have fixed a few minor issues and the XML export works again.

5th April 2022 Update
---------------------

This project isn't dead, just resting :-)

I've spent some time and fixed some bugs that prevented it working. Here's the summary,

- removed ROC prices as they're no longer available
- removed the DECC planning data as the URL no longer exists
- Ofgem certificate retrieval is presently broken :-(
- Adjusted Elexon API to work
- Started removing Python 2 support
- Removed the CI tag as I need to update it

The issue with Ofgem is that when trying to actually get the data it redirects to an error page saying the session has expired. If anyone knows what's going on then let me know :-)

I will try and get a release pushed once the Ofgem certificate issue is resolved.