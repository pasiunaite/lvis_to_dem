#!/usr/bin/python3

"""
The script creates a gap-filled DEM from point data.
Author: Gabija pasiunaite.
"""


import os
import rasterio
import numpy as np
from osgeo import gdal
from osgeo import osr
from rasterio.fill import fillnodata
from matplotlib import pyplot as plt


class DEM:

    def __init__(self, elevs, lons, lats, res=30.0):
        """
        Initializes empty lat, long and elevation arrays to store values.
        """
        self.elev = elevs
        self.x = lons
        self.y = lats
        self.res = res
        self.nX = int((np.max(self.x) - np.min(self.x)) / self.res + 1)
        self.nY = int((np.max(self.y) - np.min(self.y)) / self.res + 1)

    def points_to_raster(self):
        """
        The funciton converts point data to a raster of specified resolution.
        The value of a pixel is taken as a mean of all points that fall within the pixel.
        """
        # Points -> Raster
        # Create a raster using histogram2d
        self.elev, yi, xi = np.histogram2d(self.y, self.x, bins=(self.nY, self.nX), weights=self.elev, normed=False)
        counts, _, _ = np.histogram2d(self.y, self.x, bins=(self.nY, self.nX))

        # Take the mean of points
        self.elev = self.elev / counts
        self.elev[np.isnan(self.elev)] = -999.0
        self.elev = np.flip(self.elev, axis=0)
        return


    def write_tiff(self, filename="fill_test.tif", epsg=3031):
        """
        Function converts a raster to a GeoTIFF and saves it in the outputs directory.
        Author: Steven Hancock.
        :param filename: output file name
        :param epsg:     EPSG projection
        """
        # Raster -> GeoTiff
        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (np.min(self.x), self.res, 0, np.max(self.y), 0, -self.res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create('../outputs/' + filename,
                                                      self.nX, self.nY, 1, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(self.elev)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
        dst_ds.FlushCache()  # write to disk
        dst_ds = None

        print("Image written to", filename)
        return


    def plot_dem(self, filename="fill_test.tif"):
        """
        Helper function to plot resulting DEM.
        :param filename: name of file to plot.
        """
        src = rasterio.open("../outputs/" + filename)
        ax = plt.figure(1, figsize=[10, 9])
        #self.elev[self.elev == -999.0] = np.nan
        print(np.max(self.elev), np.min(self.elev))
        im = plt.imshow(src.read(1), vmin=400, vmax=np.max(self.elev))
        ax.colorbar(im, fraction=0.046, pad=0.04)
        plt.show()
        return

    def gapfill(self):
        """
        Fill the missing data gaps in the fligh line using Rasterio's fillnodata module.
        The algorithm uses weighted average to estimate the pixel value (search radius was set to 5 pixels).
        No smoothing was applied.
        """
        mask = ~(self.elev == -999.0)
        self.elev = fillnodata(image=self.elev, mask=mask,  max_search_distance=5.0)
        return

    def merge_tiles(self, year):
        """
        The function merges multiple tiles into a single GeoTiff.
        :param year: year of data collection
        """
        # Change directory into the outputs file dir
        os.chdir(r"../outputs/" + str(year))
        # Get all the files in that dir that end with .tif
        files = [f for f in os.listdir('./') if f.endswith('.tif')]
        files_str = " ".join(files)
        print('Merging these files: ', files_str)

        # Merge all the tiles using GDAL merge command. Set no data value to -999.0
        merge_cmd = "gdal_merge.py -o 2015.tif -of gtiff -a_nodata -999.0 " + files_str
        os.system(merge_cmd)

        # Go back to the main working directory
        os.chdir(r"../../scripts")
        return
