#!/usr/bin/python3

"""
Task 2: create a gap-filled DEM from all the 2015 data

The script also has a cmd parser to change the resolution, flight year and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

import os
import psutil
import argparse
import timeit
from sys import path
from os import getenv
from lvis_ground import lvisGround
from dem import lvis_to_DEM, DEM_merge
import numpy as np
from scipy.signal import fftconvolve
import gc
from lxml import etree
from osgeo import gdal
from astropy.convolution import convolve_fft


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Create a DEM from a specified file of any chosen resolution.")
    # Add arguments
    parser.add_argument('--y', dest='year', type=int, default=2015, help='Year of the data collection: 2009 or 2015')
    parser.add_argument('--res', dest='resolution', type=int, default=1000.0, help="DEM resolution")
    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # Time the run
    start = timeit.default_timer()

    # Get command line arguments
    args = getCmdArgs()

    # Get a list of hd5 files in the LVIS file directory
    dir = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '/'
    dir2 = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '_additional/'
    files = [dir + f for f in os.listdir(dir) if f.endswith('.h5')]

    # Append additional files for 2015
    if args.year == 2015:
        files = files + [dir2 + f for f in os.listdir(dir2) if f.endswith('.h5')]


    for file in files:
        gc.collect()
        print('Processing file: ', file)
        # Read in LVIS data within the area of interest
        dem = lvis_to_DEM(file, minX=256.0, minY=-75.7, maxX=263.0, maxY=-74.0, setElev=True, res=args.resolution)

        # If there is data in the ROI, then process it.
        if dem.data_present:
            full_fn = '/' + str(args.year) + '/' + file[-9:-3] + '_dem.tif'
            # find the ground and reproject
            dem.estimateGround()
            dem.reproject(4326, 3031)

            dem.points_to_raster()
            dem.gapfill()
            dem.write_tiff(filename=full_fn)
            # dem.plot_dem(filename=full_fn)

            # ---- RAM -----
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print('memory use:', str(memoryUse)[0:5], 'GB')


    smooth_dem = DEM_merge(args.year)
    smooth_dem.merge_tiles()
    smooth_dem.gaussian_blur()

    stop = timeit.default_timer()
    print('Processing time: ' + str((stop - start) / 60.0) + ' min')
