How to use the pipeline
=======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This page documents how each part of the pipeline is controlled to get the desired output.

Important Infomation
--------------------

The main feature of the pipeline is its ability to work with any shape-file within Kenya. The shape-file is used to aggregate the data to any level (county/sub-county/ward/grazing block etc.) calibrate errors using hindcasts and then forecast for each area. 
The name of the shapefile controls the name of the database hdf5 file that is created and used. This means that when the same shapefile is used (with the pipeline in the update mode) the previously created time-series will be updated meaning a new one will not have to be made from scratch.
Because of the pipeline’s ability to do this, the file path to the shapefile and the ID or name column in the shapefile must be set. The ID/name columns determine what the name of the output forecast reports are. For example, you want this to be set to the name of the county so that the
reports are outputted as ‘Kitui Forecast Dated 05-05-2020’ or ‘Turkana Forecast Dated 05-05-2020’ etc. This is set on line 40 of the Main.py document and should be used like so: 

.. code-block:: python

    shapefile_filepath = '..\\CountyShapes\\County.shp'


The settings of the pipeline
----------------------------

The pipeline has three main settings. The first, used to smooth the entire dataset for the first time, create a new time-series, hindcast to calibrate errors and then create forecasts.
How to use setting one (Fresh run):

To use the first setting, all the dekadal must be placed into the ‘RCMRD Data’ folder. 

The next step is to set the value of some key Boolean variables in the Main.py on lines 34-38. They should be set as seen below :

.. code-block:: python

	create_new_time_series = True
    
    convert_NDVI_from_scratch = True
    
    calibrate_errors = True 

This setting will take a long time to run. Using the Sussex HPC this took ~ 15 hours. This has since been completed on the RCMRD server and therefore should not need to be run in this setting again. 



The second setting is used once you have a smoothed dataset, new data is downloaded, and you want to update your time-series ‘database’ with new, smoothed data and create new forecasts. 

How to use setting two (Update forecasts):

Once the first setting has been used, the databases that have been created can now be updated. 

For this to run, the previous year of data (before the newly downloaded data) must be left in the ‘RCMRD data’ folder. The reason for this is so when the Whittaker smoothing algorithm is run it maintains the same quality as the previous soothing. 
I recommend that all the raw, unsmoothed data is left in the folder in-case the program need to be restarted from scratch at any point, but it can function with just the previous 36 files + the new files. They key boolean variables should now be changed to the following: 

.. code-block:: python

	create_new_time_series = False
    
    convert_NDVI_from_scratch = False
    
    calibrate_errors = False 
	


The third is when you want to create a new time-series from pre-smoothed data. This just creates a new ‘database’ performs the hindcasts and creates new forecasts. 

How to use setting three (Create new time-series database).

This is the easiest setting to use. It just looks at the data that has already been smoothed and then aggregates and creates a new time-series database. 
Ensure that the shapefile is the same one used to create the original so that the names match and the data is saved to the correct database. Again, the key variables need to be changed, this time, to the following configuration: 

.. code-block:: python

	create_new_time_series = True
    
    convert_NDVI_from_scratch = False
    
    calibrate_errors = True 
	

How the databases work
----------------------
The databases are saved in the hdf5 format using the h5py python module. 
Within an hdf file there are several ‘datasets’ that can be accessed through the h5py module in a dictionary style.
 You can access these datasets which then contain the date, NDVI, VCI 10D and the VCI3M. They also (once hindcasts have been performed) contain the hindcast data.
The data can be accessed with the h5py module like so:

.. code-block:: python

	Import h5py as h5
	
	X = h5.File(‘County.h5’,’r’)
	
	key_list = list(x.keys())
	
	data_array = x[key_list[0]][:]
	
	#Data array is a 2-D array, essentially a spreadsheet. In the first column are the dates and are accessed like so:
	
	Dates = data_array[:,0]
	
In the second column is the corresponding NDVI values, third is the VCI10D and fourth is the VCI3M. There are then 10 extra columns which contain information about the hindcasts. Each column represents a lag time for the hindcasts, e.g. 10 day lag time, 20 day lag time and so on. This has been done so that different metrics can be used to assess how well the pipeline’s forecasts are doing. 














