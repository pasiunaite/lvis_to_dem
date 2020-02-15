#!/usr/bin/python3

"""
Task 1: create a DEM from a single LVIS flight line.

The script also has a cmd parser to change the resolution, flighline file and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

import os
import psutil
import timeit
import argparse
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
    parser.add_argument('--fn', dest='filename', type=str, default='ILVIS1B_AQ2015_1017_R1605_056419.h5', help='Filename')
    parser.add_argument('--dem_fn', dest='dem_name', type=str, default='dem', help='DEM filename')
    parser.add_argument('--res', dest='resolution', type=int, default=30.0, help="DEM resolution")
    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # Time the run
    start = timeit.default_timer()

    # Get command line arguments
    args = getCmdArgs()
    file_dir = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '/' + args.filename

    # Read in LVIS data within the area of interest
    lvis = lvisGround(file_dir, minX=256.0, minY=-75.7, maxX=263.0, maxY=-74.0, setElev=True)

    # If there is data in the ROI, then process it.
    if lvis.data_present:
        # find the ground and reproject
        lvis.estimateGround()
        lvis.reproject(4326, 3031)

        lvis.save_to_file('test')

        # Plot data points
        #lvis.plot_data_points()

        # Create a tiff and plot the resulting DEM
        tiff_handle = tiffHandle(lvis)

        tiff_handle.writeTiff()
        tiff_handle.plot_dem()

