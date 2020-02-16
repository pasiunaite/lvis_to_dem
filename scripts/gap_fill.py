#!/usr/bin/python3

"""
Task 1: create a DEM from a single LVIS flight line.

The script also has a cmd parser to change the resolution, flighline file and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

Author: Gabija Pasiunaite
"""

import numpy as np
from lvis_ground import lvisGround
from handleTiff import tiffHandle
import numpy as np
from osgeo import gdal
from osgeo import osr
import rasterio
from rasterio.fill import fillnodata
from matplotlib import pyplot as plt


class DEM:

    def __init__(self, elevs, lons, lats, res=10.0):
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


    def write_tiff(self, filename="fill_test.tif", epsg=3031):
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


    def plot_dem(self, filename="fill_test.tif"):
        src = rasterio.open("./" + filename)
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
        The algorithm uses inverse distance weighting to estimate the value (search radius was set to 5 pixels).
        No smoothing was applied.
        :return:
        """
        mask = ~(self.elev == -999.0)
        self.elev = fillnodata(image=self.elev, mask=mask,  max_search_distance=5.0)
        return

if __name__ == "__main__":
    dataset = np.load('test.npz')
    lons = dataset['lon']
    lats = dataset['lat']
    elev = dataset['elev']
    print(elev.shape)

    dem = DEM(elevs=elev, lons=lons, lats=lats, res=10.0)
    dem.points_to_raster()
    dem.gapfill()
    dem.write_tiff()
    dem.plot_dem()