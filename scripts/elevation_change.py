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
        dem1_dir = '../outputs/' + before + '/' + before + '.tif'
        dem2_dir = '../outputs/' + after + '/' + after + '.tif'

        # From here onwards we are only working with overlapping arrays
        self.dem1, self.dem2 = warplib.memwarp_multi_fn([dem1_dir, dem2_dir], extent='intersection', res='min', t_srs=dem2_dir)
        self.glacier_shp = '../outputs/pine_island_glacier/glims_polygons.shp'
        self.diff = []


    def elevation_change(self):
        """
        Function produces an elevation change map.
        Script is heavily based on Geohackweek's tutorial on processing Mt Rainier Glacier data:
        https://geohackweek.github.io/raster/05-pygeotools_rainier/
        """

        # Get a 2D numpy masked array from the output of the previous function
        dem2009 = iolib.ds_getma(self.dem1)
        dem2015 = iolib.ds_getma(self.dem2)

        # Get the difference of elevation between the two DEMs
        self.diff = dem2015 - dem2009

        # Write the geotiff
        iolib.writeGTiff(self.diff, '../outputs/elevation_change.tif', self.dem1)

        # Mask areas that do not belong to the glacier
        # Create binary mask from polygon shapefile to match our warped raster datasets
        glacier_mask = geolib.shp2array(self.glacier_shp, self.dem2)

        # Now apply the mask to ethe difference array
        self.diff = np.ma.array(self.diff, mask=glacier_mask)
        iolib.writeGTiff(self.diff, '../outputs/glacier_elevation_change.tif', self.dem1)
        return

    def volume_change(self):
        """
        Function calculates various glacier volume and area change metrics.
        Again, this function is heavily based on the following tutorial:
        https://geohackweek.github.io/raster/05-pygeotools_rainier/
        """
        time_diff = 2015 - 2009
        # Calculate annual rate of change
        annual_rate = np.ma.array(self.diff) / np.array(time_diff)

        # Extract x and y pixel resolution (m) from geotransform
        gt = self.dem1.GetGeoTransform()
        px_res = (gt[1], -gt[5])
        # Calculate pixel area in m^2
        px_area = px_res[0] * px_res[0]

        # Multiple pixel area by the observed elevation change for all valid pixels over glaciers
        dhdt_mean = annual_rate.mean()
        # Compute area in km^2
        area_total = px_area * annual_rate.count() / 1E6
        # Volume change rate in km^3/yr
        vol_rate = dhdt_mean * area_total / 1E3
        # Volume change in km^3
        vol_total = vol_rate * time_diff
        # Assume intermediate density between ice and snow for volume change (Gt)
        rho = 0.850
        mass_rate = vol_rate * rho
        mass_total = vol_total * rho

        # Print some numbers (clean this up)
        print('%0.2f m/yr mean elevation change rate' % dhdt_mean)
        print('%0.2f km^2 total area' % area_total)
        print('%0.2f km^3/yr mean volume change rate' % vol_rate)
        print('%0.2f km^3 total volume change' % vol_total)
        print('%0.2f Gt/yr mean mass change rate' % mass_rate)
        print('%0.2f Gt total mass change\n' % mass_total)


if __name__ == "__main__":
    cmd_args = getCmdArgs()
    change = Change_Detection(before=cmd_args.before, after=cmd_args.after)
    change.elevation_change()
    change.volume_change()
