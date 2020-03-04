#!/usr/bin/python3

"""
Task 2: create gap-filled DEMs from all the 2009 and 2015 data.

The script also has a cmd parser to change the resolution, flight year and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

import os
import gc
import psutil
import argparse
import timeit
from dem import lvis_to_DEM, DEM_merge


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    parser = argparse.ArgumentParser(description="Create a DEM from a specified file of any chosen resolution.")
    parser.add_argument('--y', dest='year', type=int, default=2015, help='Year of the data collection: 2009 or 2015')
    parser.add_argument('--res', dest='resolution', type=int, default=100.0, help="DEM resolution")
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

    # Check if output dir exists, if not then create it
    dirCheckList = ['../outputs', '../outputs/2009', '../outputs/2015']
    for directory in dirCheckList:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    # Process all the LVIS files and write a DEM of a single flight line into the output dir
    for file in files:
        gc.collect()
        print('Processing file: ', file)
        # Read in LVIS data within the area of interest
        dem = lvis_to_DEM(file, minX=253.0, minY=-75.8, maxX=282.3, maxY=-74.7, setElev=True, res=args.resolution)

        # If there is data in the ROI, then process it.
        if dem.data_present:
            full_fn = '/' + str(args.year) + '/' + file[-9:-3] + '_dem.tif'
            # find the ground and reproject
            dem.estimateGround()
            dem.reproject(4326, 3031)

            dem.points_to_raster()
            dem.gapfill()
            dem.write_tiff(filename=full_fn)

            # Check RAM usage as files are being processed
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print('memory use:', str(memoryUse)[0:5], 'GB')


    # Merge all the processed flightlines from that year into a single tif and fill the gaps
    smooth_dem = DEM_merge(args.year, args.resolution)
    smooth_dem.merge_tiles()

    # Apply Gaussian smoothing to get rid of the artefacts
    smooth_dem.gaussian_blur()
    smooth_dem.plot_dem(str(args.year) + '.tif')

    stop = timeit.default_timer()
    print('Processing time: ' + str((stop - start) / 60.0) + ' min')
