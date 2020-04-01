import os
import pytest
import numpy as np
from numpy.testing import assert_array_equal
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection
import time

import mshapely
from mshapely.io import readGeometry
from mshapely.spatial import DF

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
    [0,0,1,1.2],
    [10,0,5,1.2],
    [20,0,2,1.2],
    [30,0,1,1.2],
    [40,0,3,1.2],
    ])
  df=DF(density,minDensity=1,maxDensity=10,minGrowth=1.2)
  np.testing.assert_array_equal(df.dp,np.array([[0,0,1,1.2,0,0],[20,0,2,1.2,0,2],[30,0,1,1.2,0,3]]))
  
  value=20000
  example=np.zeros((value,4))
  example[:,0]=np.arange(value)
  example[:,2] = np.tile(np.arange(1,101),int(value*0.01))
  example[:,3]=1.2
  a=DF(example,minDensity=1.0,maxDensity=101.0,balanced_tree=False)
  a=a.dp[:,:4]
  np.testing.assert_array_equal(a,np.column_stack((np.arange(0,value,100),np.zeros(int(value*0.01)),np.zeros(int(value*0.01))+1.0,np.zeros(int(value*0.01))+1.2)))

def test_inearest_dresample():
  import matplotlib.pyplot as plt
  polygon = Point((0,0)).buffer(100)#.simplify(0.1)
  
  hole1 = Point((-50,0)).buffer(20)
  hole2 = Point((50,0)).buffer(20)
  polygon = Polygon(polygon.exterior,[hole1.exterior.coords[::-1],hole2.exterior.coords[::-1]])
  density=polygon.inearest(maxDistance=100,angle=90)
  
  
  density[:,2]=density[:,2]*0.1
  density=np.column_stack((density,np.ones(len(density))*1.2))
  
  df = DF(density,minDensity=1,maxDensity=10)
  
  # df.write("test/data/test_inearest.geojson")
  df1=DF.read("test/data/test_inearest.geojson")
  
  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
  fig.tight_layout()
  
  df.plot(axe=axes[0],fig=fig,showDP=True)
  df1.plot(axe=axes[1],fig=fig,showDP=True)
  
  
  df.plotSave("test/data/density.1.png")
  
  np.testing.assert_almost_equal(df.dp[:,:2],df1.dp[:,:2],decimal=6)
  
  
  
def test_dresample():
  
  density = np.array([[0,0,1,1.2]])
  df = DF(density,minDensity=1.0,maxDensity=5.0)
  r=LineString([(0,0),(30,0)]).dresample(df)
  
  results = np.array(
    [ 0.        ,  1.    ,      2.2     ,    3.64  ,      5.368 ,      7.4416,
  9.92992   , 12.915904,   16.4990848  ,20.56560333 ,25.28280166 ,30.        ]
    )
  # np.testing.assert_almost_equal(r.xy[:,0], results)
  
  
  line = LineString([(0,0),(200,0)])
  mp = MultiPoint([(100,0)])
  density = np.array([[0,0,100,1.2],[100,0,1,1.2],[200,0,100,1.2]])
  df = DF(density,minDensity=2.0,maxDensity=100.0)
  r = line.dresample(df,mp=mp)
  


if __name__ == "__main__":
  # test_resample()
  # test_removeHoles()
  # test_dsimplify()
  # test_inearest_dresample()
  # test_dresample()
  
  