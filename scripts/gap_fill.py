#!/usr/bin/python3

"""
Task 1: create a DEM from a single LVIS flight line.

The script also has a cmd parser to change the resolution, flighline file and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

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

