#coding=utf-8

"""
Class and function to convert Ordnance Survey grid co-ordinates into
latitude/longitude. The code here is taken from movable-type.co.uk
which is (c) Chris Veness 2005-2012.

 - www.movable-type.co.uk/scripts/coordtransform.js
 - www.movable-type.co.uk/scripts/latlong-convert-coords.html

"""

import math

from pywind.ofgem.utils import viewitems


class LatLon(object):
    OSGB36 = 1
    WGS84 = 2

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

    def __init__(self, lat, lon, scheme):
        self.lat = lat
        self.lon = lon
        self.scheme = scheme

    def _nearest(self, n):
        if n % 1 >= 0.5:
            return math.ceil(n)
        return math.floor(n)

    def _parts(self, n):
        n = math.fabs(n)
        d = math.floor(n)
        m0 = (n - d) * 60
        m = math.floor(m0)
        s = (m0 - m) * 60
        return [d, m, s]

    def _text(self, n):
        p = self._parts(n)
        return "%d %02d'%.04f\"" % (p[0], p[1], p[2])

    def as_string(self):
        NS = 'S' if self.lat < 0 else 'N'
        EW = 'W' if self.lon < 0 else 'E'
        return "%s%s %s%s" % (NS, self._text(self.lat),
                              EW, self._text(self.lon))

    def convert(self, scheme):
        if scheme == self.scheme:
            return

        if self.scheme == self.OSGB36 and scheme == self.WGS84:
            txFromOSGB36 = {}
            for k,v in viewitems(self.DATUM_TRANSFORM['toOSGB36']):
                txFromOSGB36[k] = -v
            self.convertEllipsoid(self.ELLIPSIS['Airy1830'],
                                  txFromOSGB36,
                                  self.ELLIPSIS['WGS84'])
            self.scheme = scheme
        elif self.scheme == self.WGS84 and scheme == self.OSGB36:
            self.convertEllipsoid(self.ELLIPSIS['WGS84'],
                                  self.DATUM_TRANSFORM['toOSGB36'],
                                  self.ELLIPSIS['Airy1830'])
            self.scheme = scheme

    def convertEllipsoid(self, e1, t, e2):

        # 1: convert polar to cartesian coordinates (using ellipse 1)

        lat = math.radians(self.lat)
        lon = math.radians(self.lon)

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
        precision = 4 / a # results accurate to around 4 metres

        eSq = (a*a - b*b) / (a*a)
        p = math.sqrt(x2*x2 + y2*y2)
        phi = math.atan2(z2, p*(1-eSq))
        phiP = 2 * math.pi

        while math.fabs(phi-phiP) > precision:
            nu = a / math.sqrt(1 - eSq*math.sin(phi)*math.sin(phi))
            phiP = phi
            phi = math.atan2(z2 + eSq*nu*math.sin(phi), p)

        lmbda = math.atan2(y2, x2)
        H = p/math.cos(phi) - nu

        self.lat = math.degrees(phi)
        self.lon = math.degrees(lmbda)


def osGridToLatLong(E, N):
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

    lat=lat0
    M=0

    while True:
        lat += (N-N0-M) / (a*F0)

        Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat-lat0)
        Mb = (3*n + 3*n*n + (21/8)*n3) * math.sin(lat-lat0) * math.cos(lat+lat0)
        Mc = ((15/8)*n2 + (15/8)*n3) * math.sin(2*(lat-lat0)) * math.cos(2*(lat+lat0))
        Md = (35/24)*n3 * math.sin(3*(lat-lat0)) * math.cos(3*(lat+lat0))
        M = b * F0 * (Ma - Mb + Mc - Md) # meridional arc
        # ie until < 0.01mm
        if N-N0-M < 0.00001:
            break

    cosLat = math.cos(lat)
    sinLat = math.sin(lat)
    # transverse radius of curvature
    nu = a*F0/math.sqrt(1-e2*sinLat*sinLat)
    # meridional radius of curvature
    rho = a*F0*(1-e2)/math.pow(1-e2*sinLat*sinLat, 1.5)
    eta2 = nu/rho-1

    tanLat = math.tan(lat)
    tan2lat = tanLat*tanLat
    tan4lat = tan2lat*tan2lat
    tan6lat = tan4lat*tan2lat
    secLat = 1/cosLat
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

    dE = (E-E0)
    dE2 = dE*dE
    dE3 = dE2*dE
    dE4 = dE2*dE2
    dE5 = dE3*dE2
    dE6 = dE4*dE2
    dE7 = dE5*dE2

    lat -= VII*dE2 + VIII*dE4 - IX*dE6
    lon = lon0 + X*dE - XI*dE3 + XII*dE5 - XIIA*dE7

    return LatLon(math.degrees(lat), math.degrees(lon), LatLon.OSGB36)


"""
# Convert (OSGB36) latitude/longitude to Ordnance Survey grid reference easting/northing coordinate
#
# @param {LatLon} point: OSGB36 latitude/longitude
# @return {OsGridRef} OS Grid Reference easting/northing
def latLongToOsGrid() = function(point) {
  var lat = point.lat().toRad();
  var lon = point.lon().toRad();

  var a = 6377563.396, b = 6356256.910;          // Airy 1830 major & minor semi-axes
  var F0 = 0.9996012717;                         // NatGrid scale factor on central meridian
  var lat0 = (49).toRad(), lon0 = (-2).toRad();  // NatGrid true origin is 49ºN,2ºW
  var N0 = -100000, E0 = 400000;                 // northing & easting of true origin, metres
  var e2 = 1 - (b*b)/(a*a);                      // eccentricity squared
  var n = (a-b)/(a+b), n2 = n*n, n3 = n*n*n;

  var cosLat = Math.cos(lat), sinLat = Math.sin(lat);
  var nu = a*F0/Math.sqrt(1-e2*sinLat*sinLat);              // transverse radius of curvature
  var rho = a*F0*(1-e2)/Math.pow(1-e2*sinLat*sinLat, 1.5);  // meridional radius of curvature
  var eta2 = nu/rho-1;

  var Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat-lat0);
  var Mb = (3*n + 3*n*n + (21/8)*n3) * Math.sin(lat-lat0) * Math.cos(lat+lat0);
  var Mc = ((15/8)*n2 + (15/8)*n3) * Math.sin(2*(lat-lat0)) * Math.cos(2*(lat+lat0));
  var Md = (35/24)*n3 * Math.sin(3*(lat-lat0)) * Math.cos(3*(lat+lat0));
  var M = b * F0 * (Ma - Mb + Mc - Md);              // meridional arc

  var cos3lat = cosLat*cosLat*cosLat;
  var cos5lat = cos3lat*cosLat*cosLat;
  var tan2lat = Math.tan(lat)*Math.tan(lat);
  var tan4lat = tan2lat*tan2lat;

  var I = M + N0;
  var II = (nu/2)*sinLat*cosLat;
  var III = (nu/24)*sinLat*cos3lat*(5-tan2lat+9*eta2);
  var IIIA = (nu/720)*sinLat*cos5lat*(61-58*tan2lat+tan4lat);
  var IV = nu*cosLat;
  var V = (nu/6)*cos3lat*(nu/rho-tan2lat);
  var VI = (nu/120) * cos5lat * (5 - 18*tan2lat + tan4lat + 14*eta2 - 58*tan2lat*eta2);

  var dLon = lon-lon0;
  var dLon2 = dLon*dLon, dLon3 = dLon2*dLon, dLon4 = dLon3*dLon, dLon5 = dLon4*dLon, dLon6 = dLon5*dLon;

  var N = I + II*dLon2 + III*dLon4 + IIIA*dLon6;
  var E = E0 + IV*dLon + V*dLon3 + VI*dLon5;

  return new OsGridRef(E, N);
}
"""

