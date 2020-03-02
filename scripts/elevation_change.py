#!/usr/bin/python3

"""
Task 3: determine the elevation and total volume change between two DEMs

Author: Gabija Pasiunaite
"""

import os
import numpy as np
import argparse
from handleTiff import tiffHandle

os.system("pip install pygeotools")
from pygeotools.lib import iolib, warplib, geolib, timelib, malib


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Create an elevation change map for two DEMs.")
    # Add arguments
    parser.add_argument('--before', dest='before', type=str, default='2009', help="DEM to use as 'before' raster")
    parser.add_argument('--after', dest='after', type=str, default='2015', help="DEM to use as 'after' raster")
    # Parse arguments
    args = parser.parse_args()
    return args


class Change_Detection:

    def __init__(self, before, after):
        """
        Class constructor.
        """
        self.tiff_handler = tiffHandle()
        self.dem1_dir = '../outputs/' + before + '/' + before + '.tif'
        self.dem2_dir = '../outputs/' + after + '/' + after + '.tif'
        self.dem1, self.trs1 = self.tiff_handler.readTiff(filename=self.dem1_dir)
        self.dem2, self.trs2 = self.tiff_handler.readTiff(filename=self.dem2_dir)
        self.glacier_shp = '../outputs/pine_island_glacier/glims_polygons.shp'
        # TRS: 0- x corner coord, 1 - res in x, 2- ... , 3- y corner coord, 4- ..., 5 - res in y
        print(self.trs1, self.trs2)

    def getcoords(self):

        xlen, ylen = len(self.elev), len(self.elev[1, :])  # Get the length fot

        self.lats, self.longs = np.empty((xlen, ylen)), np.empty((xlen, ylen))
        # Make empty array of the same size as the elevation data

        # Loop to iterate through both arrays and append coordinates to later reuse the writetiff
        for i in range(xlen):
            for j in range(ylen):
                self.longs[i, j] = self.tds[1] * j + self.tds[2] * i + self.tds[0]
                self.lats[i, j] = self.tds[4] * j + self.tds[5] * i + self.tds[3]

    def elevation_change(self):
        """
        Function produces an elevation change map.
        Script is heavily based on Geohackweek's tutorial on processing Mt Rainier Glacier data:
        https://geohackweek.github.io/raster/05-pygeotools_rainier/
        """
        # function to map the overlap between the two files in accordance to the 2015 tif file
        dem_2009, dem_2015 = warplib.memwarp_multi_fn([self.dem1_dir, self.dem2_dir], extent='intersection', res='min', t_srs=self.dem2_dir)

        # Get the list of geo transform parametres from the gdal objects.
        t_ds2015 = dem_2015.GetGeoTransform()

        # Get a 2D numpy masked array from the output of the previous function
        dem2009 = iolib.ds_getma(dem_2009)
        dem2015 = iolib.ds_getma(dem_2015)

        # Get the difference of elevation between the two DEMs
        diff = dem2015 - dem2009
        # Write the geotiff
        iolib.writeGTiff(diff, '../outputs/elevation_change.tif', dem_2009)

        # Mask areas that do not belong to the glacier
        # Create binary mask from polygon shapefile to match our warped raster datasets
        glacier_mask = geolib.shp2array(self.glacier_shp, dem_2009)
        # Now apply the mask to each array
        masked_diff = np.ma.array(diff, mask=glacier_mask)
        iolib.writeGTiff(masked_diff, '../outputs/glacier_elevation_change.tif', dem_2009)
        return

    def volume_change(self):
        """
        Function calculates the volume change between the two DEMs.
        """

        px_area = self.tds[1] ** 2  # Calculate the area associated with each pixels
        glacier = self.elev[self.elev != -999]  # Remove the missing data
        count = len(glacier)  # Counts the amount of pixels of data in the geotiff file
        totalarea = (px_area * count) / 1E6  # Calculate the area

        print('The change of elevation was between {}m and {}m.'
              ' With an average of {}m'.format(min(glacier), max(glacier), np.mean(glacier)))

        volchange = totalarea * (np.mean(glacier) / 1E3)

        print('The total Volume change is about ' + str(volchange) + ' km^3')


if __name__ == "__main__":
    cmd_args = getCmdArgs()
    change = Change_Detection(before=cmd_args.before, after=cmd_args.after)
    change.elevation_change()
