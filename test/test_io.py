import pytest
import os
import numpy as np
from shapely.geometry import Point,LineString,Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection

import mshapely
from mshapely.io import readGeometry,writeGeometry
from mshapely.io import point2numpy,linestring2numpy,polygon2numpy,multipoint2numpy,multilinestring2numpy,multipolygon2numpy
from mshapely.io import createGEO,createMSH

def test_tofile():
  path_p_geo="../data/test_io.point.geojson"
  path_p_shp="../data/test_io.point.shp"
  path_pol_geo="../data/test_io.polygon.geojson"
  path_pol_shp="../data/test_io.polygon.shp"
  
  point = Point((0,0))
  
  point.write(path_p_geo,type="geojson").write(path_p_shp,type="shp")
  polygon=point.buffer(100,4).write(path_pol_geo,type="geojson").write(path_pol_shp,type="shp")
  
  np.testing.assert_almost_equal(readGeometry(path_p_geo)['geometry'].xy.astype(np.float32),point.xy.astype(np.float32))
  np.testing.assert_almost_equal(readGeometry(path_p_shp)['geometry'].xy.astype(np.float32),point.xy.astype(np.float32))
  np.testing.assert_almost_equal(readGeometry(path_pol_geo)['geometry'].xy.astype(np.float32),polygon.xy.astype(np.float32))
  np.testing.assert_almost_equal(readGeometry(path_pol_shp)['geometry'].xy.astype(np.float32),polygon.xy.astype(np.float32))
  
  point.delete(path_p_geo)
  polygon.delete(path_pol_geo)
  point.delete(path_p_shp)
  polygon.delete(path_pol_shp)
  
def test_tonumpy():
  point = Point(10,10)
  line = LineString([(0, 0), (0, 1),(1,1),(1,0),(0,0)])
  polygon = Polygon([(0, 0), (0, 1),(1,1),(1,0),(0,0)])
  mp = MultiPoint([(0, 0), (1, 1), (1,2), (2,2)])
  ml = MultiLineString([[(0, 0), (1, 1)],[(1,2), (2,2)]])
  polygon2 = Polygon([(0, 0), (0, 1),(1,1),(1,0),(0,0)],[LineString([(0.25, 0.25), (0.25, 0.75),(0.75,0.75),(0.75,0.25),(0.25,0.25)])])
  mpol = MultiPolygon([polygon, polygon2])
  
  np.testing.assert_array_equal(point.np, np.array([[10,10]]))
  np.testing.assert_array_equal(line.np, np.array([[0,0,0],[1,0,1],[2,1,1],[3,1,0],[0,0,0]]))
  np.testing.assert_almost_equal(line._np(isNorm=True), np.array([
    [0, 0.,0.0,0.70710678,0.70710678,0.,0.],
    [1, 0,1.,0.70710678,-0.70710678,0.,1.],
    [2, 1.,1.,-0.70710678,-0.70710678,1.,1.],
    [3, 1.,0.,-0.70710678,0.70710678,1.,0. ],
    [0, 0,0,0.70710678,0.70710678,0.,0. ]
    ]))
  np.testing.assert_almost_equal(line._np(isNorm=True,onPoint=False), np.array([
    [ 0.,   0.,   0.5,  1.,  -0.,   0.  , 0. ],
    [ 1. ,  0.5 , 1. ,  0.,  -1. ,  0.  , 1. ],
    [ 2.  , 1. ,  0.5 ,-1.  ,-0.,   1.  , 1. ],
    [ 3. ,  0.5 , 0. ,  0. ,  1. ,  1. ,  0. ],
    [ 0.  , 0. ,  0.5  ,1.,  -0.  , 0.,   0. ]
    ]))
  
  np.testing.assert_array_equal(polygon.np, np.array([[0,0,0,0],[0,1,0,1],[0,2,1,1],[0,3,1,0],[0,0,0,0]]))
  np.testing.assert_array_equal(mp.np, np.array([[0,0,0],[1,1,1],[2,1,2],[3,2,2]]))
  
  np.testing.assert_array_equal(ml.np, np.array([
    [0,0,0,0],
    [0,1,1,1],
    [1,0,1,2],
    [1,1,2,2],
    ])  )
  
  np.testing.assert_array_equal(mpol.np, np.array([
     [0.,0.,0.,0.,0.  ],
     [0.,0.,1.,0.,1.  ],
     [0.,0.,2.,1.,1.  ],
     [0.,0.,3.,1.,0.  ],
     [0.,0.,0.,0.,0.  ],
     [1.,0.,0.,0.,0.  ],
     [1.,0.,1.,0.,1.  ],
     [1.,0.,2.,1.,1.  ],
     [1.,0.,3.,1.,0.  ],
     [1.,0.,0.,0.,0.  ],
     [1.,1.,0.,0.25,0.25],
     [1.,1.,1.,0.25,0.75],
     [1.,1.,2.,0.75,0.75],
     [1.,1.,3.,0.75,0.25],
     [1.,1.,0,0.25,0.25],
  ]))
  
  
def test_togmsh():
  polygon = Point((0,0)).buffer(100)
  hole1 = Point((-50,0)).buffer(20)
  hole2 = Point((50,0)).buffer(20)
  polygon = Polygon(polygon.exterior,[hole1.exterior.coords[::-1],hole2.exterior.coords[::-1]])
  density=polygon.inearest(maxDistance=100,angle=90)
  density[:,2]=density[:,2]*0.1
  density=np.column_stack((density,np.ones(len(density))*1.2))
  
  polygon=polygon.dresample(density,minDensity=1,maxDensity=100)
  density=polygon.inearest(maxDistance=100,angle=90)
  density[:,2]=density[:,2]*0.1
  density=np.column_stack((density,np.ones(len(density))*1.2))
  polygon.msh("test/data/test.msh",density,minDensity=1,maxDensity=100).plot("test/data/test.png")
  
  
  
  # polygon = Polygon([(0, 0), (0, 1),(1,1),(1,0),(0,0)],[LineString([(0.25, 0.25), (0.25, 0.75),(0.75,0.75),(0.75,0.25),(0.25,0.25)])])
  # getGeo(polygon)
  
  # array=np.array([[0,0,11,1.2],[0,0,233,1.2],[0,0,107,1.2],[0,0,1007,1.2],[0,0,12,1.2],[0,0,950,1.2]])
  # getAttractors(array)



if __name__ == "__main__":
  
  # test_tofile()
  # test_tonumpy()
  test_togmsh()
  