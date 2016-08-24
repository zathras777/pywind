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

"""
The Ordnane Survey publishes a comprehensive document on their co-ordinate
systems which is available at

https://www.ordnancesurvey.co.uk/docs/support/guide-coordinate-systems-great-britain.pdf

The conversion routines used in the Coord class are from blog posts by Hannah Fry and
remain her copyright.

- http://www.hannahfry.co.uk/blog/2012/02/01/converting-latitude-and-longitude-to-british-national-grid
- http://www.hannahfry.co.uk/blog/2012/02/01/converting-british-national-grid-to-latitude-and-longitude-ii

"""

from math import pi, sin, cos, sqrt, tan
from numpy.ma import arctan2


class Coord(object):
    """Each instance of the Coord class represents a single co-ordinate, which
    can be craeted using either WGS84 or OSGB36. Conversions between the 2
    systems are done as needed on demand.
    """
    def __init__(self, e_or_lat, n_or_lon):
        """Create the object with the initial point. Values should be supplied as
        float values, but integers can also be used. Providing anything else will
        result in a ValueError exception.

        :param e_or_lat: Either the Easting or Latitude.
        :param n_or_lon: Either the Northing or Longitude
        :raises: ValueError
        """
        if not isinstance(e_or_lat, (int, float)):
            raise ValueError("Easting/Latitude value should be an int or float")
        if not isinstance(n_or_lon, (int, float)):
            raise ValueError("Northing/Longitude value should be an int or float")
        self.easting, self.northing = None, None
        self.lat, self.lon = None, None
        if e_or_lat < 0 or e_or_lat > 90.0:
            self.easting = e_or_lat
            self.northing = n_or_lon
        else:
            self.lat = e_or_lat
            self.lon = n_or_lon

    def as_wgs84(self, precision=None):
        """Return the co-ordinate as WGS84 latitude, longitude pair.

        :param precision: The number of decimal places to return. Defaults to 4.
        :rtype: float, float
        """
        if self.lat is None or self.lon is None:
            if self._OSGB36toWGS84() is False:
                raise ValueError("Unable to convert to WGS84")
        prec = precision or 4
        return round(self.lat, prec), round(self.lon, prec)

    def as_osgb36(self, precision=None):
        """Return the co-ordinate as OSGB36 Easting, Northing pair.

        :param precision: The number of decimal places to return. Defaults to 3.
        :rtype: float, float
        """
        if self.easting is None or self.northing is None:
            if self._WGS84toOSGB36() is False:
                raise ValueError("Unable to convert to OSGB36")
        prec = precision or 3
        return round(self.easting, prec), round(self.northing, prec)

    # Private functions

    def _OSGB36toWGS84(self):
        """ Convert between OSGB36 and WGS84. If we already have values available, we just return them.

        :rtype: float, float
        """
        if self.easting is None or self.northing is None:
            return False

        #E, N are the British national grid coordinates - eastings and northings
        a, b = 6377563.396, 6356256.909     #The Airy 180 semi-major and semi-minor axes used for OSGB36 (m)
        F0 = 0.9996012717                   #scale factor on the central meridian
        lat0 = 49 * pi / 180                    #Latitude of true origin (radians)
        lon0 = -2 * pi / 180                    #Longtitude of true origin and central meridian (radians)
        N0, E0 = -100000, 400000            #Northing & easting of true origin (m)
        e2 = 1 - (b*b)/(a*a)                #eccentricity squared
        n = (a-b) / (a+b)

        #Initialise the iterative variables
        lat, M = lat0, 0

        while self.northing - N0 - M >= 0.00001: #Accurate to 0.01mm
            lat += (self.northing - N0 - M) / (a * F0)
            M1 = (1 + n + (5./4)*n**2 + (5./4)*n**3) * (lat-lat0)
            M2 = (3*n + 3*n**2 + (21./8)*n**3) * sin(lat-lat0) * cos(lat+lat0)
            M3 = ((15./8)*n**2 + (15./8)*n**3) * sin(2*(lat-lat0)) * cos(2*(lat+lat0))
            M4 = (35./24)*n**3 * sin(3*(lat-lat0)) * cos(3*(lat+lat0))
            #meridional arc
            M = b * F0 * (M1 - M2 + M3 - M4)

        #transverse radius of curvature
        nu = a * F0 / sqrt(1 - e2 * sin(lat) ** 2)

        #meridional radius of curvature
        rho = a * F0 * (1 - e2) * (1 - e2 * sin(lat) ** 2) ** (-1.5)
        eta2 = nu / rho-1

        secLat = 1./cos(lat)
        VII = tan(lat)/(2*rho*nu)
        VIII = tan(lat)/(24*rho*nu**3)*(5+3*tan(lat)**2+eta2-9*tan(lat)**2*eta2)
        IX = tan(lat)/(720*rho*nu**5)*(61+90*tan(lat)**2+45*tan(lat)**4)
        X = secLat/nu
        XI = secLat/(6*nu**3)*(nu/rho+2*tan(lat)**2)
        XII = secLat/(120*nu**5)*(5+28*tan(lat)**2+24*tan(lat)**4)
        XIIA = secLat/(5040*nu**7)*(61+662*tan(lat)**2+1320*tan(lat)**4+720*tan(lat)**6)
        dE = self.easting - E0

        #These are on the wrong ellipsoid currently: Airy1830. (Denoted by _1)
        lat_1 = lat - VII*dE**2 + VIII*dE**4 - IX*dE**6
        lon_1 = lon0 + X*dE - XI*dE**3 + XII*dE**5 - XIIA*dE**7

        #Want to convert to the GRS80 ellipsoid.
        #First convert to cartesian from spherical polar coordinates
        H = 0 #Third spherical coord.
        x_1 = (nu/F0 + H)*cos(lat_1)*cos(lon_1)
        y_1 = (nu/F0+ H)*cos(lat_1)*sin(lon_1)
        z_1 = ((1-e2)*nu/F0 +H)*sin(lat_1)

        #Perform Helmut transform (to go between Airy 1830 (_1) and GRS80 (_2))
        s = -20.4894*10**-6 #The scale factor -1
        tx, ty, tz = 446.448, -125.157, + 542.060 #The translations along x,y,z axes respectively
        rxs,rys,rzs = 0.1502,  0.2470,  0.8421  #The rotations along x,y,z respectively, in seconds
        rx, ry, rz = rxs*pi/(180*3600.), rys*pi/(180*3600.), rzs*pi/(180*3600.) #In radians
        x_2 = tx + (1+s)*x_1 + (-rz)*y_1 + (ry)*z_1
        y_2 = ty + (rz)*x_1  + (1+s)*y_1 + (-rx)*z_1
        z_2 = tz + (-ry)*x_1 + (rx)*y_1 +  (1+s)*z_1

        #Back to spherical polar coordinates from cartesian
        #Need some of the characteristics of the new ellipsoid
        a_2, b_2 =6378137.000, 6356752.3141 #The GSR80 semi-major and semi-minor axes used for WGS84(m)
        e2_2 = 1- (b_2*b_2)/(a_2*a_2)   #The eccentricity of the GRS80 ellipsoid
        p = sqrt(x_2**2 + y_2**2)

        #Lat is obtained by an iterative proceedure:
        lat = arctan2(z_2,(p*(1-e2_2))) #Initial value
        latold = 2 * pi
        while abs(lat - latold)>10**-16:
            lat, latold = latold, lat
            nu_2 = a_2/sqrt(1-e2_2*sin(latold)**2)
            lat = arctan2(z_2+e2_2*nu_2*sin(latold), p)

        #Lon and height are then pretty easy
        lon = arctan2(y_2,x_2)
        H = p/cos(lat) - nu_2

        #Convert to degrees
        self.lat = lat*180/pi
        self.lon = lon*180/pi

        return True

    def _WGS84toOSGB36(self):
        """Perform conversion from WGS84 to OSGB36. If the OSGB36 co-ords are available,
        just return those.
        """
        if self.lat is None or self.lon is None:
            return False

        #First convert to radians
        #These are on the wrong ellipsoid currently: GRS80. (Denoted by _1)
        lat_1 = self.lat * pi / 180
        lon_1 = self.lon * pi / 180

        #Want to convert to the Airy 1830 ellipsoid, which has the following:
        a_1, b_1 =6378137.000, 6356752.3141    #The GSR80 semi-major and semi-minor axes used for WGS84(m)
        e2_1 = 1 - (b_1*b_1) / (a_1 * a_1)     #The eccentricity of the GRS80 ellipsoid
        nu_1 = a_1/sqrt(1-e2_1*sin(lat_1)**2)

        #First convert to cartesian from spherical polar coordinates
        H = 0 #Third spherical coord.
        x_1 = (nu_1 + H)*cos(lat_1)*cos(lon_1)
        y_1 = (nu_1 + H)*cos(lat_1)*sin(lon_1)
        z_1 = ((1-e2_1)*nu_1 + H)*sin(lat_1)

        #Perform Helmut transform (to go between GRS80 (_1) and Airy 1830 (_2))
        s = 20.4894*10**-6 #The scale factor -1
        tx, ty, tz = -446.448, 125.157, -542.060 #The translations along x,y,z axes respectively
        rxs, rys, rzs = -0.1502, -0.2470, -0.8421#The rotations along x,y,z respectively, in seconds
        rx, ry, rz = rxs*pi/(180*3600.), rys*pi/(180*3600.), rzs*pi/(180*3600.) #In radians
        x_2 = tx + (1+s)*x_1 + (-rz)*y_1 + ry * z_1
        y_2 = ty + rz * x_1 + (1+s)*y_1 + (-rx)*z_1
        z_2 = tz + (-ry) * x_1 + rx * y_1 +(1+s)*z_1

        #Back to spherical polar coordinates from cartesian
        #Need some of the characteristics of the new ellipsoid
        a, b = 6377563.396, 6356256.909 #The GSR80 semi-major and semi-minor axes used for WGS84(m)
        e2 = 1 - (b*b)/(a*a) #The eccentricity of the Airy 1830 ellipsoid
        p = sqrt(x_2**2 + y_2**2)

        #Lat is obtained by an iterative proceedure:
        lat = arctan2(z_2,(p*(1-e2))) #Initial value
        latold = 2*pi
        while abs(lat - latold)>10**-16:
            lat, latold = latold, lat
            nu = a/sqrt(1 - e2 * sin(latold) ** 2)
            lat = arctan2(z_2 + e2 * nu * sin(latold), p)

        #Lon and height are then pretty easy
        lon = arctan2(y_2,x_2)
        H = p/cos(lat) - nu

        #E, N are the British national grid coordinates - eastings and northings
        F0 = 0.9996012717 #scale factor on the central meridian
        lat0 = 49*pi/180#Latitude of true origin (radians)
        lon0 = -2*pi/180#Longtitude of true origin and central meridian (radians)
        N0, E0 = -100000, 400000#Northing & easting of true origin (m)
        n = (a-b)/(a+b)

        #meridional radius of curvature
        rho = a*F0*(1-e2)*(1-e2*sin(lat)**2)**(-1.5)
        eta2 = nu*F0/rho-1

        M1 = (1 + n + (5/4)*n**2 + (5/4)*n**3) * (lat-lat0)
        M2 = (3*n + 3*n**2 + (21/8)*n**3) * sin(lat-lat0) * cos(lat+lat0)
        M3 = ((15/8)*n**2 + (15/8)*n**3) * sin(2*(lat-lat0)) * cos(2*(lat+lat0))
        M4 = (35/24)*n**3 * sin(3*(lat-lat0)) * cos(3*(lat+lat0))

        #meridional arc
        M = b * F0 * (M1 - M2 + M3 - M4)

        I = M + N0
        II = nu*F0*sin(lat)*cos(lat)/2
        III = nu*F0*sin(lat)*cos(lat)**3*(5- tan(lat)**2 + 9*eta2)/24
        IIIA = nu*F0*sin(lat)*cos(lat)**5*(61- 58*tan(lat)**2 + tan(lat)**4)/720
        IV = nu*F0*cos(lat)
        V = nu*F0*cos(lat)**3*(nu/rho - tan(lat)**2)/6
        VI = nu*F0*cos(lat)**5*(5 - 18* tan(lat)**2 + tan(lat)**4 + 14*eta2 - 58*eta2*tan(lat)**2)/120

        N = I + II*(lon-lon0)**2 + III*(lon- lon0)**4 + IIIA*(lon-lon0)**6
        E = E0 + IV*(lon-lon0) + V*(lon- lon0)**3 + VI*(lon- lon0)**5

        self.easting = E
        self.northing = N

        return True
