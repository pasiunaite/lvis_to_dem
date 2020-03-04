# Mapping Pine Island Glacier Using LVIS Data
**Object Orientated Software Engineering: Spatial Algorithms Project**

## About <br>
Land, Vegetation and Ice Sensor (LVIS) is a full-waveform imaging LIDAR, meaning it measures the reflected laser intensity as a function of range and the entire time history of the outgoing and return pulses is digitized. In order to derive some useful products, such as Digital Elevation Models (DEMs), we need to extract elevation data from the waveforms. 

The following sections describe the steps taken to produce two DEMs (2009 and 2015) over the Pine Island Glacier in Antarctica. 

## Directory: <br>
- **/media/** contains images of the outputs
- **/outputs/** contains GeoTIFFS of the outputs
- **/scripts/** contains the following Python scripts for processing LVIS data:
  - *contours.py* script for computing contours for a raster at a user specified interval.
  - *dem.py* contains two class definitions for processing DEMs: lvis_to_DEM and DEM_merge.
  - *elevation_change.py* script for finding elevation and volume change between two DEMs.
  - *flight_2_dem.py* processes a single flight line into a DEM. 
  - *full_dem.py* script uses the two classes defined in *dem.py* to process all the flightlines into a single gap-filled DEM. 
  - *lvis_data.py* a class to read in LVIS data.
  - *lvis_ground.py* a class for denoising waveforms and extracting elevation data from them. 
  - *marching_squares.py* marching squares algorithm implementation for finding isocontours for a 2D array.

## Environment setup <br>
To run any of the scripts, you will first need to configure conda using the environment.yml:
```
conda env create --file environment.yml
conda activate lvis
```


## Task 1: create a DEM from a single LVIS flight line
The script also has a cmd parser to change the resolution, flighline file and the output DEM name.

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/signal.png" width="40%" height="40%" alt="alt text">
</p>

Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

To produce a 10 m resolution DEM for a single flight line:
```
python3 flight_2_dem.py
```

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/flight_to_dem.png" alt="alt text">
</p>

## Task 2: create gap-filled DEMs for 2009 and 2015

The script also has a cmd parser to change the resolution, flight year and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

To produce a 100 m resolution DEM for 2009:
```
python3 full_dem.py --y 2009 --res 100
```
The script might take a couple of hours to run. The resulting 100 m resolution DEMs for 2009 and 2015 are illustrated below. 

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/dems.JPG" width="70%" height="70%" alt="alt text">
</p>

## Task 3: determine the elevation and total volume change between two DEMs

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/elev_change.png" width="45%" height="45%" alt="alt text">
</p>

## Task 4: add contours to the derived DEMs

<p align="center">
<img src="https://github.com/edinburgh-university-OOSA/oosa-final-assignment-pasiunaite/blob/master/media/contour.JPG" alt="alt text">
</p>


Author: **Gabija Pasiunaite**
