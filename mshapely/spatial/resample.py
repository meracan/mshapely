import warnings
import numpy as np
from scipy import spatial
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString
from shapely.ops import cascaded_union,split,nearest_points,linemerge,snap

from .spatial import dsimplify_Point

def resample_LineString(linestring, maxLength=1.0):
  """
  Resample linstring based on maxLength
  
  Parameters
  ----------
  linestring: 
  maxLength: 
    (default=1.0)
  
  Example
  ------ 
  TODO
  """     
  if maxLength <= 0.0: return linestring
  n = np.max([np.ceil(linestring.length / maxLength), 1.0])
  length = linestring.length / n
  segments = [Point(list(linestring.coords)[0])]
  for i in range(int(n)):
    p2 = linestring.interpolate(length * (i + 1))
    segments.append(p2)
  return LineString(segments)


def _resample_Polygon(linestring, maxLength=1.0):
  """
  Resample Polygon based on maxLength
  
  Parameters
  ----------
  linestring: 
  maxLength: 
    (default=1.0)
  
  Example
  ------ 
  TODO
  """     
  
  if maxLength <= 0.0: return linestring
  n = np.max([np.ceil(linestring.length / maxLength), 3.0])
  length = linestring.length / n
  segments = [Point(list(linestring.coords)[0])]
  for i in range(int(n) - 1):
    
    p2 = linestring.interpolate(length * (i + 1))
    segments.append(p2)
  return LineString(segments)


def resample_Polygon(polygon, *args, **kwargs):
  """
  Resample Polygon
  
  Parameters
  ----------
  polygon: 
  
  Example
  ------ 
  TODO
  """ 
  exterior = Polygon(_resample_Polygon(polygon.exterior, *args, **kwargs))
  interiors = [Polygon(_resample_Polygon(interior, *args, **kwargs)) for interior in polygon.interiors]
  interiors = cascaded_union(interiors)
  return exterior.difference(interiors)


def _dresample_LineString(linestring, density, minDensity=1.0, maxDensity=10.0, growth=1.2):
  """ 
  Resample linestring based on density points
  
  Parameters
  ----------      
  density : 2D array points [n,xyd]
  minDensity: minimum density (default=1.0)
  minDensity: minimum density (default=10.0)
  growth: mesh growth factor (default=1.2)
  
  Example
  ------ 
  TODO
  """
  if(linestring.length<minDensity):warnings.warn("LineString is shorter than minDensity")
  if(linestring.length<minDensity*np.power(growth,0)):return linestring
  if(maxDensity<minDensity*np.power(growth,2)):
    maxDensity=minDensity*np.power(growth,2)
  
  # print(density.shape)
  
  density = dsimplify_Point(density,minDensity=1,maxDensity=10,growth=1.2)
  
  points = density[:, [0, 1]]
  density = density[:, 2]
  density[density<minDensity]=minDensity
  density[density>maxDensity]=maxDensity
  
  kdtree = spatial.cKDTree(points)
  n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(growth)-1),1)
  maxDistance = (minDensity*np.power(growth,n+1)-minDensity)/(growth-1)
  
  def getDistance(_p):
    index = kdtree.query_ball_point(_p, maxDistance)
    pts = points[index]
    distances = np.linalg.norm(pts - _p, axis=1)
    # print(distances)
    if len(distances) == 0:
      distance = maxDensity
    else:
      n = np.maximum(0,np.log(distances*(growth-1)/density[index]+1)/np.log(growth))
      # print(n)
      dd = density[index] * np.power(growth, n)
      distance = np.min(dd)
    
    
    return np.minimum(distance,maxDensity)
  
  flip=False
  if(getDistance(linestring.coords[-1])<getDistance(linestring.coords[0])):
    flip=True
    linestring=LineString(reversed(linestring.coords))
  
  length = 0
  p = linestring.interpolate(length)
  segments = [p]
  end=[]
  while (length+minDensity<= linestring.length):
    pl=np.array(p)
    distancel = getDistance(pl)
    tlength = length + distancel
    pr = linestring.interpolate(tlength)
    distancer = getDistance(pr)
    
    
    distance =np.minimum(distancel,distancer)   
    
    # This array is saved to smooth out the end
    if(length+maxDistance>linestring.length):
      end.append(dict(distance=distance,length=length))
    
    length += distance
    # print(distance)
    p = linestring.interpolate(length)
    segments.append(p)


  # Smooth out the end
  # Get last point, get density, smooth out using points within maxDistance
  # print(LineString(segments))
  extra = (length - linestring.length)
  n=len(end)
  lp=getDistance(linestring.coords[-1])
  v = np.array([np.maximum(o['distance']-lp,0) for o in end])
  s = np.sum(v)
  
  if s==0:
    v = np.array([np.maximum(o['distance']-minDensity,0) for o in end])
    s = np.sum(v)
  u=v/s*extra
  
  # print(v,s,u,extra)
  
  if(n!=0): # Special case when the segment is shorter than the minDensity
    segments = segments[:-n]
    length = end[0]['length']
    for i,_u in enumerate(u):
      length +=end[i]['distance']-_u
      
      p = linestring.interpolate(length)
      segments.append(p)
    
    # Make sure the last point is equal
    segments = segments[:-1]
  
  segments.append(linestring.coords[-1])
  newlinestring = LineString(segments)
  
  if(flip):newlinestring=LineString(reversed(newlinestring.coords))
  return newlinestring

def dresample_LineString(linestring,density,mp=None,*args, **kwargs):
  
  if(mp is not None):
    segments = _split_line_with_multipoint(linestring,mp)
    return linemerge([_dresample_LineString(s,density,*args, **kwargs) for s in segments])
  else:
    return _dresample_LineString(linestring,density,*args, **kwargs)


  
def dresample_Polygon(polygon,*args, **kwargs):
  """ 
  Resample Polygon with density points
  
  Parameters
  ----------      
  density : 2D array points [n,xyd]
  minDensity: minimum density (default=1.0)
  minDensity: minimum density (default=10.0)
  growth: mesh growth factor (default=1.2)
  
  Example
  ------ 
  TODO
  """   
  exterior = Polygon(dresample_LineString(polygon.exterior,*args, **kwargs))
  interiors = [Polygon(dresample_LineString(interior,*args, **kwargs)) for interior in polygon.interiors]
  interiors = cascaded_union(interiors)
  return exterior.difference(interiors)  


def resampleNear(linestring,feature,minDensity=1.0):
  """ 
  Resample Polygon with density points
  
  Parameters
  ----------      
  density : 2D array points [n,xyd]
  minDensity: minimum density (default=1.0)
  minDensity: minimum density (default=10.0)
  growth: mesh growth factor (default=1.2)
  
  Example
  ------ 
  TODO
  """   
  linestring=LineString(np.round(np.array(linestring.coords),12))
  featurepts= feature.resample(minDensity).xy
  splitters = []
  for xy in featurepts:
    p1,p2 = nearest_points(linestring, Point(xy))
    splitters.append(p1)
    # print(linemerge(_split_line_with_point(linestring, p1)))
    
  return linemerge(_split_line_with_multipoint(linestring,MultiPoint(splitters)))
  # return _linemerge_with_multipoint(linestring,MultiPoint(splitters))

def resampleNearPolygon(polygon, *args, **kwargs):
  """ 
  Resample Near for Polygon
  
  Parameters
  ----------      
  
  
  Example
  ------ 
  TODO
  """   
  
  exterior = Polygon(resampleNear(polygon.exterior, *args, **kwargs))
  interiors = [Polygon(resampleNear(interior, *args, **kwargs)) for interior in polygon.interiors]
  interiors = cascaded_union(interiors)
  return exterior.difference(interiors)





def _split_line_with_point(line, splitter):
  """ 
  Split a LineString with a Point
  
  Parameters
  ----------      
  
  
  Example
  ------ 
  TODO
  """     
  
  assert (isinstance(line, LineString))
  assert (isinstance(splitter, Point))

  line = LineString(np.round(np.array(line.coords), 12))
  
  # check if point is in the interior of the line
  if not line.relate_pattern(splitter, '0********'):
    # point not on line interior --> return collection with single identity line
    # (REASONING: Returning a list with the input line reference and creating a
    # GeometryCollection at the general split function prevents unnecessary copying
    # of linestrings in multipoint splitting function)
    return [line]
  elif line.coords[0] == splitter.coords[0]:
    # if line is a closed ring the previous test doesn't behave as desired
    return [line]
  
  # point is on line, get the distance from the first point on line
  distance_on_line = line.project(splitter)
  coords = list(line.coords)
  # split the line at the point and create two new lines
  # TODO: can optimize this by accumulating the computed point-to-point distances
  for i, p in enumerate(coords):
    pd = line.project(Point(p))
    if pd == distance_on_line:
      return [
        LineString(coords[:i + 1]),
        LineString(coords[i:])
      ]
    elif distance_on_line < pd or (i > 0 and pd == 0):
      # we must interpolate here because the line might use 3D points
      cp = line.interpolate(distance_on_line)
      ls1_coords = coords[:i]
      ls1_coords.append(cp.coords[0])
      ls2_coords = [cp.coords[0]]
      ls2_coords.extend(coords[i:])
      return [LineString(ls1_coords), LineString(ls2_coords)]


def _split_line_with_multipoint(line, splitter):
    """Split a LineString with a MultiPoint"""

    assert(isinstance(line, LineString))
    assert(isinstance(splitter, MultiPoint))

    chunks = [line]
    for pt in splitter.geoms:
        new_chunks = []
        for chunk in filter(lambda x: not x.is_empty, chunks):
            # add the newly split 2 lines or the same line if not split
            new_chunks.extend(_split_line_with_point(chunk, pt))
        chunks = new_chunks

    return chunks