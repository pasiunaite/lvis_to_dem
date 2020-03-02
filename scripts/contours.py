#!/usr/bin/python3

"""
Task 4: Add contours to any raster at a user defined interval.

Author: Gabija Pasiunaite
"""

import os
import numpy as np
import argparse
from handleTiff import tiffHandle

os.system("pip install pygeotools")
from pygeotools.lib import iolib, warplib, geolib, timelib, malib


def getCmdArgs():
    """
    Function parses command line arguments.
    :return: args: cmd arguments
    """
    # Create an argparse object with a help comment
    parser = argparse.ArgumentParser(description="Add contour lines to an existing DEM.")
    # Add arguments
    parser.add_argument('--fn', dest='filename', type=str, default='2009.tif', help="Filename of a DEM to which add the contours to.")
    parser.add_argument('--spacing', dest='spacing', type=int, default=10, help="Spacing of contour lines (in m).")
    # Parse arguments
    args = parser.parse_args()
    return args


class Contours:

    def __init__(self, filename, spacing):
        """
        Class constructor.
        """
        self.file = '../outputs/' + filename
        self.spacing = spacing

    def add_contours(self):
        """
        Marching Squares vs Dividing Cubes
        http://www.inf.ed.ac.uk/teaching/courses/vis/lecture_notes/lecture7.pdf
        :return:
        """

        return



if __name__ == "__main__":
    cmd_args = getCmdArgs()
    contours = Contours(cmd_args.filename, cmd_args.spacing)
