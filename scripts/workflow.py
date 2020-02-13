#!/usr/bin/python3

"""
Workflow for processing LVIS data.
"""

from lvis_ground import lvisGround


if __name__ == "__main__":
    filename = '/geos/netdata/avtrain/data/3d/oosa/week4/lvis_antarctica/ILVIS1B_AQ2015_1014_R1605_070717.h5'

    # find bounds
    b = lvisGround(filename, onlyBounds=True)

    # set some bounds
    x0 = b.bounds[0]
    y0 = b.bounds[1]
    x1 = (b.bounds[2]-b.bounds[0])/15+b.bounds[0]
    y1 = (b.bounds[3]-b.bounds[1])/15+b.bounds[1]

    #print(x0, y0, x1, y1)

    # read in bounds
    lvis = lvisGround(filename, minX=x0, minY=y0, maxX=x1, maxY=y1, setElev=True)

    lvis.reproject(4326, 3031)
    #lvis.setElevations()

    # find the ground
    lvis.estimateGround()

    lvis.writeTiff(res=30.0)

    #print(lvis.dumpBounds())


