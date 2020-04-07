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

def segmentsLength(points):
  n = len(points)
  isClosed = np.array_equal(points[0], points[n - 1])
  if isClosed:points=points[:n-1]
  n=len(points)
  p0 = points
  
  p1 = np.roll(p0, 1, axis=0)
  p2 = np.roll(p0, -1, axis=0)
    
  d1=np.linalg.norm(p1 -p0, axis=1)
  d2=np.linalg.norm(p2 -p0, axis=1)
  minDistance=np.minimum(d1,d2)
  
  newpoints=np.column_stack((minDistance,points))
  if isClosed:
    newpoints=np.append(newpoints,newpoints[0][None,:],axis=0)
    
  return newpoints
  
def linestring2numpy(line,isNorm=False,isSegment=False,*args, **kwargs):
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
  if isSegment:
    points = segmentsLength(points, *args, **kwargs)
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
  ndarray(2D),[x,y]
  
  Example
  ------ 
  TODO
  
  """  
  return np.concatenate([point2numpy(p) for p in s])


def multilinestring2numpy(s, *args, **kwargs):
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
    temp = linestring2numpy(p, *args, **kwargs)
    n = len(temp)
    id = np.zeros(n) + i
    temp = np.column_stack((id, temp))
    multi.append(temp)
  
  return np.concatenate(multi)


def multipolygon2numpy(s, *args, **kwargs):
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
    temp = polygon2numpy(p, *args, **kwargs)
    n = len(temp)
    id = np.zeros(n) + i
    temp = np.column_stack((id, temp))
    multi.append(temp)
  
  return np.concatenate(multi)