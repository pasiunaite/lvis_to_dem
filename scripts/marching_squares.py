#!/usr/bin/python3

"""
The script was modified from the following repo:
https://github.com/zinuzian/ImageLab2019
"""

import os
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt
from PyQt5 import QtGui, QtCore, QtWidgets
from skimage.draw import line, set_color
from skimage import measure, io, restoration


class ContourFinder:

    def __init__(self, filepath):

        # Load img file
        self.filepath = filepath
        self.original = io.imread(self.filepath, as_gray=True)

        # Load the raster
        ds = gdal.Open("../outputs/2009.tif")
        self.original = np.array(ds.GetRasterBand(1).ReadAsArray())


        self.pen_color = "#ff0000"
        self.value = -1.0

    def setColor(self, colorValue):
        self.color = colorValue

    def choose(self, x, y):
        self.value = self.original[y][x]
        return self.value


    def find(self, value):
        try:
            # Denoise the original image
            denoised = restoration.denoise_tv_chambolle(self.original, weight=0.1, multichannel=True)

            print(np.min(denoised), np.max(denoised), np.median(denoised))
            # denoised = restoration.denoise_wavelet(self.image, multichannel=True)

            # Find contours at a constant value
            # Uses Marching Squares Algorithm
            contours = measure.find_contours(denoised, value)

            # Display the image and plot all contours found
            fig, ax = plt.subplots()
            ax.imshow(denoised, cmap=plt.cm.gray)

            for n, contour in enumerate(contours):
                ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

            ax.axis('image')
            ax.set_xticks([])
            ax.set_yticks([])
            plt.show()

            return contours

        except Exception as e:
            print(e)

    def save(self, savePath, contours, colorStr):
        try:
            h = colorStr.lstrip('#')
            colorIntArray = list(int(h[i:i + 2], 16) for i in (0, 2, 4))
            colorIntArray = np.array(colorIntArray)

            colorFloatArray = colorIntArray

            ext = self.filepath.split('.')[1]
            if ext == "png" or ext == "PNG":
                print("png detected")
                # colorIntArray = np.append(colorIntArray, [1])
                colorFloatArray = np.append(colorFloatArray, [255])


            # print(colorIntArray)
            print(colorFloatArray)

            temp = io.imread(self.filepath, as_gray=False)
            #print(temp)
            for n, contour in enumerate(contours):
                for i in range(len(contour) - 1):
                    rr, cc = line(int(contour[i, 0]), int(contour[i, 1]), int(contour[i + 1, 0]),
                                  int(contour[i + 1, 1]))
                    # set_color(temp, (rr, cc), colorIntArray)
                    set_color(temp, (rr, cc), colorFloatArray)

            #print(temp)
            io.imsave(savePath, temp)

            return True
        except Exception as e:
            print(e)




if __name__ == "__main__":
    filepath = "test.png"
    cf = ContourFinder(filepath)

    #cf.save("result.png", cf.find(0.7), "#ff0000")



