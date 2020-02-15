#!/usr/bin/python3

import numpy as np
from osgeo import gdal
from osgeo import osr
import rasterio
from matplotlib import pyplot as plt


def writeTiff(data, x, y, res=30.0, filename="lvis_image.tif", epsg=3031):
    # Points -> Raster
    # determine bounds
    minX = np.min(x)
    maxX = np.max(x)
    minY = np.min(y)
    maxY = np.max(y)

    # determine image size
    nX = int((maxX - minX) / res + 1)
    nY = int((maxY - minY) / res + 1)

    # Bin the data onto a grid of nY x nX
    # Have to reverse x & y due to row-first indexing
    zi, yi, xi = np.histogram2d(y, x, bins=(nY, nX), weights=data, normed=False)
    counts, _, _ = np.histogram2d(y, x, bins=(nY, nX))

    zi = zi / counts
    zi = np.ma.masked_invalid(zi)

    fig, ax = plt.subplots()
    scat = ax.pcolormesh(xi, yi, zi)
    fig.colorbar(scat)
    ax.margins(0.05)
    plt.show()

    print(xi.shape, yi.shape, zi.shape)

    return


def plot_dem(elevs, filename="lvis_image.tif"):
    src = rasterio.open("./" + filename)
    ax = plt.figure(1, figsize=[10, 9])
    im = plt.imshow(src.read(1), vmin=np.min(elevs)+1, vmax=np.max(elevs)-1)
    ax.colorbar(im, fraction=0.046, pad=0.04)
    plt.show()
    return

def plot_data_points(lon, lat, elev):
    #plt.tripcolor(self.lon, self.lat, self.zG)
    plt.scatter(x=lon, y=lat, c=elev, s=1)
    plt.gca().invert_xaxis()
    cbar = plt.colorbar()
    cbar.set_label("elevation (m)", labelpad=15)
    plt.show()
    return



if __name__ == "__main__":
    dataset = np.load('test.npz')
    lons = dataset['lon']
    lats = dataset['lat']
    elev = dataset['elev']
    print(elev.shape)

    writeTiff(data=elev, x=lons, y=lats)
    #plot_data_points(lons, lats, elev)