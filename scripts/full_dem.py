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
from handleTiff import tiffHandle
from data_store import dataStore


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Create a DEM from a specified file of any chosen resolution.")
    # Add arguments
    parser.add_argument('--y', dest='year', type=int, default=2009, help='Year of the data collection: 2009 or 2015')
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

    # Instantiate an empty data store

    data_store = dataStore()

    # Get a list of hd5 files in the LVIS file directory
    dir = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/' + str(args.year) + '/'
    files = [f for f in os.listdir(dir) if f.endswith('.h5')]

    for file in files:
        print('Processing file: ', file)
        # Read in LVIS data within the area of interest
        #lvis = lvisGround(dir + file, minX=256.0, minY=-75.7, maxX=263.0, maxY=-74.0, setElev=True)
        lvis = lvisGround(dir + file, setElev=True)

        # If there is data in the ROI, then process it.
        if lvis.data_present:
            # find the ground and reproject
            lvis.estimateGround()
            lvis.reproject(4326, 3031)
            # append flightine data to the datastore
            lons, lats, zGs = lvis.get_results()
            data_store.append_data(lons, lats, zGs)

            # ---- RAM -----
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print('memory use:', memoryUse)

    # save the processed data to file
    data_store.save_data(str(args.year))

    stop = timeit.default_timer()
    print('Processing time: ' + str((stop - start) / 60.0) + ' min')


        # Create a tiff and plot the resulting DEM
    #tiff_handle = tiffHandle(lvis)
    #tiff_handle.writeTiff()
    #tiff_handle.plot_dem()


    # Managing memory:
    """
    Pandas + chunks: https://towardsdatascience.com/why-and-how-to-use-pandas-with-large-data-9594dda2ea4c
    Pandas + dask: https://towardsdatascience.com/how-to-handle-large-datasets-in-python-with-pandas-and-dask-34f43a897d55
    """