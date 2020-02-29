#!/usr/bin/python3

"""
Task 1: create a DEM from a single LVIS flight line.

The script also has a cmd parser to change the resolution, flighline file and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

from __future__ import division
import numpy as np
from lvis_ground import lvisGround
from handleTiff import tiffHandle
import numpy as np
from osgeo import gdal
from osgeo import osr
import rasterio
from rasterio.fill import fillnodata
from matplotlib import pyplot as plt
import glob
import os
from scipy.interpolate import griddata



import numpy as np
import matplotlib.pyplot as plt

def iwd(x,y,v,grid,power):
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            distance = np.sqrt((x-i)**2 + (y-j)**2)
            if (distance**power).min()==0:
                grid[i,j] = v[(distance**power).argmin()]
            else:
                total = np.sum(1/(distance**power))
                grid[i,j] = np.sum(v/(distance**power)/total)
    return grid

np.random.seed(123433789) # GIVING A SEED NUMBER FOR THE EXPERIENCE TO BE REPRODUCIBLE
grid = np.zeros((100,100),dtype='float32') # float32 gives us a lot precision
x,y = np.random.randint(0,100,10),np.random.randint(0,100,10) # CREATE POINT SET.
v = np.random.randint(0,10,10) # THIS IS MY VARIABLE

grid = iwd(x,y,v,grid,2)
plt.imshow(grid.T,origin='lower',interpolation='nearest',cmap='jet')
plt.scatter(x,y,c=v,cmap='jet',s=120)
plt.xlim(0,grid.shape[0])
plt.ylim(0,grid.shape[1])
plt.grid()
plt.show()