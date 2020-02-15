#!/usr/bin/python3

"""
A class to store point data from all the flightlines.
Author: Steven Hancock.
"""

# import necessary packages
import os
import psutil
from pyproj import Proj, transform  # package for reprojecting data
from osgeo import gdal             # pacage for handling geotiff data
from osgeo import osr              # pacage for handling projection information
from gdal import Warp
import numpy as np
import rasterio
from matplotlib import pyplot as plt


class dataStore:
    """
    Class to store and manipulate denoised data.
    """

    def __init__(self):
        """
        Initializes empty lat, long and elevation arrays to store values.
        """
        self.lon = np.empty((0, 1), dtype='float64')
        self.lat = np.empty((0, 1), dtype='float64')
        self.elev = np.empty((0, 1), dtype='float64')

    def append_data(self, lons, lats, zG):
        """
        Append processed points from a single flightline to the data store.
        :param lons: longitudes
        :param lats: latitudes
        :param cog:  center of mass
        """
        self.lon = np.append(self.lon, lons)
        self.lat = np.append(self.lat, lats)
        self.elev = np.append(self.elev, zG)
        return

    def save_data(self, filename='data_2015'):
        """
        Save all the processed data into a binary compressed data format for retrieval later.
        :param filename:
        :return:
        """
        np.savez_compressed(filename, lon=self.lon, lat=self.lat, elev=self.elev)
        return
