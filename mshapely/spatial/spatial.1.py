import warnings
import numpy as np
from scipy import spatial
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection
from shapely.ops import cascaded_union,split,nearest_points,linemerge,snap
from tqdm import tqdm
from ..linalg import norm,rotate
from .density import DF

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


def _ll2numpy(l):
  """
  Converts kdtree list of lits to numpy array
  
  Parameters
  ----------
  l:list[list[int]] 
    List of lists of integers
  
  Note
  ----
  List of lists can have different array shape.
  Thus, the maximum array shape is taken (length) and fills for smaller arrays with its first value (li[0]).
  
  Example
  ------ 
  TODO
  """  
  length = max(map(len, l))
  return np.asarray([li+[li[0]]*(length-len(li)) for li in l],dtype=np.int)

# def dsimplify_Point(points,minDensity=1.0, maxDensity=10.0,*args,**kwargs):
#   """
#   Simplify/remove points by respecting minimum density field.
  
#   Parameters
#   ----------
#   points:ndarray
#     shape(npoint,3)
#   minDensity: 
#     default=1.0
#   maxDensity: 
#     default=10.0
  
#   Note
#   ----
#   The algorithm uses a stepping approach by gradually increasing the growth n value and gradually removing points.
#   This avoids searching large quantities of unnecessary points.
  
#   Example
#   ------ 
#   TODO
#   """  
#   newpoints=points
#   temppoints=np.array([])
  
#   i=1
#   growths=points[:,3]
#   mingrowth=np.min(growths)
#   n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(mingrowth)-1),1)
#   # while(len(temppoints)!=len(newpoints)):
#   while(i<=n):
#     temppoints=newpoints
#     tempDensity = np.minimum(minDensity*np.power(mingrowth,i),maxDensity)
#     newpoints=_dsimplify_Point(temppoints,minDensity=minDensity,maxDensity=tempDensity,mingrowth=mingrowth,*args,**kwargs)
#     i=i+1
    
#   return newpoints 

# def _dsimplify_Point(points,minDensity=1.0, maxDensity=10.0, mingrowth=1.2,balanced_tree=True):
#   """
#   The algorithm to simplify/remove points by respecting minimum density field.
#   See dsimplify_Point for more information
  
#   """  
#   nvalue=1000
  
#   xy = points[:, [0, 1]]
#   density = points[:, 2]
#   growth = points[:, 3]
#   npoints = xy.shape[0]
  
#   kdtree = spatial.cKDTree(xy,balanced_tree=balanced_tree)
  
#   n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(mingrowth)-1),1)
#   maxDistance = (minDensity*np.power(mingrowth,n+1)-minDensity)/(mingrowth-1)
  
#   keepindices=np.zeros(npoints,dtype=np.int)
#   for x in range(0,npoints,nvalue):
#     xn = np.minimum(npoints,x+nvalue)
#     array = np.arange(x,xn)
#     subpoints = xy[array]
    
#     l = kdtree.query_ball_point(subpoints,maxDistance)
#     l=_ll2numpy(l) 
    
#     distances = np.linalg.norm(xy[l] - subpoints[:,None], axis=2)
#     nn=np.log(distances*(growth[l]-1)/density[l]+1)/np.log(growth[l])
#     dd = density[l]*np.power(growth[l], nn)
    
#     ii=np.argmin(dd,axis=1)
#     iii=np.squeeze(np.take_along_axis(l,ii[:,None],axis=1))
    
#     keepindices[x:xn]=iii
    
#   # print(points[np.where(xy[:,1]<-4020000)[0],2])
#   uniques=np.unique(keepindices)
#   return points[uniques]


def cArea(d):
  """
  Area of circle
  
  Parameters
  ----------
  d:float
    diameter
  """
  return np.pi*np.power(d*0.5,2.)
    

def dsimplify_Polygon(polygon,points,minDensity=1,maxDensity=10,mingrowth=1.2,limitFineDensity=1000,fine=None,coarse=None):
  """
  Simplify polygons and remove points by respecting minimum density field.
  It mainly uses the buffer/unbuffer techniques for different density area/zone.
  
  Parameters
  ----------
  polyon:Polygon
  points:ndarray
    shape(npoint,3)
  minDensity:float
  maxDensity:float
  growth:float
  cB:float
    Correction buffer
  
  Notes
  -----
  Correction buffers are used to correc geometric issues.
  
  TODO: points should be replace by features to include points,lines and polygons
    
  """
  
  
  
  points = dsimplify_Point(points,minDensity=1,maxDensity=10)
  
  xy = points[:, [0, 1]]
  density = points[:, 2]
  udensity = np.unique(density)
  
  
  
  
  steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4,4E4,7E4,1E5,2E5,4E5,7E5],dtype=np.float32)
  # steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4],dtype=np.float32)
  steps=steps[steps<polygon.length]
  maxDensity=np.minimum(maxDensity,polygon.length*0.1)
  maxDistance = DF.getl_D(minDensity,mingrowth,maxDensity)
  
  polygon=polygon.buffer(0)
  if fine:fine=fine.buffer(0)
  if coarse:coarse=coarse.buffer(0)
  
  def getZones(tpolygon,d):
    ozones=[]
    zones=[]
    for unique in udensity:
      mps=MultiPoint(xy[density==unique]).buffer(d)
      _d = DF.getD_l(unique,mingrowth,d)
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
    _dd=DF.getD_l(minDensity,mingrowth,d)
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
  
  # prev.plot("o-")
  # ndomain.plot("o-")
  
  
  # t=tqdm(total=1, unit_scale=True)  
  # # outline=coarse.simplify(_dd*0.1)
  
  # outline=outline.buffer(-maxDensity*0.1).buffer(maxDensity*0.1)
  # if not outline.is_empty:
    # outline=outline.removeHoles(cArea(maxDensity*0.1)).simplify(maxDensity*0.01)
    
  ndomain,prev=process(None,ndomain,prev,maxDistance,polygon)
  # t.update(1);t.close()  
  
  
  
  # ndomain.plot("o-")
  
  
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
    l=_ll2numpy(l)
    inearest[x:xn]=_inearest_Polygon(xy[l],subpoints,angle)
    t.update(xn-x)
  t.close()
  
  points = np.column_stack((xy,inearest))
  
  return points
  