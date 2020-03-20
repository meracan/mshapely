import os
import sys
import time
import fiona
import numpy

from shapely import affinity
from shapely.geometry import Point, LineString, Polygon, \
  MultiPoint, MultiLineString, MultiPolygon,GeometryCollection

from shapely.ops import cascaded_union
from shapely import speedups

from .mist import add_attribute,add_method

from .io import writeGeometry,readGeometry,deleteGeometry,point2numpy,linestring2numpy,polygon2numpy,multipoint2numpy,\
  multilinestring2numpy,multipolygon2numpy

from .transformation import pieSectors

from .spatial import removeHolesPolygon,simplifyDensityPoint,simplifyDensityPolygon,fetchPolygon

from .resample import resampleLine,resamplePolygon,resampleDensity,resampleDensityPolygon

from .plot import plotPolygon,plotPolygons,plotSave

speedups.enable()


@add_method([GeometryCollection,Polygon,MultiPolygon])
def toShape(self):
  if isinstance(self[0],Point):
    return MultiPoint(self)
  elif isinstance(self[0],LineString):
    return MultiLineString(self)
  elif isinstance(self[0],Polygon):
    return MultiPolygon(self)
  elif isinstance(self[0],MultiPoint):
    l=[]
    for f in self:
      for geo in list(f):l.append(geo)
    return MultiPoint(l)
  elif isinstance(self[0],MultiLineString):
    l=[]
    for f in self:
      for geo in list(f):l.append(geo)
    return MultiLineString(l)
  elif isinstance(self[0],MultiPolygon):
    l=[]
    for f in self:
      for geo in list(f):l.append(geo)
    return MultiPolygon(l)
  return self
#
# Convert Shapely to numpy array
#
@add_attribute(GeometryCollection)
def np(self):
  return self.toShape().np
  
@add_attribute([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def np(self):
  return self._np()
#
# Get NP with function
#
@add_method(Point)
def _np(self,*args,**kwargs):
  return point2numpy(self,*args,**kwargs)

@add_method(MultiPoint)
def _np(self,*args,**kwargs):
  return multipoint2numpy(self,*args,**kwargs)
  
@add_method(LineString)
def _np(self,*args,**kwargs):
  return linestring2numpy(self,*args,**kwargs)

@add_method(MultiLineString)
def _np(self,*args,**kwargs):
  return multilinestring2numpy(self,*args,**kwargs)

@add_method(Polygon)
def _np(self,*args,**kwargs):
  return polygon2numpy(self,*args,**kwargs)

@add_method(MultiPolygon)
def _np(self,*args,**kwargs):
  return multipolygon2numpy(self,*args,**kwargs)


#
# Get xy coordinates
#
def xy_(feature):
  array=feature.np
  n=array.shape[1]
  return array[:,[n-2,n-1]]

@add_attribute([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def xy(self):
  return xy_(self)



#
# Write to files
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def write(self, *args, **kwargs):
  writeGeometry(self, *args, **kwargs)
  return self

#
# Write to files
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def delete(self, *args, **kwargs):
  deleteGeometry(*args, **kwargs)
  return self


#
# Resample
#
@add_method(GeometryCollection)
def resample(self, *args, **kwargs):
  return self.toShape().resample()

@add_method([Point,MultiPoint])
def resample(self, *args, **kwargs):
  return self

@add_method(LineString)
def resample(self, *args, **kwargs):
  return resampleLine(self, *args, **kwargs)

@add_method(MultiLineString)
def resample(self, *args, **kwargs):
  multi = [linestring.resample(*args, **kwargs) for linestring in self]
  return MultiLineString(multi)

@add_method(Polygon)
def resample(self, *args, **kwargs):
  return resamplePolygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def resample(self, *args, **kwargs):
  return MultiPolygon([polygon.resample(*args, **kwargs) for polygon in self])

#
# Resample Density
#
@add_method(GeometryCollection)
def resampleDensity(self):
  return self.toShape().resampleDensity()

@add_method([Point,MultiPoint])
def resampleDensity(self):
  return self
  
@add_method(LineString)
def resampleDensity(self, *args, **kwargs):
  return resampleDensity(self, *args, **kwargs)

@add_method(MultiLineString)
def resampleDensity(self, *args, **kwargs):
  multi = [linestring.resampleDensity(*args, **kwargs) for linestring in self]
  return MultiLineString(multi)

@add_method(Polygon)
def resampleDensity(self, *args, **kwargs):
  return resampleDensityPolygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def resampleDensity(self, *args, **kwargs):
  return MultiPolygon([polygon.resampleDensity(*args, **kwargs) for polygon in self])


# 
# Sectors
# 
@add_method(GeometryCollection)
def sectors(self):
  return self.toShape().sectors()
  
@add_method([Point,MultiPoint])
def sectors(self, *args, **kwargs):
  return self
  
@add_method([LineString,Polygon])
def sectors(self, *args, **kwargs):
  onPoint=kwargs.get('onPoint',False)
  pts=self._np(isNorm=True, onPoint=onPoint)
  return pts,pieSectors(pts, *args, **kwargs)

@add_method([MultiLineString,MultiPolygon])
def sectors(self, *args, **kwargs):
  multi = [item.sectors(*args, **kwargs) for item in self]
  return multi


# 
# Remove Holes
# 
@add_method(GeometryCollection)
def removeHoles(self, *args, **kwargs):
  return self.toShape().removeHoles(*args, **kwargs)
  
@add_method([Point,MultiPoint,LineString,MultiLineString])
def removeHoles(self, *args, **kwargs):
  return self

@add_method(Polygon)
def removeHoles(self, *args, **kwargs):
  return removeHolesPolygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def removeHoles(self, *args, **kwargs):
  return MultiPolygon([polygon.removeHoles(*args, **kwargs) for polygon in self])

# 
# Get largest
# 
@add_method(GeometryCollection)
def getLargest(self):
  return self.toShape().getLargest()
  
@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon])
def getLargest(self):
  return self

@add_method(MultiPolygon)
def getLargest(self):
  # TODO: Might need to fill holes
  areas = numpy.array([polygon.area for polygon in self])
  return self[numpy.argmax(areas)]
  
#
# Correct polygons and multipolygons
#
@add_method(GeometryCollection)
def correct(self,value):
  return self.toShape().correct(value)

@add_method([Point,MultiPoint,LineString,MultiLineString])
def correct(self):
  return self
  
@add_method([Polygon,MultiPolygon])
def correct(self,value):
  return self.buffer(value)

#
# Simplify Density
#
@add_method(GeometryCollection)
def simplifyDensity(self,*args,**kwargs):
  return self.toShape().simplifyDensity(*args,**kwargs)

@add_method([Point,MultiPoint,LineString,MultiLineString])
def simplifyDensity(self):
  return simplifyDensityPoint(self,*args,**kwargs)
  
@add_method(Polygon)
def simplifyDensity(self,*args,**kwargs):
  return simplifyDensityPolygon(self,*args,**kwargs)

@add_method(MultiPolygon)
def simplifyDensity(self,*args,**kwargs):
  return cascaded_union([polygon.simplifyDensity(*args, **kwargs) for polygon in self])

#
# Compute Fetch
#
@add_method(GeometryCollection)
def fetch(self,*args,**kwargs):
  return self.toShape().fetch(*args,**kwargs)

@add_method([Point,MultiPoint,LineString,MultiLineString])
def fetch(self):
  return self
  
@add_method(Polygon)
def fetch(self,*args,**kwargs):
  return fetchPolygon(self,*args,**kwargs)

@add_method(MultiPolygon)
def fetch(self,*args,**kwargs):
  a=numpy.array([polygon.fetch(*args, **kwargs) for polygon in self])
  l,m,n=a.shape
  return numpy.reshape(a, (l*m, n)) 


#
# Plot
#
@add_method(GeometryCollection)
def plot(self,*args,**kwargs):
  return self.toShape().plot(*args,**kwargs)
  
@add_method(Polygon)
def plot(self,*args,**kwargs):
  plotPolygon(self,*args,**kwargs)
  return self

@add_method(MultiPolygon)
def plot(self,*args,**kwargs):
  plotPolygons(self,*args,**kwargs)
  return self

@add_method([GeometryCollection,Polygon,MultiPolygon])
def savePlot(self,*args,**kwargs):
  plotSave(*args,**kwargs)
  return self
 