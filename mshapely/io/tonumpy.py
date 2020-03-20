import numpy as np
from ..linalg import norm,normalVector

def point2numpy(point):
  """
  Converts shapely points to numpy array
  
  Parameters
  ----------
  point: Point
  
  Output
  ------ 
  ndarray(2D),[x,y]
  
  Example
  ------ 
  TODO
  
  """
  return np.array(point.coords.xy).T
  
def linestring2numpy(line,isNorm=False,*args, **kwargs):
  """
  Converts shapely LineString to numpy array
  
  Parameters
  ----------
  line: LineString
  isNorm: bool
    Compute normal vectors
  
  Output
  ------ 
  ndarray(2D),[id,x,y,(xn,yn)]
  
  Example
  ------ 
  TODO
  
  """  
 
  points = np.array(line.coords.xy).T
  n = len(points)
  if isNorm:
    points = normalVector(points, *args, **kwargs)
  pointids = np.arange(n)
  if (np.array_equal(points[0], points[n - 1])):
    pointids[n - 1] = 0
  return np.column_stack((pointids, points))

  
def polygon2numpy(polygon, *args, **kwargs):
  """
  Converts shapely Polygon to numpy array
  
  Parameters
  ----------
  polygon: Polygon
  
  Output
  ------ 
  ndarray(2D),[lid,id,x,y,(xn,yn)]
  
  Example
  ------ 
  TODO
  
  """  
  exterior = linestring2numpy(polygon.exterior, *args, **kwargs)
  
  n = len(exterior)
  lineID=0
  lineid = np.zeros(n)
  exterior = np.column_stack((lineid, exterior))
  # exterior = exterior[:-1]  # remove last point
  if len(polygon.interiors) == 0: return exterior
  interiors = []
  for interior in polygon.interiors:
    interior = linestring2numpy(interior, *args, **kwargs)
    n = len(interior)
    lineID += 1
    lineid = np.zeros(n) +lineID
    interior = np.column_stack((lineid, interior))
    # interior = interior[:-1]  # remove last point
    interiors.append(interior)
  
  interiors = np.concatenate(interiors)
  return np.concatenate((exterior, interiors))
  
def multipoint2numpy(s):
  """
  Converts shapely MultiPoint to numpy array
  
  Parameters
  ----------
  s: MultiPoint
  
  Output
  ------ 
  ndarray(2D),[id,x,y]
  
  Example
  ------ 
  TODO
  
  """  
  multi = np.concatenate([point2numpy(p) for p in s])
  return np.column_stack((np.arange(len(multi)), multi))


def multilinestring2numpy(s):
  """
  Converts shapely MultiLineString to numpy array
  
  Parameters
  ----------
  s: MultiPoint
  
  Output
  ------ 
  ndarray(2D),[lid,id,x,y]
  
  Example
  ------ 
  TODO
  
  """  

  multi = []
  for i, p in enumerate(s):
    temp = linestring2numpy(p)
    n = len(temp)
    id = np.zeros(n) + i
    temp = np.column_stack((id, temp))
    multi.append(temp)
  
  return np.concatenate(multi)


def multipolygon2numpy(s):
  """
  Converts shapely MultiPolygon to numpy array
  
  Parameters
  ----------
  s: MultiPoint
  
  Output
  ------ 
  ndarray(2D),[pid,lid,id,x,y]
  
  Example
  ------ 
  TODO
  
  """    
  
  multi = []
  for i, p in enumerate(s):
    temp = polygon2numpy(p)
    n = len(temp)
    id = np.zeros(n) + i
    temp = np.column_stack((id, temp))
    multi.append(temp)
  
  return np.concatenate(multi)