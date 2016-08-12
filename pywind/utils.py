"""
Utility functions used by more than module within pywind.
"""

import requests


def get_or_post_a_url(url, post=False, **kwargs):
    """
    Use the requests library to either get or post to a specified URL. The return code is checked
    and exceptions raised if there has been a redirect or the status code is not 200.

    Args:
         url: The URL to be used.
         post: True if the request should be a POST. Default is False which results in a GET request.
         kwargs: Optional keyword arguments that are passed directly to the requests call.
    Returns:
        The requests object is returned if all checks pass.
    Raises:
        Raises Exception for various errors.
    """
    try:
        if post:
            req = requests.post(url, **kwargs)
        else:
            req = requests.get(url, **kwargs)
    except requests.exceptions.SSLError as err:
        raise Exception("SSL Error\n  Error: {}\n    URL: {}".
                        format(err.message[0], url))
    except requests.exceptions.ConnectionError:
        raise Exception("Unable to connect to the server.\nURL: {}".
                        format(url))
    if req.status_code != 200:
        raise Exception("Request was completed, but status code is not 200.\n"+
                        "URL: {}\nStatus Code: {}".format(url, req.status_code))
    if req.url != url:
        raise Exception("Returned URL was from a different URL than requested.\n" +
                        "Requested: {}\nActual:  {}".format(url, req.url))
    return req
