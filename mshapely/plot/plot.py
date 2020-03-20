""" Matplorlib wrapper to quickly plot shapely geometry
Notes
-----

TODO: add properties and color

"""

import matplotlib.pyplot as plt

def plotPoints(points,type='o',axe=None):
  xy=points.xy
  canvas = plt if axe is None else axe
  canvas.plot(xy[:,0],xy[:,1], type)
  
def plotPolygon(polygon,type='-',axe=None,):
  xy = polygon.exterior.xy
  canvas = plt if axe is None else axe
  canvas.plot(xy[:,0],xy[:,1], type)
  for interior in list(polygon.interiors):
    xy = interior.xy
    canvas.plot(xy[:,0],xy[:,1], type)
  

def plotLineString(linestring,type='-',axe=None,):
  xy = linestring.xy
  canvas = plt if axe is None else axe
  canvas.plot(xy[:,0],xy[:,1], type)
    
    
def plotSave(name='plot.png',axe=None):
  plt.savefig(name)
  canvas = plt if axe is None else axe
  canvas.clf()