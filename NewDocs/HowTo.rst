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

Step 7: Report creation 
-----------------------

Reports are then constructed using the forecasted data. They consist of a simple map of Kenya using colour to indicate the VCI level in 30 day’s time for the different regions (as designated from the shapefile) and a time-series including the forecast and the past half a year of VCI data. The residuals and standard deviation of the residuals (from the stored hindcast data)
is then calculated and displayed on the graph. These reports are then saved as pdfs. 















