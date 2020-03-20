import pytest
import os
import numpy as np
from shapely.geometry import Point,LineString,Polygon,MultiPoint,MultiLineString,MultiPolygon
import matplotlib.pyplot as plt
import mshapely

def test_general():
  # print(Point(0,0).np)
  # print(LineString([[0,0],[1,0],[2,0]]).np)  
  # print(Polygon([[0,0],[1,0],[2,0],[0,0]]).np)
  # print(MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).np)
  # print(MultiPoint([[0,0],[1,0],[2,0],[0,0]]).np)
  # print(MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).np)
  # print(MultiPolygon([Polygon([[0,0],[1,0],[2,0],[0,0]])]).np)
  
  # print(Point(0,0).xy)
  # print(LineString([[0,0],[1,0],[2,0]]).xy)  
  # print(Polygon([[0,0],[1,0],[2,0],[0,0]]).xy)
  # print(MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).xy)
  # print(MultiPoint([[0,0],[1,0],[2,0],[0,0]]).xy)
  # print(MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).xy)
  # print(MultiPolygon([Polygon([[0,0],[1,0],[2,0],[0,0]])]).xy)
  
  # print(LineString([[0,0],[1,0],[2,0]])._np())  
  # print(LineString([[0,0],[1,0],[2,0]])._np(isNorm=True))
  # print(LineString([[0,0],[1,0],[2,0]])._np(isNorm=True,onPoint=False))
  
  
  
  
  # print(LineString([(0,0),(30,0)]).dresample(np.array([[0,0,1]]), minDensity=1.0, maxDensity=5.0, growth=1.2))
  
  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 3))
  fig.tight_layout()
  LineString([(0,0),(30,0)]).plot("o-",axes[0]).dresample(np.array([[0,0,1]]), minDensity=1.0, maxDensity=5.0, growth=1.2).plot("o-",axes[1]).savePlot("doc/img/dresample.1.png")
  
  fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 3))
  fig.tight_layout()
  mp = MultiPoint([(100,0)])
  density = np.array([[0,0,100],[100,0,1],[200,0,100]])
  LineString([(0,0),(200,0)]).plot("o-",axes[0]).dresample(density=density,mp=mp,minDensity=2.0, maxDensity=100.0, growth=1.2).plot("o-",axes[1]).savePlot("doc/img/dresample.2.png")
  
  fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 5))
  fig.tight_layout()
  mp = MultiPoint([(0, 0), (0, 100),(100,100),(100,0)])
  density = np.array([[0,0,1],[100,100,1]])
  polygon=Polygon([(0, 0), (0, 100),(100,100),(100,0),(0,0)]).plot("o-",axes[0][0])
  polygon.dresample(density,minDensity=2.0, maxDensity=20.0, growth=1.2).plot("o-",axes[0][1])
  polygon.dresample(density,mp,minDensity=2.0, maxDensity=20.0, growth=1.2).plot("o-",axes[1][0])
  polygon.savePlot("doc/img/dresample.3.png")
  
  
  
  
  
  None
  
if __name__ == "__main__":
  test_general()
  
  