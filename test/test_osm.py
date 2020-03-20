import os
import pytest
import numpy as np
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon

from mshapely.osm import OSM


def test_downloadOSM():
  OSM.downloadOSM("../data")
  None

def test_extractOSM():
  OSM.extractOSM("../data/water-polygons-split-4326.zip","../data/osm.geojson",[-68,43,-62,47])
  None

def test_unionOSM():
  obj = {
    "minDensity":10,
    "maxDensity":10000,
    "growth":1.2,
    "path":{
      "osm":"../data/osm.geojson",
      "domain":"../data/domain.geojson",
      "density":"../data/density.geojson",
      "osmDomain":"../data/osmDomain.geojson",
      "osmSimplify":"../data/osmSimplify.geojson",
      "osmFetch":"../data/osmFetch.geojson",
      "osmResample":"../data/osmResample.geojson",
    }
  }
  
  
  
  # unionOSM(obj['osm'],obj['union'])
  if not os.path.exists(obj['path']['density']):
    density = np.array([
      # [-40,0,10],
      [-63.563342,44.634637,10],
      [-63.553987,44.627934,10],
      [-63.495436,44.606528,20],
      # [0,90,10],
      ])
    xy=density[:,[0,1]]
    properties = [{"density":x} for x in density[:,2]]
    OSM.write(list(map(Point,zip(xy[:,0],xy[:,1]))),obj['path']['density'],properties=properties)
  
  if not os.path.exists(obj['path']['domain']):
    domain=Point((-63.553987,44.627934,0.001)).buffer(1)  
    domain.write(obj['path']['domain'])
  
  osm=OSM(obj)
  print(osm.osmFetch.xy)
  
  

  

if __name__ == "__main__":
  # test_downloadOSM()
  # test_extractOSM()
  test_unionOSM()
  
  None