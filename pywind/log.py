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
