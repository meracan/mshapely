import warnings
import numpy as np
from scipy import spatial
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString
from shapely.ops import cascaded_union,split,nearest_points,linemerge,snap
from tqdm import tqdm

from .df import DF

def resample_LineString(linestring, maxLength=1.0):
  """
  Resample object using equal segment length. 
  The segment is automatically calculated using the length of the LineString and maxLength parameter.
  The segment is equal or smaller than the maxLength.
  
  Parameters
  ----------
  maxLength: float,optional
    Default is 1.0.
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
  if maxLength <= 0.0: return linestring
  n = np.max([np.ceil(linestring.length / maxLength), 3.0])
  length = linestring.length / n
  segments = [Point(list(linestring.coords)[0])]
  for i in range(int(n) - 1):
    p2 = linestring.interpolate(length * (i + 1))
    segments.append(p2)
  return LineString(segments)


def resample_Polygon(polygon, *args, **kwargs):
  exterior = Polygon(_resample_Polygon(polygon.exterior, *args, **kwargs))
  interiors = [Polygon(_resample_Polygon(interior, *args, **kwargs)) for interior in polygon.interiors]
  interiors = cascaded_union(interiors)
  return exterior.difference(interiors)
resample_Polygon.__doc__=resample_LineString.__doc__

def _dresample_LineString(linestring, df,progress=False):
  minDensity=df.minDensity
  maxDensity=df.maxDensity
  minGrowth=df.minGrowth
  if(linestring.length<minDensity):
    warnings.warn("LineString is shorter than minDensity")
    return linestring
  maxDistance=DF.getl_D(minDensity,minGrowth,maxDensity)
  
  flip=False
  if(df.getDensity([linestring.coords[-1]])<df.getDensity([linestring.coords[0]])):
    flip=True
    linestring=LineString(reversed(linestring.coords))
  
  length = 0
  p = linestring.interpolate(length)
  segments = [p]
  end=[]
  if progress:t=tqdm(total=int(linestring.length),position=1)
  while (length+minDensity<= linestring.length):
    pl=p
    distancel = df.getDensity(pl.xy)
    tlength = length + distancel
    pr = linestring.interpolate(tlength)
    distancer = df.getDensity(pr.xy)
    
    distance =np.minimum(distancel,distancer)[0]   
    
    # This array is saved to smooth out the end
    if(length+maxDistance>linestring.length):
      end.append(dict(distance=distance,length=length))
    
    length += distance
    p = linestring.interpolate(length)
    segments.append(p)
    
    if progress:t.update(int(distance))
  if progress:t.close()

  # Smooth out the end
  # Get last point, get density, smooth out using points within maxDistance
  # print(LineString(segments))
  extra = (length - linestring.length)
  n=len(end)
  lp=df.getDensity([linestring.coords[-1]])
  v = np.array([np.maximum(o['distance']-lp,0) for o in end])
  s = np.sum(v)
  
  if s==0:
    v = np.array([np.maximum(o['distance']-minDensity,0) for o in end])
    s = np.sum(v)
  u=v/s*extra
  
  # print(v,s,u,extra)
  # print(segments)
  if(n!=0): # Special case when the segment is shorter than the minDensity
    segments = segments[:-n]
    
    length = end[0]['length']
    # print(end)
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

def dresample_LineString(linestring,df,mp=None,*args, **kwargs):
  """ 
  Resample object using a 2D Density Field object. 
  The length of the segments are automatically calculated using the Density Field.
  
  Parameters
  ----------
  df: Density Field object
  mp:MultiPoint,optional
   MultiPoint are part of the resampling. 
   An error will raise if the distance between points are smaller than minDensity.
   
  """  
  if(mp is not None):
    segments = _split_line_with_multipoint(linestring,mp)
    return linemerge([_dresample_LineString(s,df,*args, **kwargs) for s in segments])
  else:
    return _dresample_LineString(linestring,df,*args, **kwargs)


  
def dresample_Polygon(polygon,*args, **kwargs):
  progress=False
  temp=kwargs
  if 'progress' in kwargs:
    progress=kwargs['progress']
    del temp['progress']
  
    
  if progress:t=tqdm(total=len(polygon.interiors)+1,position=0)
  exterior = Polygon(dresample_LineString(polygon.exterior,*args, **kwargs))
  if progress:t.update(1)
  interiors=[]
  for interior in polygon.interiors:
    _r = dresample_LineString(interior,*args, **kwargs)
    
    if len(_r.coords)<4 or not _r.is_ring:continue
    newinterior = Polygon(_r)
    if not newinterior.is_empty:
      _n= newinterior.exterior
      coords = _n.coords[::-1] if not _n.is_ccw else _n.coords
      interiors.append(coords)
    if progress:t.update(1)
  if progress:t.close()
  
  # raise Exception("asd")
  return Polygon(exterior.exterior,interiors)
dresample_Polygon.__doc__=dresample_LineString.__doc__


def _split_line_with_point(line, splitter):
  """ 
  Split a LineString with a Point
  
  Parameters
  ----------      

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