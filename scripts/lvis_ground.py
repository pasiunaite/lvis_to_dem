#!/usr/bin/python3

"""
Some example functions for processing LVIS data.
Author: Steven Hancock.
"""

import os
import psutil
import numpy as np
import pandas as pd
from lvis_data import lvisData
from pyproj import Proj, transform
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d


class lvisGround(lvisData):
    """
    LVIS class with extra processing steps
    """

    def __init__(self, filename, minX=-100000000, maxX=100000000, minY=-1000000000, maxY=100000000,
                 setElev=False, onlyBounds=False):
        lvisData.__init__(self, filename, minX=minX, minY=minY, maxX=maxX, maxY=maxY, setElev=setElev,
                          onlyBounds=onlyBounds)

    def estimateGround(self, threshScale=5, statsLen=10, minWidth=3, smooWidth=0.5):
        """
        Processes waveforms to estimate ground.
        Only works for bare Earth. DO NOT USE IN TREES
        """
        # find noise statistics
        self.findStats(statsLen=statsLen)
        # set threshold
        threshold = self.meanNoise + threshScale * self.stdevNoise
        # remove background
        self.denoise(threshold, minWidth=minWidth, smooWidth=smooWidth)
        # find centre of gravity of remaining signal
        self.CofG()
        # Remove no data points (-999.0) form lat, long and zG arrays
        self.lon = self.lon[self.zG != -999.0] #- 180
        self.lat = self.lat[self.zG != -999.0]
        self.zG = self.zG[self.zG != -999.0]
        return

    def CofG(self):
        """
        Find centre of gravity of denoised waveforms
        """
        # allocate space for ground elevation and put no data flags
        self.zG = np.full(self.nWaves, -999.0)

        # loop over waveforms
        for i in range(0, self.nWaves):
            if np.sum(self.denoised[i]) > 0.0:  # avoid empty waveforms (clouds etc)
                self.zG[i] = np.average(self.z[i], weights=self.denoised[i])
        print(self.zG.shape)
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

        print('No of waves: ', self.nWaves, 'resolution: ', res)
        # ----- RAM ---
        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
        print('memory use:', memoryUse)

        # loop over waves
        for i in range(0, self.nWaves):
            if i % 50000 == 0:
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
        return

    def plot_data_points(self):
        #plt.tripcolor(self.lon, self.lat, self.zG)
        plt.scatter(x=self.lon, y=self.lat, c=self.zG, s=1)
        plt.gca().invert_xaxis()
        cbar = plt.colorbar()
        cbar.set_label("elevation (m)", labelpad=15)
        plt.show()
        return

    def save_to_file(self, filename='data_2015'):
        """
        Save all the processed data into a binary compressed data format for retrieval later.
        :param filename:
        :return:
        """
        np.savez_compressed(filename, lon=self.lon, lat=self.lat, elev=self.zG)
        return

    def get_results(self):
        return self.lon, self.lat, self.zG

