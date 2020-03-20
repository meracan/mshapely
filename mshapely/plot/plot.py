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
  
def plotPolygon(polygon,type='-',axe=None,style="plot",color=None):
  # style="plot","fill"
  xy = polygon.exterior.xy
  canvas = plt if axe is None else axe
  xy=polygon.xy[:,-2:]
  if style=="plot":canvas.plot(xy[:,0],xy[:,1], type,color=color)
  else:canvas.fill(xy[:,0],xy[:,1], type,color=color)
  

def plotLineString(linestring,type='-',axe=None,):
  xy = linestring.xy
  canvas = plt if axe is None else axe
  canvas.plot(xy[:,0],xy[:,1], type)
    
    
def plotSave(name='plot.png',axe=None):
  plt.savefig(name)
  canvas = plt if axe is None else axe
  canvas.clf()