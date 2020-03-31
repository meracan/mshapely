
import pytest
import os
import numpy as np
import matplotlib.pyplot as plt


import mshapely
from mshapely.spatial import DF


def test_DF_static():
    # Get Density for different growth
    np.testing.assert_almost_equal(DF.getD_n(1,1.2,np.arange(10)),[1.       , 1.2      , 1.44     , 1.728    , 2.0736   , 2.48832  ,
      2.985984 , 3.5831808, 4.299817 , 5.1597804])
    
    # Get distance for different growth
    np.testing.assert_almost_equal(DF.getl_n(1,1.2,np.arange(10)),[ 1.       ,  2.2      ,  3.64     ,  5.368    ,  7.4416   ,
        9.92992  , 12.915904 , 16.4990848, 20.7989018, 25.9586821])
    
    # Get n based on minDensity, growth and density
    np.testing.assert_almost_equal(DF.getn_D(np.array([1]),1.2,5.1597804),[9])
    
    # Get n based on minDensity,growth and distance
    np.testing.assert_almost_equal(DF.getn_l(1,1.2,25.9586821),[9])
    
    np.testing.assert_almost_equal(DF.getn_l(np.array([1,2]),np.array([1.2,1.2]),np.array([25.9586821])),[9,6.0193865])

def test_ll2numpy():
  None

def test_plot():
  
  density=np.array([[0,0,1,1.2],[2.5,0,10,1.2],[5,0,1,1.05]])
  
  fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 5))
  fig.tight_layout()
  df=DF(density,minDensity=1,maxDensity=100,minGrowth=1.2)
  df.plot(extent=[-10,-10,10,10],axe=axes,fig=fig).plotSave("doc/img/density.1.png")
  
  None

def test_simplify():
  None

if __name__ == "__main__":
  test_DF_static()
  # test_ll2numpy()
  test_plot()
  # test_simplify()


