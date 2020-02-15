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

    def __init__(self, elevs, lons, lats, res):
        """
        Initializes empty lat, long and elevation arrays to store values.
        """
        self.elev = elevs
        self.x = lons
        self.y = lats
        self.res = res
        self.nX = int((np.max(self.x) - np.min(self.x)) / self.res + 1)
        self.nY = int((np.max(self.y) - np.min(self.y)) / self.res + 1)

    def points_to_raster(self, data, x, y, res):
        # Points -> Raster

        # Create a raster using histogram2d
        zi, yi, xi = np.histogram2d(y, x, bins=(self.nY, self.nX), weights=data, normed=False)
        counts, _, _ = np.histogram2d(y, x, bins=(self.nY, self.nX))

        # Take the mean of points
        zi = zi / counts
        zi[np.isnan(zi)] = -999.0
        zi = np.flip(zi, axis=0)
        return



    def writeTiff(self, data, x, y, res=100.0, filename="2015_dem.tif", epsg=3031):
        # Points -> Raster
        # determine bounds
        minX = np.min(x)
        maxX = np.max(x)
        minY = np.min(y)
        maxY = np.max(y)

        # determine image size
        nX = int((maxX - minX) / res + 1)
        nY = int((maxY - minY) / res + 1)
        print(nX, nY)

        # Create a raster using histogram2d
        zi, yi, xi = np.histogram2d(y, x, bins=(nY, nX), weights=data, normed=False)
        counts, _, _ = np.histogram2d(y, x, bins=(nY, nX))

        # Take the mean of points
        zi = zi / counts
        zi[np.isnan(zi)] = -999.0
        zi = np.flip(zi, axis=0)

        # Raster -> GeoTiff
        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (minX, res, 0, maxY, 0, -res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)

        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(zi)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
        dst_ds.FlushCache()  # write to disk
        dst_ds = None

        print("Image written to", filename)
        return


def plot_dem(elevs, filename="2015_dem.tif"):
    src = rasterio.open("./" + filename)
    ax = plt.figure(1, figsize=[10, 9])
    im = plt.imshow(src.read(1), vmin=np.min(elevs)+1, vmax=np.max(elevs)-1)
    ax.colorbar(im, fraction=0.046, pad=0.04)
    plt.show()
    return



if __name__ == "__main__":
    dataset = np.load('data.npz')
    lons = dataset['lon']
    lats = dataset['lat']
    elev = dataset['elev']
    print(elev.shape)

    writeTiff(data=elev, x=lons, y=lats)
    plot_dem(elevs=elev)