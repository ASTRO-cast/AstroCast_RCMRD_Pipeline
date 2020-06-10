Pipeline Overview
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This page describes what each section of the pipeline does and why. 
There are 7 main stages of the pipeline. Each stage has been segmented as one or two different module files to ensure the code is nice and readable. 
The input to the pipeline files are dekadal NDVI TIF files. They are the 10-day maximum composites of NDVI processed and collected by RCMRD using the MODIS satellite. 


Step 1: Changing the size of the raw files
------------------------------------------

The first step in the pipeline is the adaptation of the raw data. From 2018 onwards, there is a shift in the size of the TIF files covering Kenya. From 2003-2018 the size
of the files are 3611 x 4406 but this changes to 3601 x 4393 in the most recent data collections. As the algorithms created need a consistent size, 10 rows of null pixels
are appended onto the vertical height of the image, 5 at the top and 5 at the bottom. On the horizontal size of the image, 7 columns of null pixels are added on the left 
and then 6 columns of null pixels are added to the right. These images are then saved, overwriting the previous dekadal data.

Improvements that can be made
*****************************
These pixels can be geolocated and the reasons for why this happen can be investigated.



Step 2: Smoothing the data
------------------------------------------

It was found that data collected pre-2017 was smoothed. This was not the case for the most current data. This lead to issues when converting from NDVI to VCI. 
To create a more reliable product the Whittaker smoother was implemented in Python. Two functions where created, one which handles the smoothing on the first run 
of the program (all the data) and one which handles the regular smoothing of the new data. 

**Smoothing on first run**

The full dataset is first loaded in and split into two, ensuring there is a small, 10 dekadal overlap. This is so the older smoothed data can be perfectly matched 
with the newly smoothed data. This smoothing is performed on each pixel from the 563rd dekadal onwards and the previously smoothed data is checked for any null values
(cloud coverage) and then the two points either side are used to fill in the missing value with a linear interpolation. 

During this process there is a lot of temporary data stored (~40 Gb). This data is deleted after, but it is worth noting as the smoothed data will also be created and saved in the process leading to a lot of data being created in total.
Smoothing only new files
When newly downloaded files are to be smoothed, a year of data previous to it is also loaded into the program. This is to ensure the newly smoothed data does match up with the previously smoothed data. It also reduces the time taken for the smoothing algorithm to run

Improvements that can be made
*****************************
As this is a very quick process that is performed millions of times, python may not be the best language for the job (as it is interpreted). I have created the same algorithm in C++ and linked it into the Python front end and it does show 
the potential for a speed-up in the ballpark of 5-10 times.

Step 3: Finding the Min/Max of each pixel
-----------------------------------------

To convert NDVI to VCI it is required that the minimum and maximum NDVI values are found, for each pixel at each time-step. This is a fairly simple step that just compares the same dekadal from each of the different years and find the minimum and maximum pixel. Currently, this is running 
on the baseline of 2003-2018 but it is very possible this will change in the future. 

Step 4: Aggregation
-------------------

Once the NDVI has been produced, the aggregation of the NDVI can occur.  A shapefile is used to crop the NDVI TIFF alongside the Min and Max TIFFs for the respective dekadal. The VCI is then calculated each pixel using the standard formula and the min/max of each pixel. 
Any null values (clouded values) are masked out and then the amount of null values is compared to the amount of valid values. If less than 1% of the shape contains valid data, then the value is just said to be null and later interpolated by the gaussian processes. 

The date, average NDVI and average VCI for each shape in the shapefile is saved for each timestep into an HDF ‘database’ with the same name as the original shapefile. Later, hindcast data is also stored into this file.

Step 5: Hindcasts
-----------------

Each shape in the shapefile then has hindcasts performed. The first half of the time-series is used for training the gaussian processes code with the second half being used to verify the accuracy of the forecasts. The forecast values are stored alongside the actual values from the same date. This is so that the residuals, r-squared score etc can then be calculated and updated each time the program is run. 
Whenever a forecast is performed the new forecasts are stored in the hindcast columns of the HDF ‘database’.



Step 6: Forecasting
-------------------

Forecasts are then performed using the most recent data for each shape in the shapefile. This is done using the Gaussian processes (GP) code developed by the AstroCast team. Any null values are masked out and the GP code will interpolate and forecast 
90 days into the future (9 dekadals). These forecasts are then saved alongside the hindcasts.

Step 7: Report creation 
-----------------------

Reports are then constructed using the forecasted data. They consist of a simple map of Kenya using colour to indicate the VCI level in 30 day’s time for the different regions (as designated from the shapefile) and a time-series including the forecast and the past half a year of VCI data. The residuals and standard deviation of the residuals (from the stored hindcast data)
is then calculated and displayed on the graph. These reports are then saved as pdfs. 















