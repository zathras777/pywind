""" PyWind now uses standard python logging :-) """
import logging


def setup_logging(debug=False, stdout=True, request_logging=False):
    """ Setup the logging for pywind. """
    logger = logging.getLogger('pywind')
    logger.setLevel(logging.INFO if debug is False else logging.DEBUG)

    if stdout:
        stdh = logging.StreamHandler()
        logger.addHandler(stdh)

    if request_logging:
        try:
            import http.client as http_client
        except ImportError:
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger('requests.packages.urllib3')
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
