import os
import pytest
import numpy as np
from numpy.testing import assert_array_equal
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection
import time

import mshapely
from mshapely.spatial import dsimplifyDensityPoint
from mshapely.io import readGeometry

def test_resample():
  point = Point((0,0)).resample()
  assert_array_equal(point.np,[[0,0]])
  assert_array_equal(LineString([(0,0),(10,0)]).resample(), np.column_stack((np.arange(11),np.zeros(11))))
  assert_array_equal(LineString([(0,0),(10,0)]).resample(2), np.column_stack((np.arange(0,11,2),np.zeros(6))))

  assert_array_equal(MultiLineString([[(0,0),(10,0)]]).resample().xy, np.column_stack((np.arange(11),np.zeros(11))))
  
  assert_array_equal(Polygon([(0, 0), (0, 2),(2,2),(2,0),(0,0)]).resample().xy,np.array([
    [0., 0.],
    [0., 1.],
    [0., 2.],
    [1., 2.],
    [2., 2.],
    [2., 1.],
    [2., 0.],
    [1., 0.],
    [0., 0.]
   ]))


def test_removeHoles():
  polygon = Polygon([(0, 0), (0, 1),(1,1),(1,0),(0,0)])
  polygon2 = Polygon([(0, 0), (0, 1),(1,1),(1,0),(0,0)],[LineString([(0.25, 0.25),(0.75,0.25) ,(0.75,0.75),(0.25, 0.75),(0.25,0.25)])])
  assert_array_equal(polygon2.removeHoles().np,polygon.np)
  assert_array_equal(polygon2.removeHoles(0.1).np,polygon2.np)

  assert_array_equal(Point(0,0).removeHoles().np,Point(0,0).np)
  assert_array_equal(LineString([(0,0),(10,0)]).removeHoles().np,LineString([(0,0),(10,0)]).np)

def test_dsimplify():
  density=np.array([
    [0,0,1],
    [10,0,5],
    [20,0,2],
    [30,0,1],
    [40,0,3],
    ])
  d=simplifyDensityPoint(density)
  np.testing.assert_array_equal(d,np.array([[0,0,1],[20,0,2],[30,0,1]]))
  
  value=20000
  example=np.zeros((value,3))
  example[:,0]=np.arange(value)
  example[:,2] = np.tile(np.arange(1,101),int(value*0.01))
  a=simplifyDensityPoint(example,minDensity=1.0,maxDensity=101.0,balanced_tree=False)
  np.testing.assert_array_equal(a,np.column_stack((np.arange(0,value,100),np.zeros(int(value*0.01)),np.zeros(int(value*0.01))+1.0)))

def test_inearest_dresample():
  polygon = Point((0,0)).buffer(100)
  
  hole1 = Point((-50,0)).buffer(20)
  hole2 = Point((50,0)).buffer(20)
  polygon = Polygon(polygon.exterior,[hole1.exterior.coords[::-1],hole2.exterior.coords[::-1]])
  density=polygon.fetch(maxDistance=100,angle=90)
  density[:,2]=density[:,2]*0.1
  mp=GeometryCollection(list(map(Point,density[:,:2])))
  # mp.write("test/data/test_fetch.geojson",properties=map(lambda x:{"density":x},density[:,2]))
  np.testing.assert_almost_equal(density[:,2],list(map(lambda x:x['density'],readGeometry("test/data/test_fetch.geojson")['properties'])),decimal=6)
  
  
  
  polygon=polygon.resampleDensity(density,minDensity=1,maxDensity=100,growth=1.2)
  # polygon.write("test/data/test_inearest.geojson")
  np.testing.assert_almost_equal(polygon.xy,readGeometry("test/data/test_inearest.geojson")['geometry'].xy,decimal=6)
  

if __name__ == "__main__":
  test_resample()
  test_removeHoles()
  test_dsimplify()
  test_inearest_dresample()
  
  