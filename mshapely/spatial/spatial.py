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
  
  Example
  ------ 
  TODO
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
  
  Example
  ------ 
  TODO
  """     
  # interiors = [Polygon(interior) for interior in list(polygon.interiors)]
  # print("Julien")
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
    

def dsimplify_Polygon(polygon,df,limitFineDensity=1000,fine=None,coarse=None):
  """
  Simplify polygons and remove points by respecting minimum density field.
  It mainly uses the buffer/unbuffer techniques for different density area/zone.
  
  Parameters
  ----------
  polyon:Polygon
  df:Density field
  limitFineDensity:
  fine:
  coarse:
  
  Notes
  -----
  Correction buffers are used to correc geometric issues.
  
  TODO: points should be replace by features to include points,lines and polygons
    
  """
  
  points = df.dp
  xy = points[:, [0, 1]]
  density = points[:, 2]
  udensity = np.unique(density)
  
  steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4,4E4,7E4,1E5,2E5,4E5,7E5],dtype=np.float32)
  # steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4],dtype=np.float32)
  steps=steps[steps<polygon.length]
  minDensity = df.minDensity
  maxDensity = df.maxDensity
  minGrowth = df.minGrowth
  maxDensity=np.minimum(maxDensity,polygon.length*0.1)
  maxDistance = DF.getl_D(minDensity,minGrowth,maxDensity)
  
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
      
      zone=ozone.buffer(-_d*0.1).buffer(_d*0.1).removeHoles(cArea(_d*0.1)).simplify(_d*0.01)
      
      if not zone.is_empty:
        ozones.append(zone.getExterior().union(mps.buffer(-_d*0.1)))
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
  t=tqdm(total=len(steps), unit_scale=True)
  for i,d in enumerate(steps):
    _dd=DF.getD_l(minDensity,minGrowth,d)
    if(_dd>limitFineDensity):
      coarse=coarse.simplify(_dd*0.01).buffer(0)
      opolygon=coarse
    else:
      fine=fine.simplify(_dd*0.01).buffer(0)
      opolygon=fine
    ndomain,prev=process(opolygon,ndomain,prev,d)
    # ndomain.plot()
    t.update(1)
  t.close()
  
  ndomain,prev=process(None,ndomain,prev,maxDistance,polygon)
  
  return ndomain


def DotProduct(A,B):
  return A[...,0]*B[...,0]+A[...,1]*B[...,1]

def CrossProduct(A,B):
  return A[...,0]*B[...,1]-A[...,1]*B[...,0]

def _CrossProduct(A,B):
  
  return A[...,0]*B[...,1]-A[...,1]*B[...,0]


def _inearest_Polygon(p2,p1,angle=90.0):
  
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
  targets[targets==0]=maxValue
  
  
  m=np.min(targets,axis=1)
  
  return m

def inearest_Polygon(polygon,maxDistance=1.0,angle=90.0,nvalue=100):
  """
  Computes nearest interior nodes
  
  Parameters
  ----------
  
  polygon:Polygon
    2D array, shape(npoints,2)
  maxDistance:float
  angle:
  nvalue:int
    npoints to search kdtree
  
  """
  points = polygon._np(isNorm=True,onPoint=True)
  xy=points[:,-2:]
  
  kdtree = spatial.cKDTree(xy)
  npoints = len(points)
  
  inearest = np.zeros(npoints) + maxDistance
  t=tqdm(total=npoints,unit_scale=True)
  
  for x in range(0,npoints,nvalue):
    xn = np.minimum(npoints,x+nvalue)
    subpoints = points[x:xn]
    l = kdtree.query_ball_point(subpoints[:,-2:],maxDistance)
    l,e=ll2numpy(l)
    inearest[x:xn]=_inearest_Polygon(xy[l],subpoints,angle)
    t.update(xn-x)
  t.close()
  
  points = np.column_stack((xy,inearest))
  
  return points
  