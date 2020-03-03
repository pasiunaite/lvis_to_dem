#!/usr/bin/python3

"""
The script was modified from the following repo:
https://github.com/zinuzian/ImageLab2019
"""

import os
import numpy as np
from osgeo import gdal
from handleTiff import tiffHandle
import matplotlib.pyplot as plt
from skimage.draw import line, set_color
from skimage import measure, io, restoration
from pygeotools.lib import iolib, warplib, geolib, timelib, malib



class ContourFinder:

    def __init__(self, filepath):
        # Load the raster
        ds = gdal.Open(filepath)
        self.raster = np.array(ds.GetRasterBand(1).ReadAsArray())
        print(self.raster.shape, type(self.raster))
        return

    def contour(self, interval=20):
        print('Creating contours every ', interval, ' m')
        # Find the first contour
        curr_contour = np.nanmax(self.raster) - np.nanmax(self.raster) % interval

        # Find contours at a constant value: uses Marching Squares Algorithm from scikit-image
        contours = measure.find_contours(self.raster, curr_contour)
        curr_contour = curr_contour - interval

        while curr_contour > np.nanmin(self.raster):
            contours.extend(measure.find_contours(self.raster, curr_contour))
            curr_contour = curr_contour - interval


        # Display the image and plot all contours found
        fig, ax = plt.subplots()
        print(np.nanmin(self.raster), np.nanmax(self.raster))
        ax.imshow(self.raster, cmap='RdBu', clim=(-50, 50))

        print(len(contours))

        for n, contour in enumerate(contours):
            # Plot contours that have more than 20 points
            if len(contour) > 20:
                ax.plot(contour[:, 1], contour[:, 0], linewidth=0.5, color='black')

        ax.axis('image')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()

        return contours


if __name__ == "__main__":
    filepath = "../outputs/glacier_elevation_change.tif"
    cf = ContourFinder(filepath)
    cf.contour(interval=20)



