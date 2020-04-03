""" Matplorlib wrapper to quickly plot shapely geometry
Notes
-----

TODO: add properties and color

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from inspect import signature


def preprocess(function):
  """
  Decorator for static methods to check input
  """
  def wrapper(geo,*args,**kwargs):
    fig=kwargs.get("fig",None)
    axe=kwargs.get("axe",None)
    defaultPointStyle={"c":"blue", "alpha":1.0,"zorder":1}
    defaultLineStyle={"c":"blue","linestyle":'solid', "alpha":0.75,"zorder":1,"marker":None}
    defaultPolygonStyle={"facecolor":"blue", "edgecolor":'black',"zorder":0}
    
    
    kwargs['pointStyle']={**defaultPointStyle, **kwargs.get("pointStyle",{})}
    kwargs['lineStyle']={**defaultLineStyle, **kwargs.get("lineStyle",{})}
    kwargs['polygonStyle']={**defaultPolygonStyle, **kwargs.get("polygonStyle",{})}
    
    if axe is None:
      fig, axe = plt.subplots(figsize=(8,8))
      fig.tight_layout()
      axe.set_aspect('equal')
    
    extent=kwargs.get("extent",None)  
    
    if extent is None:
      xy=geo.xy
      xmin, xmax = (np.min(xy[:,0]),np.max(xy[:,0]))
      ymin, ymax = (np.min(xy[:,1]),np.max(xy[:,1]))    
      
      padx = (xmax-xmin)*0.05
      pady = (ymax-ymin)*0.05
      extent=[xmin-padx,ymin-pady,xmax+padx,ymax+pady]
    
    kwargs['extent']=extent
    axe.set_xlim(extent[0], extent[2])
    axe.set_ylim(extent[1], extent[3])
    kwargs['fig']=fig
    kwargs['axe']=axe

    
    return function(geo,*args,**kwargs)
  return wrapper


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

@preprocess
def plotPoints(points,**kwargs):
  axe=kwargs["axe"]
  fig=kwargs["fig"]
  showColorbar=kwargs.get("showColorbar",False)
  
  xy=points.xy
  h=axe.scatter(xy[:,0], xy[:,1], **kwargs)
  if showColorbar:
    fig.colorbar(h)

@preprocess
def plotPolygons(polygons,*args,**kwargs):
  """
  Plot Polygons
  """
  for polygon in polygons:
    polygon.plot(*args,**kwargs)

@preprocess
def plotLineStrings(lines,*args,**kwargs):
  """
  Plot Polygons
  """
  for line in lines:
    line.plot(*args,**kwargs)

@preprocess  
def plotPolygon(polygon,*args,**kwargs):
  """
  Plot Polygon
  """
  axe=kwargs["axe"]
  fig=kwargs["fig"]
  pointStyle = kwargs['pointStyle']
  polygonStyle = kwargs['polygonStyle']
  showPoints=kwargs.get("showPoints",False)
  
  path = pathify(polygon)
  patch = PathPatch(path, **polygonStyle)
  axe.add_patch(patch)
  if showPoints:
    xy=polygon.xy
    axe.scatter(xy[:,0], xy[:,1], **pointStyle)

@preprocess
def plotLineString(linestring,*args,**kwargs):
  """
  Plot LineString
  """  
  axe=kwargs["axe"]
  fig=kwargs["fig"]
  lineStyle = kwargs['lineStyle']
  
  xy = linestring.xy
  axe.plot(xy[:,0],xy[:,1], **lineStyle)
    
    
def plotSave(name='plot.png'):
  plt.savefig(name)
  plt.clf()