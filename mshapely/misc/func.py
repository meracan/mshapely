from functools import wraps
import numpy as np

def add_method(cls):
  def decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
      return func(self, *args, **kwargs)
    
    if isinstance(cls, list):
      for _cls in cls:
        setattr(_cls, func.__name__, wrapper)
    else:  
      setattr(cls, func.__name__, wrapper)
    # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
    return func  # returning func means func can still be used normally
  
  return decorator

def add_attribute(cls):
  def decorator(func):
    def wrapper(self, *args, **kwargs):
      return func(self, *args, **kwargs)
    if isinstance(cls, list):
      for _cls in cls:
        setattr(_cls, func.__name__, property(wrapper))
    else:
      setattr(cls, func.__name__, property(wrapper))
    return func  # returning func means func can still be used normally
  
  return decorator
  
def _add_monkey_attribute(self,name,func):
  def deco():
    _name = "_" + name
    if getattr(self,_name) is None:
      setattr(self,_name, self._get(name,func))
    return getattr(self,_name)    
  return deco


def ll2numpy(l):
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
  
  empty=np.array(list(map(len, l)))
  empty= (empty==0)
  
  a=np.array([xi+[len(xi)>0 and xi[0] or 0]*(length-len(xi)) for xi in l])
  
  return a,empty
  