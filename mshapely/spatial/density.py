import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt

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


def check(function):
  """
  Decorator for static methods to check input
  """
  def wrapper(d,g,a):
    if not isinstance(d,np.ndarray):d=np.array(d)
    if not isinstance(g,np.ndarray):g=np.array(g)
    if not isinstance(a,np.ndarray):a=np.array(a)
    if np.any(g<=1):raise Exception("Growth needs to be larger than 1.0")
    
    return function(d,g,a)
  return wrapper

class DF(object):
  """
  Density Field Object. 
  Calculates the density based on density growth points.
  
  This object is used to resample (Multi)LineString and (Multi)Polygon based on a density field.
  
  Parameters
  ----------
  array: 2D ndarray
    shape: (npoint,4) : [[x,y,density,growth]] 
      x:x-coordinate
      y:y-coordinate
      density:density value
      growth:growth factor
  minDensity: float,
    Default minDensity of the field. If None, it takes minimum value of array-density
  maxDensity: float,
    Default maxDensity of the field. If None, it takes maximum value of array-density
  minGrowth:float,
    Default growth of the field. If None,it will take minimum value of array-growth
  
  """
  def __init__(self,array,minDensity=None,maxDensity=None,minGrowth=None,balanced_tree=True,nvalue=1000):
    if not isinstance(array,(np.ndarray,list)):raise Exception("Needs 2D array")
    if isinstance(array,list):array=np.array(array)
    if array.ndim !=2:raise Exception("Needs 2D array")
    
    self.minDensity = np.min(array[:,2]) if minDensity is None else minDensity
    self.maxDensity = np.max(array[:,2]) if maxDensity is None else maxDensity
    self.minGrowth = np.min(array[:,3]) if minGrowth is None else minGrowth
    self.balanced_tree=balanced_tree
    self.nvalue =nvalue
    
    npoint = len(array)
    array = np.column_stack((array,np.zeros(npoint),np.arange(npoint)))
    self._simplify(array)

  def add(self,array):
    """
    Add points to the density field
    
    Parameters
    ----------
    array: 2D ndarray : [[x,y,density,growth]] 
    
    """
    npoint = len(array)
    groupId=len(np.unique(self.dp))
    array = np.column_stack((array,np.ones(npoint)*groupId,np.arange(npoint)))
    array=np.concatenate((self.dp,array))
    self._simplify(array)
    return self
  
  def _simplify(self,points):
    """
    Simplify/remove points by respecting minimum density growth field.
    
    Parameters
    ----------
    points:ndarray : [[x,y,density,growth]] 
    
    Note
    ----
    The algorithm uses a stepping approach by gradually increasing the growth n value and gradually removing points.
    This avoids searching large quantities of unnecessary points.
    
    Output
    ------
    ndarray : [[x,y,density,growth,groupId,id]]
      groupId: Group id of the set of points.
      id: Point id of the group
    
    Example
    ------ 
    TODO
    """ 
    minDensity=self.minDensity
    minGrowth=self.minGrowth
    maxDensity=self.maxDensity
    balanced_tree = self.balanced_tree

    newpoints=points
    
    i=1
    growths=points[:,3]
    n = DF.getn_D(minDensity,minGrowth,maxDensity)
    while(i<=n):
      keepindices = self.getDensity(newpoints[:,:2],DF.getD_n(minDensity,minGrowth,i),newpoints,return_index=True)
      uniques=np.unique(keepindices)
      newpoints=newpoints[uniques]
      i=i+1
    
    self.dp=newpoints
    self.kdtree = spatial.cKDTree(newpoints[:,:2],balanced_tree=balanced_tree)
    return self 
  
  
  def getDensity(self,tp,maxDensity=None,dp=None,return_index=False):
    """
    Note
    ----
      tp=Target points,[[x,y]]
      dp=Density points,[[x,y,density,growth]]
      dd=Density for every (sub)target point and density points
    """
    minDensity=self.minDensity
    minGrowth=self.minGrowth
    nvalue=self.nvalue
    maxDensity=self.maxDensity if maxDensity is None else maxDensity
    kdtree=self.kdtree if dp is None else spatial.cKDTree(dp[:,:2],balanced_tree=self.balanced_tree)
    dp=self.dp if dp is None else dp
    
    maxDistance = DF.getl_D(minDensity,minGrowth,maxDensity)
    
    xy = dp[:,:2]
    density = dp[:,2]
    growth = dp[:,3]
    
    ntp=len(tp)
    results=np.zeros(ntp)
    for x in range(0,ntp,nvalue):
      xn = np.minimum(ntp,x+nvalue)
      array = np.arange(x,xn)
      atp = tp[array]
    
      l = kdtree.query_ball_point(atp,maxDistance)
      l=_ll2numpy(l) 
      distances = np.linalg.norm(xy[l] - atp[:,None], axis=2)
      dd = DF.getD_l(density[l],growth[l],distances)
      if return_index:
        ii=np.argmin(dd,axis=1)
        results[x:xn]=np.squeeze(np.take_along_axis(l,ii[:,None],axis=1))
      else:
        results[x:xn]=np.min(dd,axis=1)
    if return_index:return results.astype(int)
    return results
    
  @property
  def extent(self):
    return [np.min(self.dp[:,0]),np.min(self.dp[:,1]),np.max(self.dp[:,0]),np.max(self.dp[:,1])]
    
  def plot(self,extent=None,nx=100,axe=None,fig=None):
    
    if extent is None:extent=self.extent
    xmin,ymin,xmax,ymax=extent
    
    points = self.dp
    xy=points[:,:2]
    density=points[:,2]
    growth=points[:,3]
    kdtree = self.kdtree
    maxDistance = DF.getl_D(self.minDensity,self.minGrowth,self.maxDensity)
    
    
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, nx)
    xx, yy = np.meshgrid(x, y)
    pp = np.column_stack((xx.flatten(),yy.flatten()))
    
    l = kdtree.query_ball_point(pp,maxDistance)
    l=_ll2numpy(l) 
    distances = np.linalg.norm(xy[l] - pp[:,None], axis=2)
    dd = DF.getD_l(density[l],growth[l],distances)
    z=np.min(dd,axis=1)
    
    # print(z[z<1.0])
    
    z=z.reshape((len(x),len(y)))
    canvas = plt if axe is None else axe
    canvas.axis('equal')
  
    h = canvas.contourf(x,y,z)
    fig.colorbar(h, ax=canvas, shrink=0.9)
    return self

  def plotSave(self,name='plot.png',axe=None):
    plt.savefig(name)
    canvas = plt if axe is None else axe
    canvas.clf()    
    return self
    
    
  @staticmethod
  @check
  def getD_n(d,g,n):
    return d*np.power(g,n)
  
  @staticmethod
  @check
  def getn_D(d,g,D):
    a = np.array(D/d)
    a[a<1.0]=1.0 
    return np.log(a)/np.log(g)
  
  @staticmethod
  @check
  def getl_n(d,g,n):
    return (d*np.power(g,n+1)-d)/(g-1)
  
  @staticmethod
  @check
  def getl_D(d,g,D):
    n=DF.getn_D(d,g,D)
    return DF.getl_n(d,g,n)
  
  @staticmethod
  @check
  def getn_l(d,g,l):
    n=np.array(np.log(l*(g-1)/d+1)/np.log(g)-1)
    n[n<0.]=0.
    return n
    
  @staticmethod
  @check
  def getD_l(d,g,l):
    n = DF.getn_l(d,g,l)
    return DF.getD_n(d,g,n)
    