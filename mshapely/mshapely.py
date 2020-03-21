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

from .misc import add_attribute,add_method

from .io import writeGeometry,readGeometry,deleteGeometry,point2numpy,linestring2numpy,polygon2numpy,multipoint2numpy,\
  multilinestring2numpy,multipolygon2numpy

# from .transformation import pieSectors

from .spatial import removeHoles_Polygon,dsimplify_Point,dsimplify_Polygon,\
inearest_Polygon,resample_LineString,resample_Polygon,dresample_LineString,dresample_Polygon


from .plot import plotPoints,plotLineString,plotPolygon,plotSave

speedups.enable()

class MultiDensity(MultiPoint):
  def __init__(self, value):
    value=numpy.array(value)
    xy=value[:,:2]
    self.att = value[:,2:]
    super().__init__(xy)
  @property
  def xya(self):
    return numpy.column_stack((xy_(self),self.att))  



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

@add_method(GeometryCollection)
def to(self,*args,**kwargs):
  
  return self.toShape().to(*args,**kwargs)

@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon,MultiDensity])
def to(self,instance):
  if isinstance(self,Polygon):
    if instance==Point:return GeometryCollection(list(map(Point,self.xy)))
    elif instance==MultiPoint:return MultiPoint(self.xy)
    else:raise Exception("TODO")
  raise Exception("TODO")
  

#
# Convert Shapely to numpy array
#
@add_attribute(GeometryCollection)
def np(self):
  return self.toShape().np
  
@add_attribute([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon,MultiDensity])
def np(self):
  return self._np()
#
# Get NP with function
#
@add_method(Point)
def _np(self,*args,**kwargs):
  return point2numpy(self,*args,**kwargs)

@add_method([MultiPoint,MultiDensity])
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

@add_attribute([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon,MultiDensity])
def xy(self):
  return xy_(self)

#
# Write to files
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def write(self, *args, **kwargs):
  writeGeometry(self, *args, **kwargs)
  return self

# TODO MultiDensity to Geometry

#
# Write to files
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon,MultiDensity])
def delete(self, *args, **kwargs):
  deleteGeometry(*args, **kwargs)
  return self


#
# Resample
#
@add_method(GeometryCollection)
def resample(self, *args, **kwargs):
  return self.toShape().resample()

@add_method([Point,MultiPoint,MultiDensity])
def resample(self, *args, **kwargs):
  return self

@add_method(LineString)
def resample(self, *args, **kwargs):
  return resample_LineString(self, *args, **kwargs)

@add_method(MultiLineString)
def resample(self, *args, **kwargs):
  multi = [linestring.resample(*args, **kwargs) for linestring in self]
  return MultiLineString(multi)

@add_method(Polygon)
def resample(self, *args, **kwargs):
  return resample_Polygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def resample(self, *args, **kwargs):
  return MultiPolygon([polygon.resample(*args, **kwargs) for polygon in self])

#
# Resample Density
#
@add_method(GeometryCollection)
def dresample(self):
  return self.toShape().dresample()

@add_method([Point,MultiPoint,MultiDensity])
def dresample(self):
  return self

@add_method(LineString)
def dresample(self, *args, **kwargs):
  return dresample_LineString(self, *args, **kwargs)

@add_method(MultiLineString)
def dresample(self, *args, **kwargs):
  multi = [linestring.dresample(*args, **kwargs) for linestring in self]
  return MultiLineString(multi)

@add_method(Polygon)
def dresample(self, *args, **kwargs):
  return dresample_Polygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def dresample(self, *args, **kwargs):
  return MultiPolygon([polygon.dresample(*args, **kwargs) for polygon in self])


# # 
# # Sectors
# # 
# @add_method(GeometryCollection)
# def sectors(self):
#   return self.toShape().sectors()
  
# @add_method([Point,MultiPoint])
# def sectors(self, *args, **kwargs):
#   return self
  
# @add_method([LineString,Polygon])
# def sectors(self, *args, **kwargs):
#   onPoint=kwargs.get('onPoint',False)
#   pts=self._np(isNorm=True, onPoint=onPoint)
#   return pts,pieSectors(pts, *args, **kwargs)

# @add_method([MultiLineString,MultiPolygon])
# def sectors(self, *args, **kwargs):
#   multi = [item.sectors(*args, **kwargs) for item in self]
#   return multi


# 
# Remove Holes
# 
@add_method(GeometryCollection)
def removeHoles(self, *args, **kwargs):
  return self.toShape().removeHoles(*args, **kwargs)
  
@add_method([Point,MultiPoint,LineString,MultiLineString,MultiDensity])
def removeHoles(self, *args, **kwargs):
  return self

@add_method(Polygon)
def removeHoles(self, *args, **kwargs):
  return removeHoles_Polygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def removeHoles(self, *args, **kwargs):
  return MultiPolygon([polygon.removeHoles(*args, **kwargs) for polygon in self])

# 
# Get largest
# 
@add_method(GeometryCollection)
def largest(self):
  return self.toShape().largest()
  
@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiDensity])
def largest(self):
  return self

@add_method(MultiPolygon)
def largest(self):
  # TODO: Might need to fill holes
  areas = numpy.array([polygon.area for polygon in self])
  return self[numpy.argmax(areas)]
  
#
# Correct polygons and multipolygons
#
@add_method(GeometryCollection)
def correct(self,value):
  return self.toShape().correct(value)

@add_method([Point,MultiPoint,LineString,MultiLineString,MultiDensity])
def correct(self):
  return self
  
@add_method([Polygon,MultiPolygon])
def correct(self,value):
  return self.buffer(value)

#
# Simplify Density
#
@add_method(GeometryCollection)
def getExterior(self,*args,**kwargs):
  return self.toShape().getExterior(*args,**kwargs)

@add_method([Point,MultiPoint,LineString,MultiLineString])
def getExterior(self,*args,**kwargs):
  return self

@add_method(Polygon)
def getExterior(self,*args,**kwargs):
  return Polygon(self.exterior)

@add_method(MultiPolygon)
def getExterior(self,*args,**kwargs):
  return MultiPolygon([Polygon(polygon.exterior) for polygon in self])




#
# Simplify Density
#
@add_method(GeometryCollection)
def dsimplify(self,*args,**kwargs):
  return self.toShape().dsimplify(*args,**kwargs)


@add_method([Point,MultiPoint,LineString,MultiLineString])
def dsimplify(self,*args,**kwargs):
  return self

@add_method([MultiDensity])
def dsimplify(self,*args,**kwargs):
  return dsimplify_Point(self.xya,*args,**kwargs)
  
@add_method(Polygon)
def dsimplify(self,*args,**kwargs):
  return dsimplify_Polygon(self,*args,**kwargs)

@add_method(MultiPolygon)
def dsimplify(self,*args,**kwargs):
  return cascaded_union([polygon.dsimplify(*args, **kwargs) for polygon in self])

#
# Compute nearest interior nodes
#
@add_method(GeometryCollection)
def inearest(self,*args,**kwargs):
  return self.toShape().inearest(*args,**kwargs)

@add_method([Point,MultiPoint,LineString,MultiLineString,MultiDensity])
def inearest(self):
  return self
  
@add_method(Polygon)
def inearest(self,*args,**kwargs):
  return inearest_Polygon(self,*args,**kwargs)

@add_method(MultiPolygon)
def inearest(self,*args,**kwargs):
  a=numpy.array([polygon.inearest(*args, **kwargs) for polygon in self])
  l,m,n=a.shape
  return numpy.reshape(a, (l*m, n)) 


#
# Plot
#
@add_method(GeometryCollection)
def plot(self,*args,**kwargs):
  return self.toShape().plot(*args,**kwargs)

@add_method(Point)
def plot(self,*args,**kwargs):
  plotPoints(MultiPoint(self),*args,**kwargs)
  return self

@add_method([MultiPoint,MultiDensity])
def plot(self,*args,**kwargs):
  plotPoints(self,*args,**kwargs)
  return self

@add_method(LineString)
def plot(self,*args,**kwargs):
  plotLineString(self,*args,**kwargs)
  return self

@add_method(Polygon)
def plot(self,*args,**kwargs):
  plotPolygon(self,*args,**kwargs)
  return self

@add_method(MultiLineString)
def plot(self,*args,**kwargs):
  for linestring in self:
    linestring.plot(*args,**kwargs)
  return self

@add_method(MultiPolygon)
def plot(self,*args,**kwargs):
  for polygon in self:
    polygon.plot(*args,**kwargs)
  return self

@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon,MultiDensity])
def savePlot(self,*args,**kwargs):
  plotSave(*args,**kwargs)
  return self
 