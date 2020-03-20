from functools import wraps

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










