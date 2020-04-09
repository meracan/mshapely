import warnings
import numpy as np
from scipy import spatial
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection
from shapely.ops import cascaded_union,split,nearest_points,linemerge,snap
from tqdm import tqdm
from ..linalg import norm,rotate
from .df import DF
from ..misc import ll2numpy

def removeHoles_Polygon(polygon, area=1.0):
  """
  Remove holes based on area
  
  Parameters
  ----------
  polygon: 
  area: 
    default=1.0
  """     
  interiors = [Polygon(interior) for interior in list(polygon.interiors)]
  areas = np.array([interior.area for interior in interiors])
  indexes = np.where(areas > area)[0]
  interiors = [interiors[i].exterior for i in indexes]
  
  return Polygon(polygon.exterior,interiors)

def remove_Polygons(polygons, area=1.0):
  """
  Remove small polygons based on area
  
  Parameters
  ----------
  polygons:MultiPolygon 
  area: 
    default=1.0
  """     
  areas = np.array([polygon.area for polygon in list(polygons)])
  indexes = np.where(areas > area)[0]
  polygons = [polygons[i] for i in indexes]
  if len(polygons)==1:return polygons[0]
  return MultiPolygon(polygons)

def cArea(d):
  """
  Area of circle
  
  Parameters
  ----------
  d:float
    diameter
  """
  return np.pi*np.power(d*0.5,2.)
    



def dsimplify_Polygon(polygon,df,limitFineDensity=1000,limitCoarseDensity=10000,fine=None,coarse=None,progress=False):
  """
  Simplify polygons and remove points by respecting Density Field.
  It mainly uses the buffer/unbuffer techniques for different density area/zone.
  The zones are created using different buffer distance on the density points.
  To speed up simplification, the function allows fine and coarse resolution polygons
  
  Parameters
  ----------
  polyon:Polygon
    Domain or outline
  df:Density Field
  limitFineDensity:float
    Threshold value to swtich from fine to coarse
  fine:Polygon or MultiPolygon
    Fine resolution data
  coarse:Polygon or MultiPolygon
    Coarse resolution data
  """
  
  points = df.dp
  xy = points[:, [0, 1]]
  density = points[:, 2]
  udensity = np.unique(density)
  
  steps = np.array([
    1E1,2E1,4E1,7E1,
    1E2,2E2,4E2,7E2,
    1E3,2E3,4E3,7E3,
    1E4,2E4,4E4,7E4,
    1E5,2E5,4E5,7E5,
    1E6,2E6,4E6,7E6,
    1E7,2E7,4E7,7E7],dtype=np.float32)
  # steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4],dtype=np.float32)
  steps=steps[steps<polygon.length]
  minDensity = df.minDensity
  maxDensity = df.maxDensity
  minGrowth = df.minGrowth
  maxDensity=np.minimum(maxDensity,polygon.length*0.1)
  maxDistance = DF.getl_D(minDensity,minGrowth,limitCoarseDensity)
  
  polygon=polygon.buffer(0)
  if fine:fine=fine.buffer(0)
  else:fine=polygon
  if coarse:coarse=coarse.buffer(0)
  else:coarse=polygon
  
  def getZones(tpolygon,d):
    ozones=[]
    zones=[]
    for unique in udensity:
      mps=MultiPoint(xy[density==unique]).buffer(d)
      _d = DF.getD_l(unique,minGrowth,d)
      _d = np.maximum(minDensity,_d) 
      ozone=mps.intersection(tpolygon)
      
      zone=ozone.buffer(-_d*0.2).buffer(_d*0.2).removeHoles(cArea(_d*0.2)).simplify(_d*0.01)
      
      if not zone.is_empty:
        ozones.append(zone.getExterior().union(mps.buffer(-_d*0.2)))
      #  ozones.append(mps)
        zones.append(zone)
    
    ozones=cascaded_union(ozones)
    zones=cascaded_union(zones)
    # zones.plot("o-")
    return zones,ozones
  
  
  def process(domain,newdomain,prev,d,outline=None):
    if outline is not None:
      newzones=outline.difference(prev).buffer(1)
      
      if not newzones.is_empty: 
        newdomain=newdomain.union(newzones).buffer(0.01).simplify(1)
      return newdomain,prev
      
    zones,ozones = getZones(domain,d)
    if newdomain is None:return zones,ozones
    if zones.is_empty:return newdomain,prev
    newzones=zones.difference(prev).buffer(1)
    # if i==11:newzones.plot("o-")
    if not ozones.is_empty:prev=ozones
    if newzones.is_empty: return newdomain,prev
    newdomain=newdomain.union(newzones).buffer(0.01).simplify(1)
    # if i==11:newdomain.plot("o-")
    return newdomain,prev
  
  
  steps=steps[steps>=minDensity]
  steps=steps[steps<maxDistance]
  
  ndomain=None
  prev=None
  _dd=None
  if progress:t=tqdm(total=len(steps), unit_scale=True)
  for i,d in enumerate(steps):
    _dd=DF.getD_l(minDensity,minGrowth,d)
    if(_dd>limitFineDensity):
      coarse=coarse.simplify(_dd*0.01).buffer(0)
      opolygon=coarse
    else:
      fine=fine.simplify(_dd*0.01).buffer(0)
      opolygon=fine
    # opolygon.plot(polygonStyle={"facecolor":(0,0,0,0)})
    
    
    ndomain,prev=process(opolygon,ndomain,prev,d)
    # ndomain.plot()
    # ndomain.savePlot("../data/example2/temp.{}.png".format(i))
    # ndomain.plot()
    if progress:t.update(1)
  if progress:t.close()
  
  
  # ndomain.plot()
  # ndomain.savePlot("../data/example2/temp.{}.png".format("00"))
  ndomain,prev=process(None,ndomain,prev,maxDistance,polygon)
  # ndomain.plot()
  # ndomain.savePlot("../data/example2/temp.{}.png".format("000"))
  return ndomain


def DotProduct(A,B):
  return A[...,0]*B[...,0]+A[...,1]*B[...,1]

def CrossProduct(A,B):
  return A[...,0]*B[...,1]-A[...,1]*B[...,0]

def _CrossProduct(A,B):
  
  return A[...,0]*B[...,1]-A[...,1]*B[...,0]


def _inearest_Polygon(p2,p1,angle=90.0,minDistance=0):
  
  xy=p1[:,-2:]
  V2=p1[:,-4:-2]
  
  
  rad1=np.zeros(len(V2))- np.radians(angle*0.5)
  rad2=np.zeros(len(V2))+ np.radians(angle*0.5)
  
  V2N=np.column_stack((V2, np.ones(len(V2))))
  V2R1 = np.einsum('aij,aj->ai', rotate(rad1), V2N)[...,:-1]
  V2R2 = np.einsum('aij,aj->ai', rotate(rad2), V2N)[...,:-1]
  
  
  V1 = p2 - xy[:,None]
  targets = np.linalg.norm(V1, axis=2)
  VV1=V1/targets[:,:,None]
  indices=(_CrossProduct(V2R1[:,None], VV1) >= 0) & (_CrossProduct(VV1, V2R2[:,None]) >= 0)
  
  maxValue=np.maximum(1,np.max(targets))
  targets[np.invert(indices)]=maxValue
  targets[targets<=minDistance]=maxValue
  
  
  m=np.min(targets,axis=1)
  
  return m

def inearest_Polygon(polygon,maxDistance=1.0,nvalue=100,progress=False,**kwargs):
  """
  Computes nearest interior nodes based on its normal and an angle spread.
  The maximum search distance needs to be specified to avoid searching large quantities of points in large domains. 
  
  Parameters
  ----------
  maxDistance:float
   Maximum search distance.
   Default is 1.0
  minDistance:float
    Minimum search distance
    Default is 0.0
  angle:float,0<angle<180.0 
   Angle spread.  Limits the search within the angle spread.
   Default value is 90.0. 
  nvalue:int
    Number of points processed at the same time.
    Default is 1000
  
  Output
  ------
  ndarray:2D array
   shape:(n,3)
    n: Number of points in the original object.
    3:x,y,density  
  """
  points = polygon._np(isNorm=True,onPoint=True)
  xy=points[:,-2:]
  
  kdtree = spatial.cKDTree(xy)
  npoints = len(points)
  
  inearest = np.zeros(npoints) + maxDistance
  if progress:t=tqdm(total=npoints,unit_scale=True)
  
  for x in range(0,npoints,nvalue):
    xn = np.minimum(npoints,x+nvalue)
    subpoints = points[x:xn]
    l = kdtree.query_ball_point(subpoints[:,-2:],maxDistance)
    l,e=ll2numpy(l)
    inearest[x:xn]=_inearest_Polygon(xy[l],subpoints,**kwargs)
    if progress:t.update(xn-x)
  if progress:t.close()
  
  points = np.column_stack((xy,inearest))
  
  return points
  