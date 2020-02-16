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
from dem import DEM


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Create a DEM from a specified file of any chosen resolution.")
    # Add arguments
    parser.add_argument('--y', dest='year', type=int, default=2015, help='Year of the data collection: 2009 or 2015')
    parser.add_argument('--res', dest='resolution', type=int, default=30.0, help="DEM resolution")
    # Parse arguments
    args = parser.parse_args()
    return args


def merge_tiles(year):
    # Change directory into the outputs file dir
    os.chdir(r"../outputs/" + str(year))
    # Get all the files in that dir that end with .tif
    files = [f for f in os.listdir('./') if f.endswith('.tif')]
    files_str = " ".join(files)
    print('Merging these files: ', files_str)

    # Merge all the tiles using GDAL merge command. Set no data value to -999.0
    merge_cmd = "gdal_merge.py -o 2015.tif -of gtiff -a_nodata -999.0 " + files_str
    os.system(merge_cmd)

    # Go back to the main working directory
    os.chdir(r"../../scripts")
    return


if __name__ == "__main__":
    # Time the run
    start = timeit.default_timer()

    # Get command line arguments
    args = getCmdArgs()

    # Get a list of hd5 files in the LVIS file directory
    dir = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '/'
    files = [f for f in os.listdir(dir) if f.endswith('.h5')]

    for file in files:
        print('Processing file: ', file)
        # Read in LVIS data within the area of interest
        lvis = lvisGround(dir + file, minX=255.0, minY=-77, maxX=264.0, maxY=-73.0, setElev=True)

        # If there is data in the ROI, then process it.
        if lvis.data_present:
            full_fn = '/' + str(args.year) + '/' + file[-9:-3] + '_dem.tif'
            # find the ground and reproject
            lvis.estimateGround()
            lvis.reproject(4326, 3031)

            dem = DEM(elevs=lvis.zG, lons=lvis.lon, lats=lvis.lat, res=args.resolution)
            dem.points_to_raster()
            dem.gapfill()
            dem.write_tiff(filename=full_fn)
            #dem.plot_dem(filename=full_fn)

            # ---- RAM -----
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print('memory use:', memoryUse[0:5], 'GB')

    merge_tiles(year=args.year)

    stop = timeit.default_timer()
    print('Processing time: ' + str((stop - start) / 60.0) + ' min')
