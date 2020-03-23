import numpy as np
from shapely.geometry import Point

import mshapely
from mshapely import OSM

def doc_general():
  obj = {
      "minDensity":10,
      "maxDensity":10000,
      "growth":1.2,
      "path":{
        "osm":"../data/example1.osm.geojson",
        "domain":"../data/example1.domain.geojson",
        "density":"../data/example1,density.geojson",
        "osmDomain":"../data/example1.osmDomain.geojson",
        "osmSimplify":"../data/example1.osmSimplify.geojson",
        "osmResample":"../data/example1.osmResample.geojson",
      }
    }
  
  # extent = [-65,43.5,-62,46]
  # OSM.extractOSM("../data/water-polygons-split-4326.zip",obj['path']['osm'],extent)
  
  # domain=Point((-63.553987,44.627934)).buffer(1) # 1 degree  
  # domain.write(obj['path']['domain'])
  
  # density = np.array([
  #   [-63.563342,44.634637,10],
  #   [-63.553987,44.627934,10],
  #   [-63.495436,44.606528,20],
  #   ])
  # xy=density[:,[0,1]]
  # properties = [{"density":x} for x in density[:,2]]
  # OSM.write(list(map(Point,zip(xy[:,0],xy[:,1]))),obj['path']['density'],properties=properties)
  osm=OSM(obj)
  osm.osmSimplify
  osm.osmResample
  
if __name__ == "__main__":
  doc_general()
  