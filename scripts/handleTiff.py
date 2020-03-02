#!/usr/bin/python3

"""
A class to handle geotiffs.
Author: Steven Hancock.
"""

# import necessary packages
import os
import psutil
from pyproj import Proj, transform  # package for reprojecting data
from osgeo import gdal             # pacage for handling geotiff data
from osgeo import osr              # pacage for handling projection information
import numpy as np
import rasterio
from matplotlib import pyplot as plt


class tiffHandle:
    """
    Class to handle geotiff files
    """

    def __init__(self):
        """
        Class initialiser
        Does nothing as this is only an example
        """

    def plot_dem(self, filename="lvis_image.tif"):
        src = rasterio.open("./" + filename)
        ax = plt.figure(1, figsize=[10, 9])
        im = plt.imshow(src.read(1), vmin=np.min(self.data.zG)+1, vmax=np.max(self.data.zG)-1)
        ax.colorbar(im, fraction=0.046, pad=0.04)
        plt.show()
        return


    def readTiff(self, filename, epsg=3031):
        """
        Read a geotiff in to RAM
        """
        print('Reading in ', filename)
        # open a dataset object
        ds = gdal.Open(filename)
        # could use gdal.Warp to reproject if wanted?

        # read data from geotiff object
        nX = ds.RasterXSize             # number of pixels in x direction
        nY = ds.RasterYSize             # number of pixels in y direction

        # geolocation tiepoint
        transform_ds = ds.GetGeoTransform()  # extract geolocation information

        # transform_ds: 0: x corner coord, 1: res in x, 2: ...,
        # 3: y corner coord, 4: ..., 5: res in y

        # read data. Returns as a 2D numpy array
        dataset = ds.GetRasterBand(1).ReadAsArray(0, 0, nX, nY)
        return dataset, transform_ds


    def writeTiff(self, data, x, y, res, epsg=3031, filename="elevation_change.tif"):
        """
        Write a raster to a geotiff file.
        :param data: raster
        :param x:    longitudes
        :param y:    latitudes
        :param res:  resolution
        :param epsg: coordinate system
        :param filename: filename of the output
        """

        # determine image size
        nX = int((np.max(x) - np.min(x)) / res + 1)
        nY = int((np.max(y) - np.min(y)) / res + 1)

        # pack in to array
        imageArr = np.full((nY, nX), -999.0)  # make an array of missing data flags
        xInds = np.array((x - np.min(x)) / res, dtype=int)  # determine which pixels the data lies in
        yInds = np.array((np.max(y) - y) / res, dtype=int)  # determine which pixels the data lies in

        # this is a simple pack which will assign a single footprint to each pixel
        imageArr[yInds, xInds] = data

        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (np.min(x), res, 0, np.max(y), 0, -res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(imageArr)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
        dst_ds.FlushCache()  # write to disk
        dst_ds = None

        print("Image written to", filename)
        return