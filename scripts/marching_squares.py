#!/usr/bin/python3

"""
The script was modified from the following repo:
https://github.com/zinuzian/ImageLab2019
"""

import argparse
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt
from skimage import measure, io, restoration


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Add contour lines to an existing DEM.")
    # Add arguments
    parser.add_argument('--fn', dest='filename', type=str, default='2009.tif', help="Filename of a DEM to which add the contours to.")
    parser.add_argument('--spacing', dest='spacing', type=int, default=50, help="Spacing of contour lines (in m).")
    # Parse arguments
    args = parser.parse_args()
    return args


class ContourFinder:

    def __init__(self, filepath):
        # Load the raster
        self.file = filepath
        ds = gdal.Open('../outputs/' + self.file)
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


if __name__ == "__main__":
    cmd_args = getCmdArgs()
    cf = ContourFinder(cmd_args.filename)
    cf.contour(interval=cmd_args.spacing)



