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
import numpy as np
import gc
from copy import deepcopy
from lxml import etree



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


def merge_tiles(year):
    # Change directory into the outputs file dir
    os.chdir(r"../outputs/" + str(year))
    print("Merging files from " + str(year))

    # Build a GDAL virtual image from all the rasters
    build_vrt_cmd = "gdalbuildvrt -srcnodata -999.0 -overwrite " + str(year) + "_avg.vrt ./*_dem.tif"
    os.system(build_vrt_cmd)

    # Add a pixel function to the VRT to average overlapping pixels.
    # Modified from: https://gis.stackexchange.com/questions/350233/how-can-i-modify-a-vrtrasterband-sub-class-etc-from-python
    vrt_tree = etree.parse(str(year) + "_avg.vrt")
    vrt_root = vrt_tree.getroot()
    vrtband1 = vrt_root.findall(".//VRTRasterBand[@band='1']")[0]

    #vrtband1.set("subClass", "VRTDerivedRasterBand")
    pixelFunctionType = etree.Element('PixelFunctionType')
    pixelFunctionType.text = "average"
    vrtband1.insert(0, pixelFunctionType)
    pixelFunctionLanguage = etree.Element('PixelFunctionLanguage')
    pixelFunctionLanguage.text = "Python"
    vrtband1.insert(1, pixelFunctionLanguage)
    pixelFunctionCode = etree.Element('PixelFunctionCode')
    pixelFunctionCode.text = etree.CDATA("""
    import numpy as np

    def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
        x = np.ma.masked_equal(in_ar, -999)
        np.mean(x, axis = 0, out = out_ar, dtype = 'Float32')
        mask = np.all(x.mask, axis = 0)
        out_ar[mask]=-999
    """)
    vrtband1.insert(2, pixelFunctionCode)
    vrt_tree.write(str(year) + "_avg.vrt")

    # Merge all the rasters, where pixels overlap - average them
    merge_cmd = "gdal_translate --config GDAL_VRT_ENABLE_PYTHON YES -a_nodata -999.0 " + \
                str(year) + "_avg.vrt " + str(year) + "_merged.tif"
    os.system(merge_cmd)

    # ---------- GAP FILLING ---------
    # Fill gaps using
    gap_fill_cmd = "gdal_fillnodata.py -md 100000 -nomask -si 5 " + str(year) + "_merged.tif " + str(year) + "_filled.tif"
    os.system(gap_fill_cmd)

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

    """
    for file in files:
        gc.collect()
        print('Processing file: ', file)
        # Read in LVIS data within the area of interest
        lvis = lvisGround(dir + file, minX=256.0, minY=-75.7, maxX=263.0, maxY=-74.0, setElev=True)

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
            # dem.plot_dem(filename=full_fn)

            # ---- RAM -----
            pid = os.getpid()
            py = psutil.Process(pid)
            memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB
            print('memory use:', str(memoryUse)[0:5], 'GB')
    """

    merge_tiles(year=args.year)

    """ TO DO:
    - also include extra 2015 data
    - separate gap filling
    """

    stop = timeit.default_timer()
    print('Processing time: ' + str((stop - start) / 60.0) + ' min')
