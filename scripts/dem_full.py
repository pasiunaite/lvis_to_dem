#!/usr/bin/python3

"""
The script creates a gap-filled DEM from point data.
Author: Gabija pasiunaite.
"""

import numpy as np
from osgeo import gdal
from osgeo import osr
import rasterio
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
        # Points -> Raster
        # Create a raster using histogram2d
        self.elev, yi, xi = np.histogram2d(self.y, self.x, bins=(self.nY, self.nX), weights=self.elev, normed=False)
        counts, _, _ = np.histogram2d(self.y, self.x, bins=(self.nY, self.nX))

        # Take the mean of points
        self.elev = self.elev / counts
        self.elev[np.isnan(self.elev)] = -999.0
        self.elev = np.flip(self.elev, axis=0)
        return


    def write_tiff(self, filename="2015_dem.tif", epsg=3031):
        """
        Function converts a raster to a GeoTIFF and saves the file.
        Author: Steven Hancock.
        :param filename:
        :param epsg:
        :return:
        """
        # Raster -> GeoTiff
        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (np.min(self.x), self.res, 0, np.max(self.y), 0, -self.res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, self.nX, self.nY, 1, gdal.GDT_Float32)

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


    def plot_dem(self, filename="2015_dem.tif"):
        src = rasterio.open("./" + filename)
        ax = plt.figure(1, figsize=[10, 9])
        im = plt.imshow(src.read(1), vmin=np.min(self.elev)+1, vmax=np.max(self.elev)-1)
        ax.colorbar(im, fraction=0.046, pad=0.04)
        plt.show()
        return


if __name__ == "__main__":
    dataset = np.load('2015.npz')
    lons = dataset['lon']
    lats = dataset['lat']
    elev = dataset['elev']
    print(elev.shape)

    dem = DEM(elevs=elev, lons=lons, lats=lats, res=30.0)
    dem.points_to_raster()
    dem.write_tiff()
    dem.plot_dem()