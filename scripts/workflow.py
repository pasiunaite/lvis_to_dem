#!/usr/bin/python3

"""
Workflow for processing LVIS data.
"""

from lvis_ground import lvisGround


if __name__ == "__main__":
    filename = '/geos/netdata/avtrain/data/3d/oosa/assignment/lvis/2015/ILVIS1B_AQ2015_1017_R1605_071670.h5'

    # find bounds
    b = lvisGround(filename, onlyBounds=True)

    # set some bounds
    x0 = b.bounds[0]
    y0 = b.bounds[1]
    x1 = (b.bounds[2]-b.bounds[0])/15+b.bounds[0]
    y1 = (b.bounds[3]-b.bounds[1])/15+b.bounds[1]

    # read in bounds
    lvis = lvisGround(filename, minX=x0, minY=y0, maxX=x1, maxY=y1, setElev=True)

    lvis.reproject(4326, 3031)

    # find the ground
    lvis.estimateGround()

    lvis.remove_no_data()

    lvis.plot_dem()

    #print(lvis.dumpBounds())


