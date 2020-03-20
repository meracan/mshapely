import pytest
import numpy as np
from mshapely.linalg import norm,normalVector,translate,rotate,dot,cross
def test_linalg():
  #
  # norm
  #  
  np.testing.assert_array_equal(norm(np.array([[0,0]]),np.array([[1,0]])),np.array([[0,1,0]]))
  
  #
  # normalVector
  #  
  pts=np.array([[0,0],    [0,1],    [1,1],    [1,0],    [0,0],    ])
  np.testing.assert_almost_equal(normalVector(pts), np.array([
  [ 0.    ,      0.     ,     0.70710678,  0.70710678 , 0.,          0.        ],
 [ 0.   ,       1.     ,     0.70710678 ,-0.70710678 , 0.  ,        1.        ],
 [ 1.   ,       1.    ,     -0.70710678 ,-0.70710678,  1.   ,       1.        ],
 [ 1.    ,      0.   ,      -0.70710678 , 0.70710678 , 1.    ,      0.        ],
 [ 0.     ,     0.  ,        0.70710678 , 0.70710678,  0.     ,     0.        ],
  ]))
  
  #
  # translate
  #
  x= np.array([1,3])
  y= np.array([1,4])
  np.testing.assert_array_equal(translate(x,y), np.array([
  [
    [1,0,1],
    [0,1,1],
    [0,0,1],
  ],[
    [1,0,3],
    [0,1,4],
    [0,0,1],
  ]
  ]))
  
  #
  # rotate
  #
  t= np.array([np.pi*0.5,np.pi])
  np.testing.assert_almost_equal(rotate(t), np.array([
  [
    [0,-1,0],
    [1,0,0],
    [0,0,1],
  ],[
    [-1,0,0],
    [0,-1,0],
    [0,0,1],
  ]
  ]))
  
  #
  # dot
  #
  np.testing.assert_almost_equal(dot(np.array([[1,1]]),np.array([[1,1]])),np.array([2]))
  
  #
  # cross
  #
  np.testing.assert_almost_equal(cross(np.array([[1,0]]),np.array([[1,1]])),np.array([1]))
  

if __name__ == "__main__":
  test_linalg()
  