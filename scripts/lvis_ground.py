#!/usr/bin/python3

"""
Some example functions for processing LVIS data.
Author: Steven Hancock.
"""

import numpy as np
from lvis_data import lvisData
from pyproj import Proj, transform
from scipy.ndimage.filters import gaussian_filter1d
import pandas as pd
import geopandas as gpd
import rasterio
from matplotlib import pyplot as plt
from handleTiff import tiffHandle

from osgeo import gdal             # pacage for handling geotiff data
from osgeo import osr              # pacage for handling projection information
from gdal import Warp
import numpy as np


class lvisGround(lvisData):
    """
    LVIS class with extra processing steps
    """

    def estimateGround(self, threshScale=5, statsLen=10, minWidth=3, smooWidth=0.5):
        """
        Processes waveforms to estimate ground.
        Only works for bare Earth. DO NOT USE IN TREES
        """
        # find noise statistics
        self.findStats(statsLen=statsLen)
        # set threshold
        threshold = self.setThreshold(threshScale)
        # remove background
        self.denoise(threshold, minWidth=minWidth, smooWidth=smooWidth)
        # find centre of gravity of remaining signal
        self.CofG()
        return

    def setThreshold(self, threshScale):
        """
        Set a noise threshold
        """
        threshold = self.meanNoise + threshScale * self.stdevNoise
        return threshold

    def CofG(self):
        """
        Find centre of gravity of denoised waveforms
        """
        # allocate space for ground elevation
        self.zG = np.full(self.nWaves, -999.9)  # no data flag for now

        # allocate space and put no data flags
        self.zG = np.full((self.nWaves), -999.0)

        # loop over waveforms
        for i in range(0, self.nWaves):
            if np.sum(self.denoised[i]) > 0.0:  # avoid empty waveforms (clouds etc)
                self.zG[i] = np.average(self.z[i], weights=self.denoised[i])
        print(self.zG.shape)
        print(self.zG)
        return

    def reproject(self, inEPSG, outEPSG):
        """
        Reproject footprint coordinates
        """
        # set projections
        inProj = Proj(init="epsg:" + str(inEPSG))
        outProj = Proj(init="epsg:" + str(outEPSG))
        # reproject data
        x, y = transform(inProj, outProj, self.lon, self.lat)
        self.lon = x
        self.lat = y
        return

    def findStats(self, statsLen=10):
        """
        Finds standard deviation and mean of noise
        """
        self.meanNoise = np.empty(self.nWaves)
        self.stdevNoise = np.empty(self.nWaves)

        # determine number of bins to calculate stats over
        res = (self.z[0, 0] - self.z[0, -1]) / self.nBins  # range resolution
        noiseBins = int(statsLen / res)  # number of bins within "statsLen"

        # loop over waveforms
        for i in range(0, self.nWaves):
            self.meanNoise[i] = np.mean(self.waves[i, 0:noiseBins])
            self.stdevNoise[i] = np.std(self.waves[i, 0:noiseBins])
        return

    def denoise(self, threshold, smooWidth=0.5, minWidth=3):
        """
        Denoise waveform data
        """
        # find resolution
        res = (self.z[0, 0] - self.z[0, -1]) / self.nBins  # range resolution

        # make array for output
        self.denoised = np.full((self.nWaves, self.nBins), 0)

        # loop over waves
        for i in range(0, self.nWaves):
            print("Denoising wave", i + 1, "of", self.nWaves)

            # subtract mean background noise
            self.denoised[i] = self.waves[i] - self.meanNoise[i]

            # set all values less than threshold to zero
            self.denoised[i, self.denoised[i] < threshold[i]] = 0.0

            # minimum acceptable width
            binList = np.where(self.denoised[i] > 0.0)[0]
            for j in range(0, binList.shape[0]):  # loop over waveforms
                if (j > 0) & (j < (binList.shape[0] - 1)):  # are we in the middle of the array?
                    if (binList[j] != binList[j - 1] + 1) | (
                            binList[j] != binList[j + 1] - 1):  # are the bins consecutive?
                        self.denoised[i, binList[j]] = 0.0  # if not, set to zero

            # smooth
            self.denoised[i] = gaussian_filter1d(self.denoised[i], smooWidth / res)
        print('self.lon: ', self.lon.shape)
        print('self.lat: ', self.lat.shape)
        return

    def writeTiff(self, res=10.0, filename="../outputs/dem.tif", epsg=3031):
        """
        Write a geotiff from a raster layer
        """
        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (self.minX, res, 0, self.maxY, 0, -1*res)

        # determine image size
        nX = int((self.maxX - self.minX) / res + 1)
        nY = int((self.maxY - self.minY) / res + 1)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(geotransform)    # specify coords
        srs = osr.SpatialReference()            # establish encoding
        srs.ImportFromEPSG(epsg)                # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(self.zG)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
        dst_ds.FlushCache()                     # write to disk
        dst_ds = None

        print("Image written to", filename)
        return

    def plot_DEM(self, filename="../outputs/dem.tif"):
        """
        Plot DEM
        :param filename:
        :param self:
        :return:
        """
        src = rasterio.open(filename)
        plt.imshow(src.read(1), cmap='pink')
        plt.show()

        return
