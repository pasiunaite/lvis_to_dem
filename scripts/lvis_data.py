#!/usr/bin/python3

"""
A class to hold LVIS data with methods to read
Author: Steven Hancock
"""

import os
import psutil
import numpy as np
import h5py


class lvisData:
    """
    LVIS data handler
    """

    def __init__(self, filename, setElev=False, minX=-100000000, maxX=100000000, minY=-1000000000,
                 maxY=100000000, onlyBounds=False):
        """
        Calls a function to read LVIS data within bounds (minX, minY, maxX, maxY)
        setElev=True converts LVIS's stop and start elevations to arrays of elevation.
        onlyBounds sets "bounds" to the corner of the area of interest.
        """
        # call the file reader and load in to the self
        self.minX, self.minY, self.maxX, self.maxY = minX, minY, maxX, maxY
        self.lon, self.lat = None, None
        self.onlyBounds = onlyBounds

        self.data_present = True
        self.readLVIS(filename)
        if self.data_present & setElev:
            self.setElevations()

    def readLVIS(self, filename):
        """
        Read LVIS data from file
        """
        # open file for reading
        f = h5py.File(filename, 'r')
        # determine how many bins
        self.nBins = f['RXWAVE'].shape[1]
        # read coordinates for subsetting
        lon0 = np.array(f['LON0'])  # longitude of waveform top
        lat0 = np.array(f['LAT0'])  # lattitude of waveform top
        lonN = np.array(f['LON' + str(self.nBins - 1)])  # longitude of waveform bottom
        latN = np.array(f['LAT' + str(self.nBins - 1)])  # lattitude of waveform bottom
        # find a single coordinate per footprint
        tempLon = (lon0 + lonN) / 2.0
        tempLat = (lat0 + latN) / 2.0

        # write out bounds and leave if needed
        if self.onlyBounds:
            self.lon = tempLon
            self.lat = tempLat
            self.bounds = self.dumpBounds()
            return

        # determine which are in region of interest
        useInd = np.where((tempLon >= self.minX) & (tempLon < self.maxX) & (tempLat >= self.minY) & (tempLat < self.maxY))
        if len(useInd) > 0:
            useInd = useInd[0]

        if len(useInd) == 0:
            self.data_present = False
            print("No data contained in that region")
            return

        # save the subset of all data
        self.nWaves = len(useInd)
        self.lon = tempLon[useInd]
        self.lat = tempLat[useInd]

        # load sliced arrays, to save RAM
        self.lfid = np.array(f['LFID'])[useInd]  # LVIS flight ID number
        self.lShot = np.array(f['SHOTNUMBER'])[useInd]  # the LVIS shot number, a label
        self.waves = np.array(f['RXWAVE'])[useInd]  # the received waveforms. The data
        self.nBins = self.waves.shape[1]

        # these variables will be converted to easier variables
        self.lZN = np.array(f['Z' + str(self.nBins - 1)])[useInd]  # The elevation of the waveform bottom
        self.lZ0 = np.array(f['Z0'])[useInd]  # The elevation of the waveform top

        # -------- RAM -----
        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
        print('memory use:', memoryUse)

        f.close()
        return

    def setElevations(self):
        """
        Decodes LVIS's RAM efficient elevation format and produces an array of
        elevations per waveform bin.
        """
        self.z = np.empty((self.nWaves, self.nBins))
        for i in range(0, self.nWaves):  # loop over waves
            res = (self.lZ0[i] - self.lZN[i]) / self.nBins
            self.z[i] = np.arange(self.lZ0[i], self.lZN[i], -1.0 * res)  # returns an array of floats
        return

    def getOneWave(self, ind):
        """
        Return a single waveform
        """
        return self.z[ind], self.waves[ind]

    def dumpCoords(self):
        """
         Dump coordinates
         """
        return self.lon, self.lat

    def dumpBounds(self):
        """
         Dump bounds
         """
        return np.min(self.lon), np.min(self.lat), np.max(self.lon), np.max(self.lat)
