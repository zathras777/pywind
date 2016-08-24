import math


def decimal_to_degrees(num, seps=None):
    """ Given a float value and an optional set of seperators, return a formatted string.

    If the seperator has a precision value required that differs from the default of 2,
    then it should be prefixed with a colon, e.g. 3:$ would give a seperator of a $ character
    after a 3 digit number.

    :param num: The float value to parse
    :param seps: An optional list of seperators to use.
    """
    rv_str = ''
    for sep in seps or [" ", "'", ""]:
        fmt = "{:02.0f}{}" if ':' not in sep else "{{:0{}.0f}}{}".format(*sep.split(':', 1))
        rv_str += fmt.format(math.floor(num), sep)
        num = (num % 1) * 60
    return rv_str.strip()


def latlon_as_string(lat, lon):
    """ Given a numeric lat/lon, convert into "pretty strings".

    :param lat: Latitude
    :param lon: Longitude
    :rtype: str
    """
    if not isinstance(lat, (int, float)):
        raise ValueError("Latitude must be an integer or float")
    if not isinstance(lon, (int, float)):
        raise ValueError("Longitude must be an integer or float")

    return "{}{} {}{}".format(
        'S' if lat < 0 else 'N',
        decimal_to_degrees(math.fabs(lat)),
        'W' if lon < 0 else 'E',
        decimal_to_degrees(math.fabs(lon), ["3: ", "'", " "])
    )
