import numpy as np
from scipy import spatial

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
  def wrapper(d,g,a):
    if not isinstance(d,np.ndarray):d=np.array(d)
    if not isinstance(g,np.ndarray):g=np.array(g)
    if not isinstance(a,np.ndarray):a=np.array(a)
    if np.any(g<=1):raise Exception("Growth needs to be larger than 1.0")
    return function(d,g,a)
  return wrapper

class DF(object):
  
  def __init__(self,array,minDensity=None,maxDensity=None,minGrowth=None,return_index=False):
    if not isinstance(array,(np.array,list)):raise Exception("Needs array")
    if isinstance(array,list):array=np.array(array)
    if array.ndim !=2:raise Exception("Needs 2D array")
    
    self.minDensity = np.min(array[:,2]) if minDensity is None else minDensity
    self.maxDensity = np.max(array[:,2]) if maxDensity is None else maxDensity
    self.minGrowth = np.min(array[:,3]) if minGrowth is None else minGrowth
    self.balanced_tree=True
    self._x = self._simplify(array)

  def _simplify(self,points):
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
    
    Note
    ----
    The algorithm uses a stepping approach by gradually increasing the growth n value and gradually removing points.
    This avoids searching large quantities of unnecessary points.
    
    Example
    ------ 
    TODO
    """ 
    minDensity=self.minDensity
    maxDensity=self.maxDensity
    minGrowth = self.minGrowth
    balanced_tree = self.balanced_tree
    
    def _subsimplify(_points,_maxDensity):
      """
      The algorithm to simplify/remove points by respecting minimum density field.
      See dsimplify_Point for more information
      
      """  
      nvalue=1000
      
      xy = _points[:, [0, 1]]
      density = _points[:, 2]
      growth = _points[:, 3]
      npoints = xy.shape[0]
      
      kdtree = spatial.cKDTree(xy,balanced_tree=balanced_tree)
      
      maxDistance = DF.getl_D(minDensity,minGrowth,_maxDensity)
      
      keepindices=np.zeros(npoints,dtype=np.int)
      for x in range(0,npoints,nvalue):
        xn = np.minimum(npoints,x+nvalue)
        array = np.arange(x,xn)
        subpoints = xy[array]
        
        l = kdtree.query_ball_point(subpoints,maxDistance)
        l=_ll2numpy(l) 
        
        distances = np.linalg.norm(xy[l] - subpoints[:,None], axis=2)
        dd = DF.getD_l(density[l],growth[l],distances)
        
        ii=np.argmin(dd,axis=1)
        iii=np.squeeze(np.take_along_axis(l,ii[:,None],axis=1))
        
        keepindices[x:xn]=iii
        
      uniques=np.unique(keepindices)
      # TODO: return keeindices
      return _points[uniques]    
    
    newpoints=points
    temppoints=np.array([])
    
    i=1
    growths=points[:,3]
    mingrowth=np.min(growths)
    n = DF.getn_D(minDensity,mingrowth,maxDensity)
    while(i<=n):
      temppoints=newpoints
      tempDensity = np.minimum(DF.getD_n(minDensity,mingrowth,i),maxDensity)
      newpoints=_subsimplify(temppoints,tempDensity)
      i=i+1
      
    return newpoints 
  
  def plot(self):
    # Create mesh grid
    # plot contour
    # 
    
    None
    
  @staticmethod
  @check
  def getD_n(d,g,n):
    return d*np.power(g,n)
  
  @staticmethod
  @check
  def getn_D(d,g,D):
    a = D/d
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
    return np.log(l*(g-1)/d+1)/np.log(g)-1
    
  @staticmethod
  @check
  def getD_l(d,g,l):
    n = DF.getn_l(d,g,l)
    return DF.getD_n(d,g,n)
    