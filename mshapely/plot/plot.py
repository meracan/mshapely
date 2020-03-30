""" Matplorlib wrapper to quickly plot shapely geometry
Notes
-----

TODO: add properties and color

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def ring_coding(ob):
    # The codes will be all "LINETO" commands, except for "MOVETO"s at the
    # beginning of each subpath
    n = len(ob.coords)
    codes = np.ones(n, dtype=Path.code_type) * Path.LINETO
    codes[0] = Path.MOVETO
    return codes

def pathify(polygon):
    # Convert coordinates to path vertices. Objects produced by Shapely's
    # analytic methods have the proper coordinate order, no need to sort.
    vertices = np.concatenate(
                    [np.asarray(polygon.exterior)]
                    + [np.asarray(r) for r in polygon.interiors])
    codes = np.concatenate(
                [ring_coding(polygon.exterior)]
                + [ring_coding(r) for r in polygon.interiors])
    return Path(vertices, codes)


def plotPoints(points,type='o',axe=None,colors=None):
  xy=points.xy
  canvas = plt if axe is None else axe
  canvas.scatter(xy[:,0], xy[:,1], c=colors,alpha=0.75)
  # canvas.plot(xy[:,0],xy[:,1], type)

def plotPolygons(polygons,*args,**kwargs):
  xy=polygons.xy
  xmin, xmax = (np.min(xy[:,0]),np.max(xy[:,0]))
  ymin, ymax = (np.min(xy[:,1]),np.max(xy[:,1]))
  
  
  axe=kwargs.get("axe",None)
  canvas = plt if axe is None else axe
  # if axe is not None:
  canvas.set_xlim(xmin, xmax)
  canvas.set_ylim(ymin, ymax)
  
  for polygon in polygons:
    polygon.plot(setLimits=False,*args,**kwargs)
  
def plotPolygon(polygon,type='o',axe=None,style="plot",color=None,setLimits=True):
  canvas = plt if axe is None else axe
  path = pathify(polygon)
  patch = PathPatch(path, facecolor=color, edgecolor='black',zorder=0)

  # Centering
  if setLimits:
    xy=polygon.xy
    xmin, xmax = (np.min(xy[:,0]),np.max(xy[:,0]))
    ymin, ymax = (np.min(xy[:,1]),np.max(xy[:,1]))
    canvas.set_xlim(xmin-1, xmax+1)
    canvas.set_ylim(ymin-1, ymax+1)
  
  canvas.add_patch(patch)
  if type=="o":
    canvas.scatter(xy[:,0], xy[:,1], c="black",alpha=0.75,zorder=1)
    
  
  # xy=polygon.exterior.xy
  # canvas.plot(xy[:,0],xy[:,1],type)
  # for interior in polygon.interiors:
  #   xy=interior.xy
  #   canvas.plot(xy[:,0],xy[:,1],type)
  

def plotLineString(linestring,type='-',axe=None,):
  xy = linestring.xy
  canvas = plt if axe is None else axe
  canvas.plot(xy[:,0],xy[:,1], type)
    
    
def plotSave(name='plot.png',axe=None):
  plt.savefig(name)
  canvas = plt if axe is None else axe
  canvas.clf()