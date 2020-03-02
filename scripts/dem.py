#!/usr/bin/python3

"""
The script creates a gap-filled DEM from point data.
Author: Gabija pasiunaite.
"""

import os
import rasterio
import numpy as np
from osgeo import gdal
from osgeo import osr
from lxml import etree
from rasterio.fill import fillnodata
from matplotlib import pyplot as plt
from lvis_ground import lvisGround


class lvis_to_DEM(lvisGround):

    def __init__(self, filename, minX=-100000000, maxX=100000000, minY=-1000000000, maxY=100000000,
                 setElev=False, onlyBounds=False, res=100.0):
        """
        Calls child contructor to initialize lvis params and some class attributes.
        """
        lvisGround.__init__(self, filename, minX=minX, minY=minY, maxX=maxX, maxY=maxY, setElev=setElev,
                          onlyBounds=onlyBounds)
        self.res = res
        self.nX = 0
        self.nY = 0

    def points_to_raster(self):
        """
        The function converts point data to a raster of specified resolution.
        The value of a pixel is taken as a mean of all points that fall within the pixel.
        """
        # Points -> Raster
        self.nX = int((np.max(self.lon) - np.min(self.lon)) / self.res + 1)
        self.nY = int((np.max(self.lat) - np.min(self.lat)) / self.res + 1)

        # Create a raster using histogram2d
        self.zG, yi, xi = np.histogram2d(self.lat, self.lon, bins=(self.nY, self.nX), weights=self.zG, normed=False)
        counts, _, _ = np.histogram2d(self.lat, self.lon, bins=(self.nY, self.nX))

        # Take the mean of points
        self.zG = self.zG / counts
        self.zG[np.isnan(self.zG)] = -999.0
        self.zG = np.flip(self.zG, axis=0)
        return


    def write_tiff(self, filename="fill_test.tif", epsg=3031):
        """
        Function converts a raster to a GeoTIFF and saves it in the outputs directory.
        Author: Steven Hancock.
        :param filename: output file name
        :param epsg:     EPSG projection
        """
        # Raster -> GeoTiff
        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (np.min(self.lon), self.res, 0, np.max(self.lat), 0, -self.res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create('../outputs/' + filename,
                                                      self.nX, self.nY, 1, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(self.zG)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-999)  # set no data value
        dst_ds.FlushCache()  # write to disk
        dst_ds = None

        print("Image written to", filename)
        return


    def plot_dem(self, filename="fill_test.tif"):
        """
        Helper function to plot resulting DEM.
        :param filename: name of file to plot.
        """
        src = rasterio.open("../outputs/" + filename)
        ax = plt.figure(1, figsize=[10, 9])
        #self.elev[self.elev == -999.0] = np.nan
        print(np.max(self.zG), np.min(self.zG))
        im = plt.imshow(src.read(1), vmin=400, vmax=np.max(self.zG))
        ax.colorbar(im, fraction=0.046, pad=0.04)
        plt.show()
        return

    def gapfill(self):
        """
        Fill the missing data gaps in the fligh line using Rasterio's fillnodata module.
        The algorithm uses weighted average to estimate the pixel value (search radius was set to 5 pixels).
        No smoothing was applied.
        """
        mask = ~(self.zG == -999.0)
        self.zG = fillnodata(image=self.zG, mask=mask, max_search_distance=5.0)
        return


class DEM_merge:
    """
    Class for merging all the flightine DEMs into a single gap-filled and smoothed DEM.
    """

    def __init__(self, year):
        """
        Class constructor.
        :param year: year to process
        """
        self.year = str(year)

    def merge_tiles(self):
        """
        Function merges all the single flight line DEMs into one by building a virtual raster using GDAL and averaging
        overlapping pixels. No data values are then filled by interpolating (max distance = 10 pixels)
        """
        # Change directory into the outputs file dir
        os.chdir(r"../outputs/" + self.year)
        print("Merging files from " + self.year)

        # Build a GDAL virtual raster from all the DEMs
        build_vrt_cmd = "gdalbuildvrt -srcnodata -999.0 -overwrite -r cubic " + self.year + "_avg.vrt ./*_dem.tif"
        os.system(build_vrt_cmd)

        # Add a pixel function to the VRT to average overlapping pixels.
        # Modified from: https://gis.stackexchange.com/questions/350233/how-can-i-modify-a-vrtrasterband-sub-class-etc-from-python
        vrt_tree = etree.parse(self.year + "_avg.vrt")
        vrt_root = vrt_tree.getroot()
        vrtband1 = vrt_root.findall(".//VRTRasterBand[@band='1']")[0]

        vrtband1.set("subClass", "VRTDerivedRasterBand")
        pixelFunctionType = etree.Element('PixelFunctionType')
        pixelFunctionType.text = "average"
        vrtband1.insert(0, pixelFunctionType)
        pixelFunctionLanguage = etree.Element('PixelFunctionLanguage')
        pixelFunctionLanguage.text = "Python"
        vrtband1.insert(1, pixelFunctionLanguage)
        pixelFunctionCode = etree.Element('PixelFunctionCode')
        pixelFunctionCode.text = etree.CDATA("""
import numpy as np
def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
    x = np.ma.masked_equal(in_ar, -999)
    np.mean(x, axis = 0, out = out_ar, dtype = 'Float32')
    mask = np.all(x.mask, axis = 0)
    out_ar[mask]=-999
        """)
        vrtband1.insert(2, pixelFunctionCode)
        vrt_tree.write(self.year + "_avg.vrt")

        # Merge all the rasters
        merge_cmd = "gdal_translate --config GDAL_VRT_ENABLE_PYTHON YES -a_nodata -999.0 " + \
                    self.year + "_avg.vrt " + self.year + "_merged.tif"
        os.system(merge_cmd)

        # Fill the gaps
        gap_fill_cmd = "gdal_fillnodata.py -md 10 -nomask -si 1 " + self.year + "_merged.tif " + \
                       self.year + "_filled.tif"
        print('Filling gaps in the data')
        os.system(gap_fill_cmd)

        return

    def gaussian_blur(self):
        """
        Function applies 3x3 Gaussian filter to smooth out the resulting DEM. The resulting file is written to
        YEAR.tif file.
        """
        # Build a GDAL virtual raster from the gap filled DEM.
        build_vrt_cmd = "gdalbuildvrt -srcnodata -999.0 -overwrite -r cubic " + self.year + "_smoothed.vrt " + \
                        self.year + "_filled.tif"
        os.system(build_vrt_cmd)

        # Add a pixel function to the VRT to pass a 3x3 Gaussian filter to smooth out the DEM.
        # Modified from: https://gis.stackexchange.com/questions/350233/how-can-i-modify-a-vrtrasterband-sub-class-etc-from-python
        vrt_tree = etree.parse(self.year + "_smoothed.vrt")
        vrt_root = vrt_tree.getroot()
        vrtband1 = vrt_root.findall(".//VRTRasterBand[@band='1']")[0]

        vrtband1.set("subClass", "VRTDerivedRasterBand")
        pixelFunctionType = etree.Element('PixelFunctionType')
        pixelFunctionType.text = "gaussian_blur"
        vrtband1.insert(0, pixelFunctionType)
        pixelFunctionLanguage = etree.Element('PixelFunctionLanguage')
        pixelFunctionLanguage.text = "Python"
        vrtband1.insert(1, pixelFunctionLanguage)
        pixelFunctionCode = etree.Element('PixelFunctionCode')
        pixelFunctionCode.text = etree.CDATA("""
import numpy as np
from scipy.signal import fftconvolve
from astropy.convolution import convolve_fft

def gaussian_blur(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, buf_radius, gt, **kwargs):
    size = 3
    raster = np.array(in_ar[0])
    raster[raster == -999.0] = np.nan
    # expand in_array to fit edge of kernel
    padded_array = np.pad(raster, size, 'symmetric')
    # build kernel
    x, y = np.mgrid[-size:size + 1, -size:size + 1]
    g = np.exp(-(x ** 2 / float(size) + y ** 2 / float(size)))
    g = (g / g.sum()).astype('Float32')
    # do the Gaussian blur
    out = convolve_fft(padded_array, kernel=g, nan_treatment='interpolate', min_wt=0.8, preserve_nan=True)
    out_ar[:] = out[size:-size, size:-size]
            """)

        vrtband1.insert(2, pixelFunctionCode)
        vrt_tree.write(self.year + "_smoothed.vrt")

        # Execute the smoothing and write a tiff.
        smooth_cmd = "gdal_translate --config GDAL_VRT_ENABLE_PYTHON YES " + self.year + "_smoothed.vrt " + self.year + ".tif"
        print('Applying Gaussian Blur filter')
        os.system(smooth_cmd)

        # Go back to the main working directory
        os.chdir(r"../../scripts")
        return



