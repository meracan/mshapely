import warnings
import numpy as np
from scipy import spatial
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,GeometryCollection
from shapely.ops import cascaded_union,split,nearest_points,linemerge,snap
from tqdm import tqdm
from ..linalg import norm,rotate


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

def dsimplify_Point(points,minDensity=1.0, maxDensity=10.0,growth=1.2,*args,**kwargs):
  """
  Simplify/remove points by respecting minimum density field.
  
  Parameters
  ----------
  points:ndarray
    shape(npoint,3)
  minDensity: 
    default=1.0
  maxDensity: 
    default=10.0
  growth: 
    default=1.2
  
  Note
  ----
  The algorithm uses a stepping approach by gradually increasing the growth n value and gradually removing points.
  This avoids searching large quantities of unnecessary points.
  
  Example
  ------ 
  TODO
  """  
  newpoints=points
  temppoints=np.array([])
  
  i=1
  n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(growth)-1),1)
  # while(len(temppoints)!=len(newpoints)):
  while(i<=n):
    temppoints=newpoints
    tempDensity = np.minimum(minDensity*np.power(growth,i),maxDensity)
    newpoints=_dsimplify_Point(temppoints,minDensity=minDensity,maxDensity=tempDensity,growth=growth,*args,**kwargs)
    i=i+1
    
  return newpoints 

def _dsimplify_Point(points,minDensity=1.0, maxDensity=10.0, growth=1.2,balanced_tree=True):
  """
  The algorithm to simplify/remove points by respecting minimum density field.
  See dsimplify_Point for more information
  
  """  
  nvalue=1000
  
  xy = points[:, [0, 1]]
  density = points[:, 2]
  npoints = xy.shape[0]
  
  kdtree = spatial.cKDTree(xy,balanced_tree=balanced_tree)
  
  n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(growth)-1),1)
  maxDistance = (minDensity*np.power(growth,n+1)-minDensity)/(growth-1)
  
  keepindices=np.zeros(npoints,dtype=np.int)
  for x in range(0,npoints,nvalue):
    xn = np.minimum(npoints,x+nvalue)
    array = np.arange(x,xn)
    subpoints = xy[array]
    
    l = kdtree.query_ball_point(subpoints,maxDistance)
    l=_ll2numpy(l) 
    
    distances = np.linalg.norm(xy[l] - subpoints[:,None], axis=2)
    nn=np.log(distances*(growth-1)/density[l]+1)/np.log(growth)
    dd = density[l]*np.power(growth, nn)
    
    ii=np.argmin(dd,axis=1)
    iii=np.squeeze(np.take_along_axis(l,ii[:,None],axis=1))
    
    keepindices[x:xn]=iii
    
  
  uniques=np.unique(keepindices)
  return points[uniques]


def cArea(d):
  """
  Area of circle
  
  Parameters
  ----------
  d:float
    diameter
  """
  return np.pi*np.power(d*0.5,2.)
    
def dsimplify_Polygon(polygon,points,minDensity=1,maxDensity=10,growth=1.2,cB=0.01,sD=1000.0):
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
  sD:float
    Simplication distance
  
  Notes
  -----
  Correction buffers are used to correc geometric issues.
  
  TODO: points should be replace by features to include points,lines and polygons
    
  """
  steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4,4E4,7E4,1E5,2E5,4E5,7E5],dtype=np.float32)
  # steps = np.array([10,20,40,70,100,200,400,700,1000,2000],dtype=np.float32)
  if(sD>maxDensity):raise Exception("sD needs to be higher than maxDensity")
  
  points = dsimplify_Point(points,minDensity=1,maxDensity=10,growth=1.2)
  
  xy = points[:, [0, 1]]
  density = points[:, 2]
  udensity = np.unique(density)
  
  n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(growth)-1),1)
  maxDistance = (minDensity*np.power(growth,n+1)-minDensity)/(growth-1)
  polygon =polygon.correct(cB) 
  opolygon=polygon
  
  def getZones(tpolygon,d):
    ozones=[]
    zones=[]
    for unique in udensity:
      mps=MultiPoint(xy[density==unique]).buffer(d)
      _n=np.floor(np.log(d*(growth-1)/unique+1)/np.log(growth))
      _d = np.maximum(minDensity,unique*np.power(growth,_n))

      ozone=tpolygon.intersection(mps).correct(cB)
      zone=ozone.buffer(-_d*0.1).buffer(_d*0.1).correct(cB).removeHoles(cArea(_d*0.1)).simplify(_d*0.01).correct(cB)
      ozones.append(ozone)
      zones.append(zone)
      
    ozones=cascaded_union(ozones).correct(cB)  
    zones=cascaded_union(zones).correct(cB)  
    return ozones,zones
  
  
  def process(domain,newdomain,prev,d,outline=None):
    if outline is None:
      ozones,zones = getZones(domain,d)
    else:
      zones=outline.buffer(-maxDensity*0.1).buffer(maxDensity*0.1).correct(cB).removeHoles(cArea(maxDensity*0.1)).simplify(maxDensity*0.01).correct(cB)
      
    
    if newdomain is None:
      newdomain=zones
      prev=ozones
    else:
      zones=zones.difference(prev).correct(cB)
      newdomain=newdomain.union(zones).correct(cB)
    return newdomain,prev
  
  
  steps=steps[steps>=minDensity]
  steps=steps[steps<maxDistance]
  ndomain=None
  prev=None
  _dd=None
  t=tqdm(total=len(steps), unit_scale=True)
  for i,d in enumerate(steps):
    if(i%8==0):
      _nn=np.floor(np.log(d*(growth-1)/minDensity+1)/np.log(growth))
      _dd = np.maximum(minDensity,minDensity*np.power(growth,_nn))
      opolygon=opolygon.simplify(_dd*0.1,False).correct(cB)
    ndomain,prev=process(opolygon,ndomain,prev,d)
    ndomain.plot()
    t.update(1)
  t.close()
  
  
  ndomain,prev=process(opolygon.simplify(_dd*0.1).correct(cB),ndomain,prev,maxDistance,polygon.simplify(_dd*0.1).correct(cB))
  
  ndomain.savePlot("../domain.png")
  
  
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
  
  maxValue=np.max(targets)
  targets[np.invert(indices)]=maxValue
  targets[targets==0]=maxValue
  
  
  m=np.min(targets,axis=1)
  
  return m

def inearest_Polygon(polygon,maxDistance=1.0,nvalue=100,angle=90.0):
  """
  Computes nearest interior nodes
  
  Parameters
  ----------
  
  polygon:Polygon
    2D array, shape(npoints,2)
  maxDistance:float
  rDistance:float
    Resample distance
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
  