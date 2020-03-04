# Mapping Pine Island Glacier Using LVIS Data
**Object Orientated Software Engineering: Spatial Algorithms Project**

## About <br>
Land, Vegetation and Ice Sensor (LVIS) is a full-waveform imaging LIDAR, meaning it measures the reflected laser intensity as a function of range and the entire time history of the outgoing and return pulses is digitized. In order to derive some useful products, such as Digital Elevation Models (DEMs), we need to extract elevation data from the waveforms. 

The following sections describe the steps taken to produce two DEMs (2009 and 2015) over the Pine Island Glacier in Antarctica. 

## Directory: <br>
- *arg_parser.py* example script for parsing command line arguments using *argparse*
- *myBank.py* example of a Bank class (script supplied bu course organizer Steven Hancock)
- *evil_bank.py* a child class of Bank that overloads inquiry()
- *class_minima.py* a class definition for unsorted arrays. Includes functions for manipulating arrays such as selection sort, binary search and plotter. 

## Environment setup <br>
To run any of the scripts, you will first need to configure conda using the environment.yml:
```
conda env create --file environment.yml
conda activate lvis
```


## Task 1: create a DEM from a single LVIS flight line
The script also has a cmd parser to change the resolution, flighline file and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

## Task 2: create gap-filled DEMs for 2009 and 2015

The script also has a cmd parser to change the resolution, flight year and the output DEM name.
Pine Island Glacier bounding box was set to the following lats and longs: [-74, 97; -75.7, 104]

## Task 3: determine the elevation and total volume change between two DEMs

## Task 4: add contours to the derived DEMs


Author: **Gabija Pasiunaite**
