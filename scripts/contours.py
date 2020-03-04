#!/usr/bin/python3

"""
Task 4: calculate contour lines.

The script contains ContourFinder class which holds methods for creating raster contours at a specified spacing.
Currently, two implementations of the method exist. Both of them use the Marching Squares algorithm.

The first one, contour(), iterates over each contour interval and uses skimage's implementation of the
Marching Square's algorithm to compute the contours.

The second one, contour_trial(), is my attempt to write the Marching Squares algorithm. It does return the computed
vertices of each contour but I would not recommend using it because it is super slow.

Author: Gabija Pasiunaite
"""


import argparse
import numpy as np
from osgeo import gdal
from skimage import measure
import matplotlib.pyplot as plt
from marching_squares import MarchingSquareHandler


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    parser = argparse.ArgumentParser(description="Add contour lines to an existing DEM.")
    parser.add_argument('--fn', dest='filename', type=str, default='2009.tif', help="Filename of a DEM to which add the contours to.")
    parser.add_argument('--spacing', dest='spacing', type=int, default=50, help="Spacing of contour lines (in m).")
    args = parser.parse_args()
    return args


class ContourFinder:

    def __init__(self, filepath):
        # Load the raster as np array
        self.file = filepath
        ds = gdal.Open('../outputs/' + self.file)
        self.raster = np.array(ds.GetRasterBand(1).ReadAsArray())
        print(self.raster.shape, type(self.raster))
        return

    def contour(self, interval=20):
        """
        Function adds contours to a raster at a user specified interval. It iterates over each range and computes
        contours using the Marching Squares algorithm from skimage.
        :param interval:
        :return:
        """
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
        print('Min:', np.nanmin(self.raster), 'Max: ', np.nanmax(self.raster))
        im = ax.imshow(self.raster, cmap='RdBu', clim=(np.nanmin(self.raster) + 50, np.nanmax(self.raster) - 50))
        plt.title(self.file[0:-4])
        plt.colorbar(im, label='Elevation (m)', shrink=0.7)
        axs = plt.gca()
        axs.set_facecolor('0.7')

        for n, contour in enumerate(contours):
            # Plot contours that have more than 20 points
            if len(contour) > 20:
                ax.plot(contour[:, 1], contour[:, 0], linewidth=0.5, color='black')

        ax.axis('image')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()

        return contours

    def contour_trial(self):
        """
        Attempt to implement Marching Squares algorithm for computing contours from scratch.
        """
        msHandler = MarchingSquareHandler()

        # Read in dataset as np array
        ds = gdal.Open(self.filepath)
        raster = np.array(ds.GetRasterBand(1).ReadAsArray())
        raster[np.isnan(raster)] = -999.0
        print(raster.shape[0], raster.shape[1])

        # Set params: width, height and grid size of the raster
        msHandler.setWindow(raster.shape[0], raster.shape[1])
        msHandler.setGridSize(1)
        msHandler.setRadius(10)

        msHandler.setValues(raster)
        vertices = msHandler.compute()

        # Display the image and plot all contours found
        fig, ax = plt.subplots()
        print(np.nanmin(raster), np.nanmax(raster))
        print(np.nanmin(vertices), np.nanmax(raster))
        ax.imshow(np.array(ds.GetRasterBand(1).ReadAsArray()), cmap='RdBu', clim=(-50, 50))

        for contour in vertices:
            ax.plot([contour[0][0], contour[1][0]], [contour[0][1], contour[1][1]], linewidth=0.5, color='black')

        ax.axis('image')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()


if __name__ == "__main__":
    cmd_args = getCmdArgs()
    # Create a ContourFinder class instance and compute contours for the input raster
    cf = ContourFinder(cmd_args.filename)
    cf.contour(interval=cmd_args.spacing)



