import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
from shapely.geometry import Point,GeometryCollection
from tqdm import tqdm
from ..io import GIS
from ..misc import ll2numpy

def check(function):
  """
  Decorator for static methods to check input
  """
  def wrapper(d,g,a,*args):
    if not isinstance(d,np.ndarray):d=np.array(d)
    if not isinstance(g,np.ndarray):g=np.array(g)
    if not isinstance(a,np.ndarray):a=np.array(a)
    if np.any(g<=1):raise Exception("Growth needs to be larger than 1.0")
    
    return function(d,g,a,*args)
  return wrapper

class DF(object):
  """
  Density Field Object.
  
  This object is used to resample (Multi)LineString and (Multi)Polygon based on a density field.
  
  Parameters
  ----------
  array: 2D ndarray
    shape: (npoint,4) : [[x,y,density,growth]] 
      x:x-coordinate
      y:y-coordinate
      density:density value
      growth:growth value
  minDensity: float,
    Default minDensity of the field. If None, it takes minimum value of array-density
  maxDensity: float,
    Default maxDensity of the field. If None, it takes maximum value of array-density
  minGrowth:float,
    Default growth of the field. If None,it will take minimum value of array-growth
  balanced_tree:bool
    balanced_tree is a kdtree parameter
  nvalue:int
    Number of points search in the kdtree. Higher memory is required for higher point number. 
  Attributes
  ----------
  dp: ndarray,
    shape:(npoints,6),[[x,y,density,growth,groupId,pointId]]
  """
  def __init__(self,array=None,balanced_tree=True,step=1,nvalue=1000,progress=False,**kwargs):
    self.minDensity=kwargs.pop('minDensity', None)
    self.maxDensity=kwargs.pop('maxDensity', None)
    self.minGrowth=kwargs.pop('minGrowth', None)
    self.maxDensitySimplify=kwargs.pop('maxDensitySimplify', self.maxDensity)
    self.dp=None
    self.balanced_tree=balanced_tree
    self.step=step
    self.nvalue =nvalue
    self.progress=progress
    if array is not None:
      self.add(array,**kwargs)
  
  def _checkInput(self,array):
    """
    """
    if not isinstance(array,(np.ndarray,list)):raise Exception("Needs 2D array")
    if isinstance(array,list):array=np.array(array)
    if array.ndim !=2:raise Exception("Needs 2D array")
    
    return array
    
  def add(self,array,minDensity=None,maxDensity=None,minGrowth=None,maxDensitySimplify=None):
    """
    Add points to the density field
    
    Parameters
    ----------
    array: 2D ndarray : [[x,y,density,growth]]
    
    Note
    ----------
    It creates groupId and pointId automatically
    The field parameter minDensity,maxDensity and minGrowth are only defined when DF is created.
    This will not change minDensity, maxDensity and minGrowth.
    """
    
    array=self._checkInput(array)
    
    if self.minDensity is None:
      self.minDensity= np.min(array[:,2]) if minDensity is None else minDensity
    if self.maxDensity is None:
      self.maxDensity= np.max(array[:,2]) if maxDensity is None else maxDensity
      self.maxDensitySimplify=self.maxDensity
    if self.minGrowth is None:
      self.minGrowth = np.min(array[:,3]) if minGrowth is None else minGrowth
    if maxDensitySimplify is not None:
      self.maxDensitySimplify=maxDensitySimplify
    
    minDensity=self.minDensity
    maxDensity=self.maxDensity
    
    array[array[:,2]<minDensity,2]=minDensity
    array[array[:,2]>maxDensity,2]=maxDensity
    
    groupId=len(np.unique(self.dp)) if self.dp is not None else 0
    npoint = len(array)
    array = np.column_stack((array,np.ones(npoint)*groupId,np.arange(npoint)))
    array=np.concatenate((self.dp,array)) if self.dp is not None else array
    
    self._simplify(array)
    return self
  
  def inearest(self,geo,minLength=False,**kwargs):
    """
    Compute density field based on interior nearest points
    
    Parameters
    ----------
    geo:Polygon
    minLength:float
    
    angle:
    
    
    """
    maxDistance = DF.getl_D(self.minDensity,self.minGrowth,self.maxDensity)
    distance=geo.inearest(maxDistance=maxDistance,**kwargs)
    
    distance[:,2]=DF.getD_l(self.minDensity,self.minGrowth,distance[:,2])
    if minLength:
      _density=geo.minSegment()[:,-3]
      distance[:,2]=np.minimum(distance[:,2],_density)
    newdensity=np.column_stack((distance,np.ones(len(distance))*self.minGrowth))
    self.add(newdensity)
    return self
    
  
  def _simplify(self,points):
    """
    Simplify/remove uninfluential density points
    
    Parameters
    ----------
    points:ndarray : [[x,y,density,growth]] 
    
    Note
    ----
    The algorithm uses a stepping approach by gradually increasing the growth n value and gradually removing points.
    This avoids searching large quantities of uninfluential points.
    """ 
    minDensity=self.minDensity
    minGrowth=self.minGrowth
    maxDensity=self.maxDensity
    balanced_tree = self.balanced_tree
    maxDensitySimplify=self.maxDensitySimplify
    
    newpoints=points
    
    # Remove duplicates to a meter
    v,i=np.unique(np.round(newpoints[:,:2],0),return_index=True,axis=0)
    newpoints=newpoints[i]
    print(minDensity,minGrowth,maxDensitySimplify)
    n = DF.getn_D(minDensity,minGrowth,maxDensitySimplify)
    
    if self.progress:t=tqdm(total=int(n),position=1)
    i=1
    while(i<=n):
      keepindices = self.getDensity(newpoints[:,:2],DF.getD_n(minDensity,minGrowth,i),newpoints,return_index=True)
      uniques=np.unique(keepindices)
      newpoints=newpoints[uniques]
      i=i+self.step
      if self.progress:t.update(self.step)
    if self.progress:t.close()
    self.dp=newpoints
    self.kdtree = spatial.cKDTree(newpoints[:,:2],balanced_tree=balanced_tree)
    return self 
  
  
  def getDensity(self,tp,maxDensity=None,dp=None,return_index=False):
    """
    Get field density
    
    Parameters
    ----------
    tp:2D ndarray : [[x,y]]
      Target points
    
    maxDensity:float
      Used during simplication. It limits the search instead of self.maxDensity
    dp:2D ndarray : [[x,y,density,growth,groupId,pointId]]
      Density points
      Used during simplication and replaces self.dp.
    return_index:
      Used during simplication. It returns the index instead of values.
    Note
    ----
      dd=Density for every (sub)target point and density points
    """
    minDensity = self.minDensity
    minGrowth  = self.minGrowth
    nvalue     = self.nvalue
    maxDensity = self.maxDensity if maxDensity is None else maxDensity
    kdtree     = self.kdtree if dp is None else spatial.cKDTree(dp[:,:2],balanced_tree=self.balanced_tree)
    dp         = self.dp if dp is None else dp
    
    maxDistance = DF.getl_D(minDensity,minGrowth,maxDensity)
    
    xy      = dp[:,:2]
    density = dp[:,2]
    growth  = dp[:,3]
    
    tp=self._checkInput(tp)
    
    ntp=len(tp)
    
    results=np.zeros(ntp)
    for x in range(0,ntp,nvalue):
      
      xn        = np.minimum(ntp,x+nvalue)
      array     = np.arange(x,xn)
      atp       = tp[array]
      l,e         = ll2numpy(kdtree.query_ball_point(atp,maxDistance))
      if l.shape[1]!=0:
        distances = np.linalg.norm(xy[l] - atp[:,None], axis=2)
        dd        = DF.getD_l(density[l],growth[l],distances)
        dd[e]     = maxDensity
  
        if return_index:
          ii=np.argmin(dd,axis=1)
          results[x:xn]=np.squeeze(np.take_along_axis(l,ii[:,None],axis=1)) # Taking index (from min density) from l 
        else:
          dd[dd>maxDensity]=maxDensity
          results[x:xn]=np.min(dd,axis=1)
      else:
        if return_index:raise Exception("Not coded for this condition")
        results[x:xn]=maxDensity
    
    if return_index:return results.astype(int)
    return results
  
  @staticmethod
  def read(path):
    collection = GIS.read(path)
    properties=collection.properties
    schema=collection.schema
    points=collection.geometry
    minDensity=schema.get('minDensity',None)
    maxDensity=schema.get('maxDensity',None)
    minGrowth=schema.get('minGrowth',None)
    
    density = list(map(lambda x:[x['density'],x['growth']],properties))
    xy=points.xy
    dp=np.column_stack((xy,density))
    
    return DF(dp,minDensity=minDensity,maxDensity=maxDensity,minGrowth=minGrowth)
  
  def write(self,path):
    dp = self.dp
    mp=GeometryCollection(list(map(Point,dp[:,:2])))
    schema={"minDensity":self.minDensity,"maxDensity":self.maxDensity,"minGrowth":self.minGrowth}
    mp.write(path,properties=map(lambda x:{"density":x[0],"growth":x[1]},dp[:,[2,3]]),schema=schema)
    return self
    
  @property
  def extent(self):
    """
    Extent of the density field using the density points self.dp
    """
    return [np.min(self.dp[:,0]),np.min(self.dp[:,1]),np.max(self.dp[:,0]),np.max(self.dp[:,1])]
    
  def plot(self,extent=None,nx=100,axe=None,fig=None,showDP=False):
    """
    Plot the densityField
    Parameters
    ----------
    extent:1D ndarray : [minx,miny,maxx,maxy]
      Extent array. If not specified, it will automatically compute the extent based on density points
    nx:float
      Resolution of the density field in the plot.
    axe:matplotlib axe
    fig:matplotlib fig
    showDP:bool
      Plot density points 
    """
    if extent is None:extent=self.extent
    xmin,ymin,xmax,ymax=extent
    xpad=(xmax-xmin)*0.05
    ypad=(ymax-ymin)*0.05
    
    x = np.linspace(xmin-xpad, xmax+xpad, nx)
    y = np.linspace(ymin-ypad, ymax+ypad, nx)
    xx, yy = np.meshgrid(x, y)
    pp = np.column_stack((xx.flatten(),yy.flatten()))
    
    z=self.getDensity(pp).reshape((len(x),len(y)))
    
    canvas = plt if axe is None else axe
    canvas.axis('equal')
  
    h = canvas.contourf(x,y,z)
    fig.colorbar(h, ax=canvas, shrink=0.9)
    
    if showDP:
      canvas.scatter(self.dp[:,0], self.dp[:,1], c="black",alpha=0.75,zorder=1)
    
    return self

  def savePlot(self,name='plot.png',axe=None):
    """
    Save plot to file
    """
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
  def getn_D(d,g,D,ss=0):
    a = np.array(D/d)
    a[a<1.0]=1.0 
    return np.log(a)/np.log(g)+ss
  
  @staticmethod
  @check
  def getl_n(d,g,n):
    return (d*np.power(g,n+1)-d)/(g-1)
  
  @staticmethod
  @check
  def getl_D(d,g,D,*args):
    n=DF.getn_D(d,g,D,*args)
    return DF.getl_n(d,g,n)
  
  @staticmethod
  @check
  def getn_l(d,g,l,ss=0):
    n=np.array(np.log(l*(g-1)/d+1)/np.log(g)+ss)
    n[n<0.]=0.
    return n
    
  @staticmethod
  @check
  def getD_l(d,g,l,*args):
    n = DF.getn_l(d,g,l,*args)
    return DF.getD_n(d,g,n)
    