# Mapping Pine Island Glacier Using LVIS Data
**Object Orientated Software Engineering: Spatial Algorithms Project <br>
Author: Gabija Pasiunaite**

## About <br>
Land, Vegetation and Ice Sensor (**LVIS**) is a full-waveform imaging LIDAR, meaning it measures the reflected laser intensity as a function of range and the entire time history of the outgoing and return pulses is digitized. In order to derive some useful products, such as Digital Elevation Models (**DEMs**), we need to extract elevation data from the waveforms. 

The following sections describe the steps taken to produce two DEMs (2009 and 2015) over the Pine Island Glacier in Antarctica. 

## Directory <br>
- **_/media/_** contains images of the outputs
- **_/outputs/_** contains output GeoTIFFS
- **_/scripts/_** contains the following Python scripts for processing LVIS data:
  - **_contours.py_**  script for computing contours for a raster at a user specified interval.
  - **_dem.py_**  contains two class definitions for processing DEMs: lvis_to_DEM and DEM_merge.
  - **_elevation_change.py_**  script for finding elevation and volume change between two DEMs.
  - **_flight_2_dem.py_**  processes a single flight line into a DEM. 
  - **_full_dem.py_**  script uses the two classes defined in *dem.py* to process all the flightlines into a single gap-filled DEM. 
  - **_lvis_data.py_**  a class to read in LVIS data.
  - **_lvis_ground.py_**  a class for denoising waveforms and extracting elevation data from them. 
  - **_marching_squares.py_**  marching squares algorithm implementation for finding isocontours for a 2D array.

## Environment setup <br>
To run the scripts, you will first need to configure conda using the environment.yml:
```
conda env create --file environment.yml
conda activate lvis
```

## Task 1: create a DEM from a single LVIS flight line
To produce a 10 m resolution DEM for a single flight line:
```
python3 flight_2_dem.py --res 10
```
The script processes a single LVIS flight line into a DEM. The script also has a cmd parser to change the resolution and the flight line file. It first denoises the waveforms and identifies ground elevations by finding the center of mass of each waveform (see illustration below). It then uses the identified elevations to convert the point data to a raster. The value of each pixel is taken as a mean of all points that fall within the pixel. The resulting file is then writte to disc as a GeoTiff. 

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/signal.png" width="40%" height="40%" alt="alt text">
</p>

Here is a resulting 10 m resolution DEM of *ILVIS1B_AQ2015_1017_R1605_056419.h5* flight line from 2015: <br>
<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/flight_to_dem.png" alt="alt text">
</p>

## Task 2: create gap-filled DEMs for 2009 and 2015
To produce a 100 m resolution DEM for 2009:
```
python3 full_dem.py --y 2009 --res 100
```
The script processes all the flight lines that fall within the area of interest for the specified year. In order to minimize RAM usage, it saves the intermediate GeoTiffs to disc. Once all the flight lines are processed, it **merges all the DEMs** into one by building a virtual raster using GDAL and averaging overlapping pixels. **No data values are filled by interpolating** (max distance of 50 pixels was specified). **A Gaussian filter is then applied** to smooth out the gap-filled DEM. The resulting file is then written to YEAR.tif file. A kernel for the Gaussian filtering is automatically selected depending on the resolution, typically 3x3, 5x5 or 10x10.

Please note that depending on the number of inputs, the script might take a couple of hours to run. The resulting 100 m resolution DEMs for 2009 and 2015 are illustrated below:

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/dems.JPG" width="70%" height="70%" alt="alt text">
</p>

## Task 3: determine the elevation and total volume change between two DEMs
To produce an elevation change map from 2009 to 2015:
```
python3 full_dem.py --before 2009 --after 2015
```
The script processes two DEMs from different dates to create an elevation change map. First, it **preprocesses both input datasets to a common projection, extent and resolution**. Then it **differences** the preprocessed after and before rasters to create an elevation change map which is then written to disc as a GeoTiff. 

The script also **calculates multiple glacier volume and area change metrics**, such as mean elevation change rate, total area, total volume change and mass change.

Here is the **elevation change map for Pine Island Glacier from 2009 to 2015** (100 m resolution):

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/elev_change.png" width="45%" height="45%" alt="alt text">
</p>

The **change metrics computed for Pine Island Glacier from 2009 to 2015** results:
- -1.15 m/yr mean elevation change rate
- -11.37 km<sup>3</sup>/yr mean volume change rate
- -68.23 km<sup>3</sup> total volume change
- -58.00 Gt total mass change


## Task 4: add contours to the derived DEMs
To overlay contours every 50 m over the 2009 DEM:
```
python3 contours.py --fn 2009.tif --spacing 50
```
The script creates raster contours at a user specified spacing. It iterates over each contour interval and **computes contours using the Marching Squares algorithm**. 

Here are contours overlaid **every 50 m to 2009 and 2015 rasters** and **every 20 m to the elevation change map**:
<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/contour.JPG" alt="alt text">
</p>

