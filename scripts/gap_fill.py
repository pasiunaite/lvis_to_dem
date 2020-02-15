#!/usr/bin/python3


import numpy as np
from osgeo import gdal             # pacage for handling geotiff data
from osgeo import osr              # pacage for handling projection information
import rasterio
from matplotlib import pyplot as plt


def writeTiff(self, res=30.0, filename="lvis_image.tif", epsg=3031):
    """
    Make a geotiff from an array of points
    :param res:
    :param filename:
    :param epsg:
    :return:
    """

    data = self.data.zG
    x = self.data.lon
    y = self.data.lat

    # determine bounds
    minX = np.min(x)
    maxX = np.max(x)
    minY = np.min(y)
    maxY = np.max(y)

    # determine image size
    nX = int((maxX - minX) / res + 1)
    nY = int((maxY - minY) / res + 1)

    # pack in to array
    imageArr = np.full((nY, nX), -999.0)  # make an array of missing data flags
    xInds = np.array((x - minX) / res, dtype=int)  # determine which pixels the data lies in
    yInds = np.array((maxY - y) / res, dtype=int)  # determine which pixels the data lies in

    # this is a simple pack which will assign a single footprint to each pixel
    imageArr[yInds, xInds] = data

    # set geolocation information (note geotiffs count down from top edge in Y)
    geotransform = (minX, res, 0, maxY, 0, -res)

    # load data in to geotiff object
    dst_ds = gdal.GetDriverByName('GTiff').Create(filename, nX, nY, 1, gdal.GDT_Float32)

    # ----- RAM ---
    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
    print('memory use:', memoryUse)

    dst_ds.SetGeoTransform(geotransform)  # specify coords
    srs = osr.SpatialReference()  # establish encoding
    srs.ImportFromEPSG(epsg)  # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(imageArr)  # write image to the raster
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
    dst_ds.FlushCache()  # write to disk
    dst_ds = None

    # ----- RAM ---
    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
    print('memory use:', memoryUse)

    print("Image written to", filename)
    return

if __name__ == "__main__":
    data = np.load('test.npz')
    lons = data['lon']
    lats = data['lat']
    elev = data['elev']
    print(elev.shape)