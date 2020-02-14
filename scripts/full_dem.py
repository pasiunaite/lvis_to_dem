#!/usr/bin/python3

"""
Task 2: create a gap-filled DEM from all the 2015 data

The script also has a cmd parser to change the resolution, flight year and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

import os
import argparse
from sys import path
from os import getenv
from lvis_ground import lvisGround
from handleTiff import tiffHandle


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Create a DEM from a specified file of any chosen resolution.")
    # Add arguments
    parser.add_argument('--y', dest='year', type=int, default=2015, help='Year of the data collection: 2009 or 2015')
    parser.add_argument('--dem_fn', dest='dem_name', type=str, default='dem', help='DEM filename')
    parser.add_argument('--res', dest='resolution', type=int, default=30.0, help="DEM resolution")
    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # Get command line arguments
    args = getCmdArgs()

    # Get a list of hd5 files in the LVIS file directory
    dir = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '/'
    files = [f for f in os.listdir(dir) if f.endswith('.h5')]

    for file in files:
        print(file)

    # read first file to set up arrays
    #filename = direc + fileList[0]

    ## ------- mm

    # Read in LVIS data within the area of interest
    lvis = lvisGround(file_dir, minX=256.0, minY=-75.7, maxX=263.0, maxY=-74.0, setElev=True)

    # If there is data in the ROI, then process it.
    if lvis.data_present:
        # find the ground and reproject
        lvis.estimateGround()
        lvis.reproject(4326, 3031)

        # Plot data points
        #lvis.plot_data_points()

        # Create a tiff and plot the resulting DEM
        tiff_handle = tiffHandle(lvis)
        tiff_handle.writeTiff2()
        tiff_handle.plot_dem()
