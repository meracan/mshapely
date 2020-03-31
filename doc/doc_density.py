
import os
import numpy as np

import matplotlib.pyplot as plt
from mshapely import DF


def doc_density():
  density=np.array([[0,0,1,1.2],[2.5,0,10,1.2],[5,0,1,1.05]])
  df=DF(density,minDensity=1,maxDensity=100,minGrowth=1.2)
  
  fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 5))
  fig.tight_layout()
  
  df.plot(extent=[-10,-10,10,10],axe=axes[0][0],fig=fig,showDP=True)
  df.add([[-5,-5,1,1.2]]).plot(extent=[-10,-10,10,10],axe=axes[0][1],fig=fig,showDP=True)
  df.add([[-5,5,5,1.2]]).plot(extent=[-10,-10,10,10],axe=axes[1][0],fig=fig,showDP=True)
  df.add([[5,5,1,1.2]]).plot(extent=[-10,-10,10,10],axe=axes[1][1],fig=fig,showDP=True)
  df.plotSave("doc/img/density.1.png")
    
  
if __name__ == "__main__":
  doc_density()