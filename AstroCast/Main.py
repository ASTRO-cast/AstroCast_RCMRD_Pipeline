# -*- coding: utf-8 -*-
"""This is the main body and will run through each pipeline step.
Created on Sat Apr 11 14:19:35 2020
@author: Andrew

"""

from glob import glob
import h5py as h5
import numpy as np
import sys
import os
import shutil
import fix_size
import whittaker_smoothing
import NDVI_Normalisation
import Aggregate
import Forecast
import Hindcasts


def main():


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # The two varibles below contol the program. On the first run setting both
    # to TRUE edits the size of the NDVI files so they match, runs the smoothing,
    # finds the min/max values for each pixel and then aggregates into a database
    # and forecasts. THIS CREATES A NEW DATABASE.
    
    # Setting create_new_time_series to TRUE and convert from scratch to FALSE
    # avoids any smoothing, changing of file size and min/max finding. It simply
    # acesses the smoothed data and then aggregates into a NEW DATABASE
    
    # Setting both variables to FALSE means the program looks for new NDVI data
    # to smooth, if there is any, smooths it then aggregates and APPENDS it onto 
    # a current database. This means the database file needs to have been created
    # previously.
    
    #C:\\Rangeland\\image_data\\Andrew
    # Adding a loop so that the automation of several shapefiles can be done
    
    shape_files = ['C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\KenyaShape\\ken_admbnda_adm0_iebc_20191031.shp',
                   'C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\CountyShapes\\County.shp']
    
    shape_file_columns = ['ADM0_EN','Name']
    
    create_new_time_series_list = [True,True]
    
    convert_NDVI_from_scratch_list = [True,False]
    
    
    for shape,column,new_time_series,from_scratch in zip(shape_files,shape_file_columns,create_new_time_series_list,convert_NDVI_from_scratch_list):
    
        create_new_time_series = new_time_series
        
        convert_NDVI_from_scratch = from_scratch
        
    
        
        # Below is a description of some of the filepathing. I will include all the
        # folders needed in the zip I send over.
        # This is the path to the shapefile. I have included two here to default to.
        # One is the enitrety of Kenya and the other is counties. The shapefile name
        # dictates what the database name will be.
    
    
    
        shapefile_filepath = shape
    
        
        # This is the path to the raw NDVI data
        
        NDVI_filepath = 'C:\\Rangeland\\image_data\\Andrew\\RCMRD Data'
    
        # This is a path to where the smoothed data will be stored.
        smoothed_NDVI_filepath = 'C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\smoothed_NDVI'
        
        # Path to the database. This is currently hardcoded in some places but I 
        # hope to update this in the future to make it more robust.
        
        Database_path = 'C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Databases\\'
        
    
        
        # This is the name of the shapefile column that is to be used. Ideally needs
        # to be unique but also describe the region. I have two here that correspond
        # to the shapefiles above. 
        
        name_of_shapefile_column = column
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        # This is the first stage of the program occuring beofre any of the options
        # have been picked. It gets the name of the shapefile and looks for any 
        # smoothed/unsmoothed NDVI. It also checks to see if any file sizes need to 
        # be changed slighty to make sure they line up
    
    
    
        shapefile_name = shapefile_filepath.split('.shp')[0].split('\\')[-1]
    
        unsmoothed_NDVI = sorted(glob(NDVI_filepath+'\\*.tif'))
        
        smoothed_NDVI = sorted(glob(smoothed_NDVI_filepath+'\\*.tif'))
    
    
        fix_size.change_file_size(unsmoothed_NDVI,NDVI_filepath)
        
        
        if create_new_time_series and convert_NDVI_from_scratch:
            
            # This is the first option described above. This is what needs to be run 
            # for the first time. 
            
            
            unformatted_dates = [int(file.split('dekadal.')[1].split('.tif')
                                          [0]) for file in unsmoothed_NDVI]
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # Smooth each pixel
            whittaker_smoothing.run_smoothing(unsmoothed_NDVI,False,0)
       
        
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # Activate min/max normalisation class
            Nomalise_NDVI = NDVI_Normalisation.NDVI_normalisation(smoothed_NDVI)
    
            # Run the min/max finding algorithm
            Nomalise_NDVI.normalise()
        
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            #Activate class to create time series
            create_time_series = \
                Aggregate.aggregate_time_series(smoothed_NDVI,
                                                shapefile_filepath,
                                                create_new_time_series,
                                                
                                                name_of_shapefile_column)
            # Run time series creation algorithm
            create_time_series.open_files()
    
            
            # Use the databse (HDF5 file) to create hindcasts
            database_name= shapefile_filepath.split('.shp')[0].split('\\')[-1]
    
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # Activate class
            create_hindcasts = Hindcasts.hindcast(database_name)
            #Create Hindcasts
            create_hindcasts.open_dataset()
    
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # Create forecasts
            create_the_forecasts = Forecast.forecast(database_name,
                                                      shapefile_filepath,
                                                      name_of_shapefile_column)
            create_the_forecasts.open_dataset()
    
            
        elif create_new_time_series is True and convert_NDVI_from_scratch is False:
            
            # This is the second option for the pipeline. It creates new databases
            # from the smoothed NDVI and then forecasts this new database.
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            #Activate class to create time series
            create_time_series = \
                Aggregate.aggregate_time_series(smoothed_NDVI,
                                                shapefile_filepath,
                                                create_new_time_series,
                                                name_of_shapefile_column)
                
            # Run time series creation algorithm
            create_time_series.open_files()
    
            
            # Grab name of shapefile as this is will be the name of the database.
            database_name= shapefile_filepath.split('.shp')[0].split('\\')[-1]
    
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # Activate class
            create_hindcasts = Hindcasts.hindcast(database_name)
            #Create Hindcasts
            create_hindcasts.open_dataset()
    
            
            #Create forecasts
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            create_the_forecasts = Forecast.forecast(database_name,
                                                      shapefile_filepath,
                                                      name_of_shapefile_column)
            
            create_the_forecasts.open_dataset()
        else:    
            # This is the last option. It appends on new data to a database (again,
            # dictated by what the shapefile is called.)
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            
            # The code below is used to open a database, check what the last saved
            # date was. This then allows us to grab the 'new' NDVI files.
            
            shapefile_name = shapefile_filepath.split('.shp')[0].split('\\')[-1]
            main_database = h5.File((Database_path+shapefile_name+'.h5'),'r') 
            database_keys = list(main_database.keys())
            last_known_processed_date = main_database[database_keys[0]][:-10,0][-1]
            main_database.close()
            
            new_unformatted_dates = [int(file.split('dekadal.')[1].split('.tif')
                                          [0]) for file in unsmoothed_NDVI]
            
            new_data_mask = new_unformatted_dates > last_known_processed_date
            
            new_dates = np.array(new_unformatted_dates)[new_data_mask].tolist()
            
            new_NDVI_files = np.array(unsmoothed_NDVI)[new_data_mask].tolist()
            
            database_name= shapefile_filepath.split('.shp')[0].split('\\')[-1]
            
            smoothed_NDVI = sorted(glob(smoothed_NDVI_filepath+'\\*.tif'))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
             
            # Now we know what the new files are we can check if there actually are
            # any. If there isn't any, just create some forecasts based on the 
            # current data. If there are some, the next if statement checks to see
            # if that data has already been smoothed or not. If it has move on to
            # the aggregation phase, if it hasn't smooth the new data. when smoothing
            # the new data the LAST YEAR of data before the new data is also used.
            
            if len(new_NDVI_files) != 0:
                
                if len(smoothed_NDVI) < len(unsmoothed_NDVI):
    
            
                    for_smoothing = (unsmoothed_NDVI[-36-len(new_NDVI_files):
                                                     -len(new_NDVI_files)] +
                                     new_NDVI_files)
                                     
                    
                    
                    
                    whittaker_smoothing.run_smoothing(for_smoothing,True,
                                                      len(new_NDVI_files))
        
        
                # This follows the same process as above. It simply gets the newly
                # smoothed data.
                smoothed_NDVI = sorted(glob(smoothed_NDVI_filepath+'\\*.tif'))
                
                new_unformatted_dates = [int(file.split('Smoothed')[1].split('.tif')
                                              [0]) for file in smoothed_NDVI]
                
                new_data_mask = new_unformatted_dates > last_known_processed_date
                
                new_dates = np.array(new_unformatted_dates)[new_data_mask].tolist()
                
                new_smoothed_NDVI = np.array(smoothed_NDVI)[new_data_mask].tolist()
                
                
                create_time_series = \
                    Aggregate.aggregate_time_series(new_smoothed_NDVI,
                                                    shapefile_filepath,
                                                    create_new_time_series,
                                                    name_of_shapefile_column)
                    
                    
                  
                create_time_series.open_files()
         
            
                create_the_forecasts = Forecast.forecast(database_name,
                                                          shapefile_filepath,
                                                          name_of_shapefile_column)
                
                create_the_forecasts.open_dataset()
                
            else:
                
                create_the_forecasts = Forecast.forecast(database_name,
                                                          shapefile_filepath,
                                                          name_of_shapefile_column)
                
                create_the_forecasts.open_dataset()
       
       # Throughout the process some files are stored in output check so that you 
       # can see where the program has progressed to without using a console etc.
       
        shutil.rmtree('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Output_check')
    
        os.mkdir('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Output_check')
    
    
    
if __name__ == "__main__":
    main()