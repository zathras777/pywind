#coding=utf-8

"""
Class and function to convert Ordnance Survey grid co-ordinates into
latitude/longitude. The code here is taken from movable-type.co.uk
which is (c) Chris Veness 2005-2012.

 - www.movable-type.co.uk/scripts/coordtransform.js
 - www.movable-type.co.uk/scripts/latlong-convert-coords.html

"""

import math


class InvalidScheme(Exception):
    pass


class ConversionError(Exception):
    pass


def _degree_formatter(value, pos, neg, precision):

    def _split_value(value, n = 1):
        i = int(value / n)
        return i, value - i

    fmt = "%s%%0%dd" % (pos if value > 0 else neg, precision)
    value = math.fabs(value)
    degrees, remainder = _split_value(value)
    mins, secs = _split_value(remainder * 60)
    return "%s %02d %s" % (fmt % degrees, mins, ("{0:02.4f}".format(secs * 60)).zfill(7))


class Point(object):
    """ Class to represent and enable conversion between different
        geographic reference schemes.

    """

    SCHEMES = ['gridref', 'osref', 'wgs84', 'osgb36']

    SCHEME_TEXT = {
        'osref':   "UK Grid Reference (numeric E/N)",
        'gridref': "UK Grid Reference (alphanmueric)",
        'wgs84':   "WGS84 latitude/longitude",
        'osgb36':  "OSGB36 latitide/longitude"
    }

    ELLIPSIS = {
        'WGS84': {'a': 6378137, 'b': 6356752.3142, 'f': 1/298.257223563},
        'GRS80': {'a': 6378137, 'b': 6356752.314140, 'f': 1/298.257222101},
        'Airy1830': {'a': 6377563.396, 'b': 6356256.910, 'f': 1/299.3249646},
        'AiryModified': {'a': 6377340.189, 'b': 6356034.448, 'f': 1/299.32496},
        'Intl1924': {'a': 6378388.000, 'b': 6356911.946, 'f': 1/297.0}
    }

    DATUM_TRANSFORM = {
        'toOSGB36': {'tx': -446.448,
                     'ty': 125.157,
                     'tz': -542.060,
                     'rx': -0.1502,
                     'ry': -0.2470,
                     'rz': -0.8421,
                     's': 20.4894},
        'toED50': { 'tx': 89.5,
                    'ty': 93.8,
                    'tz': 123.1,
                    'rx': 0.0,
                    'ry': 0.0,
                    'rz': 0.156,
                    's': -1.2},
        'toIrl1975': {'tx': -482.530,
                      'ty': 130.596,
                      'tz': -564.557,
                      'rx': -1.042,
                      'ry': -0.214,
                      'rz': -0.631,
                      's': -8.150 }
    }


    def __init__(self, scheme, *args):
        stripped = [a.strip() for a in args]
        self.coords = {scheme: stripped}

    def converted_to(self, scheme):
        scheme = scheme.lower()
        if not scheme in self.SCHEMES:
            raise InvalidScheme
        if scheme in self.coords:
            return self.coords[scheme]

        conversions = {
            'gridref':  {
                'osref': [self._gridref_from_osref],
                'osgb36': [self._osref_from_osgb36,
                           self._gridref_from_osref],
                'wgs84': [self._osgb36_from_wgs84,
                          self._osref_from_osgb36,
                          self._gridref_from_osref]
            },
            'osref':    {
                'gridref': [self._osref_from_gridref],
                'osgb36': [self._osref_from_osgb36],
                'wgs84':  [self._osgb36_from_wgs84,
                           self._osref_from_osgb36]
            },
            'osgb36':   {
                'gridref': [self._osref_from_gridref,
                            self._osgb36_from_osref],
                'osref':    [self._osgb36_from_osref],
                'wgs84':    [self._osgb36_from_wgs84]
            },
            'wgs84':    {
                'gridref': [self._osref_from_gridref,
                            self._osgb36_from_osref,
                            self._wgs84_from_osgb36],
                'osref': [self._osgb36_from_osref,
                          self._wgs84_from_osgb36],
                'osgb36': [self._wgs84_from_osgb36]
            },
        }

        for poss, how in conversions[scheme].iteritems():
            if poss in self.coords:
                for fn in how:
                    if fn() != True:
                        return False
                break
        return True

    def pretty_string(self, scheme):
        if not scheme in self.coords:
            if self.converted_to(scheme) is False:
                raise ConversionError
        if scheme in ['gridref', 'osref']:
            return self.coords[scheme]
        return [_degree_formatter(self.coords[scheme][0], 'N','S', 2),
                _degree_formatter(self.coords[scheme][1], 'W','E', 3)]

    def dump(self):
        for k,v in self.coords.iteritems():
            print("  %s: %s" % (self.SCHEME_TEXT[k], self.pretty_string(k)))

    def __getitem__(self, value):
        if not value.lower() in self.SCHEMES:
            raise KeyError
        if self.converted_to(value.lower()):
            return self.coords[value.lower()]

        raise ConversionError

    # Conversion routines and functions only below this line.

    def _osref_from_gridref(self):
        if not 'gridref' in self.coords:
            return False

        input = self.coords['gridref'][0]
        l1 = ord(input[0].upper()) - ord("A")
        l2 = ord(input[1].upper()) - ord("A")

        # shuffle down letters after 'I' since 'I' is not used in grid:
        if l1 > 7:
            l1 -= 1
        if l2 > 7:
            l2 -= 1

        e = str(((l1-2) % 5) * 5 + (l2 % 5))
        n = str(int((19 - math.floor(l1 / 5) * 5) - math.floor(l2 / 5)))

        gridref = input[2:]
        e += gridref[:int(len(gridref) / 2)]
        n += gridref[int(len(gridref) / 2):]

        # Calculate accuracy to allow us to specify the centre of the
        # area designated.
        a = 1 * int(math.pow(10, 6-len(n)))
        n = int(math.pow(10, 6-len(n))) * int(n) + a/2
        e = int(math.pow(10, 6-len(e))) * int(e) + a/2
        self.coords['osref'] = [int(e), int(n)]
        return True

    def _gridref_from_osref(self):
        if not 'osref' in self.coords:
            return False

        input = self.coords['osref']

        # get the 100km-grid indices
        e100k = math.floor(input[0] / 100000)
        n100k = math.floor(input[1] / 100000)

        if (e100k < 0 or e100k > 6 or n100k < 0 or n100k > 12):
            return False

        # translate those into numeric equivalents of the grid letters
        l1 = (19 - n100k) - (19 - n100k) % 5 + math.floor((e100k + 10) / 5)
        l2 = (19 - n100k) * 5 % 25 + e100k % 5
        #print(l1, l2)

        # compensate for skipped 'I' and build grid letter-pairs
        if (l1 > 7):
            l1 += 1
        if (l2 > 7):
            l2 += 1


        letters = chr(int(l1) + ord('A')) + chr(int(l2) + ord('A'))
        # strip 100km-grid indices from easting & northing, and reduce precision
        e = math.floor((input[0] % 100000)) # / math.pow(10, 5 - digits / 2))
        n = math.floor((input[1] % 100000)) # / math.pow(10, 5 - digits / 2))
        self.coords['gridref'] = "%s%d%d" % (letters, e, n)
        return True

    def _osref_from_osgb36(self):
        if not 'osgb36' in self.coords:
            return False

        input = [math.radians(self.coords['osgb36'][0]),
                 math.radians(self.coords['osgb36'][1])]

        a = 6377563.396                   # Airy 1830 major & minor semi-axes
        b = 6356256.910                   # Airy 1830 major & minor semi-axes
        F0 = 0.9996012717                 # NatGrid scale factor on central meridian
        lat0 = math.radians(49)           # NatGrid true origin is 49ºN
        lon0 = math.radians(-2)           # NatGrid true origin is 2ºW
        N0 = -100000                      # Nothing of true origin (metres)
        E0 = 400000                       # Easting of true origin (metres)
        e2 = 1 - (b * b) / (a * a)        # eccentricity squared

        n = (a - b) / (a + b)
        n2 = n * n
        n3 = n * n * n

        cosLat = math.cos(input[0])
        sinLat = math.sin(input[0])
        nu = a * F0 / math.sqrt(1 - e2 * sinLat * sinLat) # transverse radius of curvature
        rho = a * F0 * (1 - e2) / math.pow(1 - e2 * sinLat * sinLat, 1.5) # meridional radius of curvature
        eta2 = nu / rho - 1

        Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (input[0]-lat0)
        Mb = (3 * n + 3 * n * n + (21/8) * n3) * math.sin(input[0] - lat0) * math.cos(input[0] + lat0)
        Mc = ((15/8) * n2 + (15/8) * n3) * math.sin(2*(input[0] - lat0)) * math.cos(2*(input[0] + lat0))
        Md = (35/24) * n3 * math.sin(3*(input[0] - lat0)) * math.cos(3*(input[0] + lat0))
        M = b * F0 * (Ma - Mb + Mc - Md)   # meridional arc

        cos3lat = cosLat * cosLat * cosLat
        cos5lat = cos3lat * cosLat * cosLat
        tan2lat = math.tan(input[0]) * math.tan(input[0])
        tan4lat = tan2lat * tan2lat

        I = M + N0
        II = (nu/2) * sinLat * cosLat
        III = (nu/24) * sinLat * cos3lat * (5 - tan2lat + 9 * eta2)
        IIIA = (nu/720) * sinLat * cos5lat * (61-58 * tan2lat + tan4lat)
        IV = nu * cosLat
        V = (nu/6) * cos3lat * (nu/rho-tan2lat)
        VI = (nu/120) * cos5lat * (5 - 18 * tan2lat + tan4lat + 14 * eta2 - 58 * tan2lat * eta2)

        dLon = input[1]-lon0
        dLon2 = dLon * dLon
        dLon3 = dLon2 * dLon
        dLon4 = dLon3 * dLon
        dLon5 = dLon4 * dLon
        dLon6 = dLon5 * dLon

        N = I + II * dLon2 + III * dLon4 + IIIA * dLon6
        E = E0 + IV * dLon + V * dLon3 + VI * dLon5
        self.coords['osref'] = [E, N]
        return True

    def _osgb36_from_osref(self):
        if not 'osref' in self.coords:
            return False

        input = self.coords['osref']

        # Airy 1830 major & minor semi-axes
        a = 6377563.396
        b = 6356256.910
        # NatGrid scale factor (for central meridian)
        F0 = 0.9996012717
        # NatGrid true origin
        lat0 = 49 * math.pi / 180.0
        lon0 = -2 * math.pi / 180.0
        # northing & easting of true origin (metres)
        N0 = -100000
        E0 = 400000

        e2 = 1 - (b*b)/(a*a) # eccentricity squared
        n = (a-b)/(a+b)
        n2 = n*n
        n3 = n*n*n

        lat = lat0
        M = 0

        while True:
            lat += (input[1]-N0-M) / (a*F0)

            Ma = (1 + n + (5/4) * n2 + (5/4) * n3) * (lat-lat0)
            Mb = (3 * n + 3 * n * n + (21 / 8) * n3) * math.sin(lat-lat0) * math.cos(lat + lat0)
            Mc = ((15 / 8) * n2 + (15/8)*n3) * math.sin(2*(lat-lat0)) * math.cos(2 * (lat + lat0))
            Md = (35 / 24) * n3 * math.sin(3 * (lat-lat0)) * math.cos(3 * (lat + lat0))
            M = b * F0 * (Ma - Mb + Mc - Md) # meridional arc
            # loop until  < 0.01mm
            if input[1]-N0-M < 0.00001:
                break

        cosLat = math.cos(lat)
        sinLat = math.sin(lat)
        # transverse radius of curvature
        nu = a * F0 / math.sqrt(1 - e2 * sinLat * sinLat)
        # meridional radius of curvature
        rho = a * F0 * (1 - e2) / math.pow(1 - e2 * sinLat * sinLat, 1.5)
        eta2 = nu / rho - 1

        tanLat = math.tan(lat)
        tan2lat = tanLat * tanLat
        tan4lat = tan2lat * tan2lat
        tan6lat = tan4lat * tan2lat
        secLat = 1.0 / cosLat
        nu3 = nu*nu*nu
        nu5 = nu3*nu*nu
        nu7 = nu5*nu*nu

        VII = tanLat/(2*rho*nu)
        VIII = tanLat/(24*rho*nu3)*(5+3*tan2lat+eta2-9*tan2lat*eta2)
        IX = tanLat/(720*rho*nu5)*(61+90*tan2lat+45*tan4lat)
        X = secLat/nu
        XI = secLat/(6*nu3)*(nu/rho+2*tan2lat)
        XII = secLat/(120*nu5)*(5+28*tan2lat+24*tan4lat)
        XIIA = secLat/(5040*nu7)*(61+662*tan2lat+1320*tan4lat+720*tan6lat)

        dE = (input[1] - E0)
        dE2 = dE*dE
        dE3 = dE2*dE
        dE4 = dE2*dE2
        dE5 = dE3*dE2
        dE6 = dE4*dE2
        dE7 = dE5*dE2

        lat -= VII*dE2 + VIII*dE4 - IX*dE6
        lon = lon0 + X*dE - XI*dE3 + XII*dE5 - XIIA*dE7
        self.coords['osgb36'] = [float("%.06f" % math.degrees(lat)), float("%.06f" % math.degrees(lon))]
        return True

    def _wgs84_from_osgb36(self):
        return self._convert('osgb36', 'wgs84')

    def _osgb36_from_wgs84(self):
        return self._convert('wgs84', 'osgb36')

    def _convert(self, scheme1, scheme2):
        if not scheme1 in self.coords:
            return False

        if scheme1 == 'osgb36' and scheme2 == 'wgs84':
            t = {}
            for k,v in self.DATUM_TRANSFORM['toOSGB36'].iteritems():
                t[k] = -v
            e1 = self.ELLIPSIS['Airy1830']
            e2 = self.ELLIPSIS['WGS84']
        elif scheme1 == 'wgs84' and scheme2 == 'osgb36':
            e1 = self.ELLIPSIS['WGS84']
            t = self.DATUM_TRANSFORM['toOSGB36']
            e2 = self.ELLIPSIS['Airy1830']
        self.coords[scheme2] = self._convertEllipsoid(e1, t, e2,
                                                      math.radians(self.coords[scheme1][0]),
                                                      math.radians(self.coords[scheme1][1]))

        return True

    def _convertEllipsoid(self, e1, t, e2, lat, lon):
        # 1: convert polar to cartesian coordinates (using ellipse 1)
        a = e1['a']
        b = e1['b']

        sinPhi = math.sin(lat)
        cosPhi = math.cos(lat)
        sinLambda = math.sin(lon)
        cosLambda = math.cos(lon)
        H = 24.7

        eSq = (a*a - b*b) / (a*a)
        nu = a / math.sqrt(1 - eSq*sinPhi*sinPhi)

        x1 = (nu+H) * cosPhi * cosLambda
        y1 = (nu+H) * cosPhi * sinLambda
        z1 = ((1-eSq)*nu + H) * sinPhi

        # 2: apply helmert transform using appropriate params
        tx = t['tx']
        ty = t['ty']
        tz = t['tz']
        rx = math.radians(t['rx']/3600) # normalise seconds to radians
        ry = math.radians(t['ry']/3600)
        rz = math.radians(t['rz']/3600)
        s1 = t['s']/1e6 + 1    # normalise ppm to (s+1)

        # apply transform
        x2 = tx + x1*s1 - y1*rz + z1*ry
        y2 = ty + x1*rz + y1*s1 - z1*rx
        z2 = tz - x1*ry + y1*rx + z1*s1

        # 3: convert cartesian to polar coordinates (using ellipse 2)
        a = e2['a']
        b = e2['b']
        precision = 4 / a  # results accurate to around 4 metres

        eSq = (a*a - b*b) / (a*a)
        p = math.sqrt(x2*x2 + y2*y2)
        phi = math.atan2(z2, p*(1-eSq))
        phiP = 2 * math.pi

        while math.fabs(phi-phiP) > precision:
            nu = a / math.sqrt(1 - eSq*math.sin(phi)*math.sin(phi))
            phiP = phi
            phi = math.atan2(z2 + eSq*nu*math.sin(phi), p)

        lmbda = math.atan2(y2, x2)
#        H = p/math.cos(phi) - nu

        return [math.degrees(phi), math.degrees(lmbda)]
