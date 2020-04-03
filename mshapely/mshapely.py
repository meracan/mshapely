import os
import sys
import time
import fiona
import numpy

from shapely import affinity
from shapely.geometry import Point, LineString, Polygon, \
  MultiPoint, MultiLineString, MultiPolygon,GeometryCollection

from shapely.ops import cascaded_union,transform
from shapely import speedups

from .misc import add_attribute,add_method
from .io import GIS
from .io import point2numpy,linestring2numpy,polygon2numpy,multipoint2numpy,\
  multilinestring2numpy,multipolygon2numpy


from .spatial import DF
from .spatial import removeHoles_Polygon,remove_Polygons,dsimplify_Polygon,\
inearest_Polygon,resample_LineString,resample_Polygon,dresample_LineString,dresample_Polygon

from .plot import plotPoints,plotLineString,plotLineStrings,plotPolygon,plotPolygons,plotSave

speedups.enable()



import warnings



@add_method([GeometryCollection,Polygon,MultiPolygon])
def toShape(self):
  if isinstance(self[0],Point):
    if len(self)==1:return Point(self[0])
    return MultiPoint(self)
  elif isinstance(self[0],LineString):
    if len(self)==1:return LineString(self[0])
    return MultiLineString(self)
  elif isinstance(self[0],Polygon):
    
    # warnings.warn("Commented below for gmsh")
    if len(self)==1:return Polygon(self[0])
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

@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
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
  
@add_attribute([Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def np(self):
  return self._np()
#
# Get NP with function
#
@add_method(Point)
def _np(self,*args,**kwargs):
  return point2numpy(self,*args,**kwargs)

@add_method([MultiPoint])
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
def write(self,path,*args, **kwargs):
  GIS(self,*args, **kwargs).write(path)
  return self


#
# Delete geometry based on filepath
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def delete(self, *args, **kwargs):
  GIS.delete(*args, **kwargs)
  return self

#
# Project
#
@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def proj(self, project):
  return transform(project,self)

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
def dresample(self, *args, **kwargs):
  return self.toShape().dresample(*args, **kwargs)

@add_method([Point,MultiPoint])
def dresample(self, *args, **kwargs):
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
  
@add_method([Point,MultiPoint,LineString,MultiLineString])
def removeHoles(self, *args, **kwargs):
  return self

@add_method(Polygon)
def removeHoles(self, *args, **kwargs):
  return removeHoles_Polygon(self, *args, **kwargs)

@add_method(MultiPolygon)
def removeHoles(self, *args, **kwargs):
  return MultiPolygon([polygon.removeHoles(*args, **kwargs) for polygon in self])
# 
# Remove Polygons
# 
@add_method(GeometryCollection)
def removePolygons(self, *args, **kwargs):
  return self.toShape().removePolygons(*args, **kwargs)
  
@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon])
def removePolygons(self, *args, **kwargs):
  return self

@add_method(MultiPolygon)
def removePolygons(self, *args, **kwargs):
  return remove_Polygons(self, *args, **kwargs)



# 
# Get largest
# 
@add_method(GeometryCollection)
def largest(self):
  return self.toShape().largest()
  
@add_method([Point,MultiPoint,LineString,MultiLineString,Polygon])
def largest(self):
  return self

@add_method(MultiPolygon)
def largest(self,return_other=False):
  # TODO: Might need to fill holes
  areas = numpy.array([polygon.area for polygon in self])
  
  index=numpy.argmax(areas)
  if return_other:
    array=[polygon for i,polygon in enumerate(self) if i!=index]
    return self[index],array
  return self[index]
  
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
# Get exterior shape
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
# Modify intersection function
#
_intersection = Polygon.intersection
@add_method(Polygon)
def intersection(self,*args,**kwargs):
  return _intersection(self,*args,**kwargs)#.removeHoles(1).removePolygons(10).simplify(0)

#
# Modify union function
#
_union = Polygon.union
@add_method(Polygon)
def union(self,*args,**kwargs):
  return _union(self,*args,**kwargs)#.removeHoles(1).removePolygons(10).simplify(0)



#
# Simplify Density
#
@add_method(GeometryCollection)
def dsimplify(self,*args,**kwargs):
  return self.toShape().dsimplify(*args,**kwargs)


@add_method([Point,MultiPoint,LineString,MultiLineString])
def dsimplify(self,*args,**kwargs):
  return self


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

@add_method([Point,MultiPoint,LineString,MultiLineString])
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

@add_method([MultiPoint])
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
  plotLineStrings(self,*args,**kwargs)
  return self

@add_method(MultiPolygon)
def plot(self,*args,**kwargs):
  plotPolygons(self,*args,**kwargs)
  return self

@add_method([GeometryCollection,Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon])
def savePlot(self,*args,**kwargs):
  plotSave(*args,**kwargs)
  return self
 