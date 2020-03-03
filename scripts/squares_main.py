#author: sushant
#modified by: michaelmontalbano


from osgeo import gdal
import sys
from MarchingSuares import MarchingSquareHandler
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

#Globals
winHeight = 140
winWidth = 140
msHandler = -1
ESCAPE = '\033'
window = 0
showGrid = True


def init():    
    global msHandler
    msHandler = MarchingSquareHandler()


    filepath = "../outputs/glacier_elevation_change.tif"

    ds = gdal.Open(filepath)
    raster = np.array(ds.GetRasterBand(1).ReadAsArray())
    raster[np.isnan(raster)] = -999.0
    print(raster.shape[0], raster.shape[1])

    msHandler.setWindow(raster.shape[0], raster.shape[1])
    msHandler.setGridSize(1)
    msHandler.setRadius(10)
    #msHandler.setThreshold(-990)


    msHandler.setValues(raster)

    vertices = msHandler.compute()

    # Display the image and plot all contours found
    fig, ax = plt.subplots()
    print(np.nanmin(raster), np.nanmax(raster))
    print(np.nanmin(vertices), np.nanmax(raster))
    ax.imshow(np.array(ds.GetRasterBand(1).ReadAsArray()), cmap='RdBu', clim=(-50, 50))


    for i in tqdm(range(0, 20000)):
        contour = vertices[i]
        # Plot contours that have more than 20 points
        ax.plot([contour[0][0], contour[1][0]], [contour[0][1], contour[1][1]], linewidth=2, color='green')

    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()



def main():
    global window
    init()


print("(s) to show/hide grid")
print("Hit ESC key to quit.")
main()
