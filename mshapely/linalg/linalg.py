import numpy as np


def norm(p2, p1):
  """
  Compute normal vector based on two points
  
  Parameters
  ----------
  p2,p1: ndarray(2D)
  
  Output
  ------ 
  ndarray(2D)
  
  Example
  ------ 
  TODO
  
  """
  np.seterr(divide='ignore', invalid='ignore')
  norm = np.array([0, 0, 1])
  v1 = p2 - p1
  v1Length = np.linalg.norm(v1, axis=1)
  V1 = v1 / v1Length[:, np.newaxis]
  V2 = np.cross(V1, norm)
  return V2
  
def normalVector(points, onPoint=True):
  """
  Compute normal vector from series of points - linestring
  
  Parameters
  ----------
  points : ndarray(2D)
  onPoint: Computer normal vector on point instead of half the segment ahead
  
  Output
  ------ 
  ndarray(4D), [xo,yo,xn,yn,x,y]
  
  Note
  ----
  xo=x and yo=y if onPoint is True. 
    If not, it's equal to half distance between the two points
  xn,yn=normal vector point
  
  
  Example
  ------- 
  TODO: Might not work with open linestring
  
  """
  
  
  n = len(points)
  isClosed = np.array_equal(points[0], points[n - 1])
  if isClosed:points=points[:n-1]
  n=len(points)
  p1 = points
  
  newpoints = np.column_stack((np.zeros((n, 4)),points))
  p2 = np.roll(p1, -1, axis=0)
  
  if onPoint:
    p0=p1
    p1 = np.roll(p1, 1, axis=0)
    V1 = norm(p2, p1)[:,:-1]
  else:
    p1 = (p1 + p2) * 0.5
    p0=p1
    V1 = norm(p2, p1)[:,:-1]
  
  newpoints[:, 0] = p0[:, 0]
  newpoints[:, 1] = p0[:, 1]
  newpoints[:, 2] = V1[:, 0]
  newpoints[:, 3] = V1[:, 1]
  
  # Check if last and first are the same
  if isClosed:
    newpoints=np.append(newpoints,newpoints[0][None,:],axis=0)
    
  return newpoints
  
def translate(x, y):
  """
  Translate matrix for 2D points
  
  Parameters
  ----------
  x,y: np.float32
  
  Output
  ------ 
  ndarray(3D)
  
  Example
  ------ 
  TODO
  
  """    
  mat3 = np.zeros((3, 3))
  m = np.repeat(mat3[np.newaxis, :, :], len(x), axis=0)
  m[:, 0, 0] = 1.0
  m[:, 1, 1] = 1.0
  m[:, 2, 2] = 1.0
  m[:, 0, 2] = x
  m[:, 1, 2] = y
  return m


def rotate(theta):
  """
  Rotate matrix for 2D points
  
  Parameters
  ----------
  theta: rad
  
  Output
  ------ 
  ndarray(3D)
  
  Example
  ------ 
  TODO
  
  """    
  c = np.cos(theta)
  s = np.sin(theta)
  mat3 = np.zeros((3, 3))
  
  m = np.repeat(mat3[np.newaxis, :, :], len(theta), axis=0)
  m[:, 0, 0] = c
  m[:, 0, 1] = -s
  m[:, 1, 0] = s
  m[:, 1, 1] = c
  m[:, 2, 2] = 1.0
  return m

def dot(A,B):
  return A[...,0]*B[...,0]+A[...,1]*B[...,1]

def cross(A,B):
  return A[...,0]*B[...,1]-A[...,1]*B[...,0]