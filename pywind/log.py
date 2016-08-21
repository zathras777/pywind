# coding=utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

""" PyWind now uses standard python logging :-) """
import logging


def setup_logging(debug=False, stdout=True, request_logging=False,
                  filename=None):
    """ Setup the logging for pywind.

    :param debug: Enable debug level messages (default False)
    :param stdout: Enable logging to stdout (default True)
    :param request_logging: Enable full logging of network requests (default False)
    :param filename: Filename to use for log.
    """
    logger = logging.getLogger('pywind')
    logger.setLevel(logging.INFO if debug is False else logging.DEBUG)

    if stdout:
        stdh = logging.StreamHandler()
        logger.addHandler(stdh)

    if filename is not None:
        fileh = logging.FileHandler(filename)
        filefmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileh.setFormatter(filefmt)
        logger.addHandler(fileh)

    if request_logging:
        try:
            import http.client as http_client
        except ImportError:
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger('requests.packages.urllib3')
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
