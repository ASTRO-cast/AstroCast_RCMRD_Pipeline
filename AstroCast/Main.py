# -*- coding: utf-8 -*-
"""This is the main body and will run through each pipeline step.


Created on Sat Apr 11 14:19:35 2020
@author: Andrew

"""

from glob import glob
import h5py as h5
import numpy as np
import sys

import NDVI_Normalisation
import NDVI_to_VCI
import VCI_To_VCI3M
import Aggregate
import Forecast


def are_you_sure(create_new_time_series):
    if create_new_time_series:
        if input('Are you sure you want to create a new time series? Hit y ')\
            != 'y':
            are_you_sure(create_new_time_series)            


def main():

    
    #~~~~~~~~~~~~~~~~~~~~~~~For user to define~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    create_new_time_series = True
    
    convert_NDVI_from_scratch = True
    
    calibrate_errors = True 
    
    shapefile_filepath = '..\\CountyShapes\\County.shp'
    
    
    NDVI_filepath = '..\\..\\..\\Data\\Raw_Data\\'
    
    VCI_filepath = '..\\..\\..\\Data\\Processed_Data2\\RCMRD_VCI\\'
    
    VCI3M_filepath = '..\\..\\..\\Data\\Processed_Data2\\RCMRD_VCI3M\\'
    
    Database_path = 'County'
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    # Make sure user wants a new time series. This can take a long time. and y
    
    # it will also overwrite any previous data.
    
    are_you_sure(create_new_time_series)

    shapefile_name = shapefile_filepath.split('.shp')[0].split('\\')[-1]
    
    
    if create_new_time_series and convert_NDVI_from_scratch:
        
        NDVI_file_list = glob(NDVI_filepath+'\*.tif')
        
        unformatted_dates = [int(file.split('dekadal.')[1].split('.tif')
                                     [0]) for file in NDVI_file_list]
        

        
        # Find min/max for every pixel
        
        Nomalise_NDVI = NDVI_Normalisation.NDVI_normalisation(NDVI_file_list)
        # Nomalise_NDVI.normalise()
        
        # Use the min/max for each pixel to convert to pixel VCI
        
        NDVI_VCI = NDVI_to_VCI.convert_NDVI_to_VCI(NDVI_file_list,
                                                  unformatted_dates)
        
        # NDVI_VCI.read_and_store_data()
        
        VCI_file_list= glob(VCI_filepath+'\*.tif')
        
        VCI_VCI3M = VCI_To_VCI3M.convert_VCI_to_VCI3M(VCI_file_list)
        
        # VCI_VCI3M.populate_average_list()
        
        VCI3M_file_list = glob(VCI3M_filepath+'\*.tif')
        
        
        create_time_series = \
            Aggregate.aggregate_time_series(NDVI_file_list,
                                            VCI_file_list,
                                            VCI3M_file_list,
                                            shapefile_filepath,
                                            create_new_time_series)
            
        #create_time_series.open_files()
        
        database_name= shapefile_filepath.split('.shp')[0].split('\\')[-1]
        
        
        
        create_the_forecasts = Forecast.forecast(database_name,
                                                 shapefile_filepath)
        
        create_the_forecasts.open_dataset()
        
        
    elif create_new_time_series is True and convert_NDVI_from_scratch is False:
        
        NDVI_file_list = glob(NDVI_filepath+'\*.tif')
        VCI_file_list= glob(VCI_filepath+'\*.tif')       
        VCI3M_file_list = glob(VCI3M_filepath+'\*.tif')

        create_time_series = \
            Aggregate.aggregate_time_series(NDVI_file_list,
                                            VCI_file_list,
                                            VCI3M_file_list,
                                            shapefile_filepath,
                                            create_new_time_series)
        
        create_time_series.open_files()
        
        database_name= shapefile_filepath.split('.shp')[0].split('\\')[-1]

        
        

        
        
        create_the_forecasts = Forecast.forecast(database_name,
                                                 shapefile_filepath)
        
        create_the_forecasts.open_dataset()
        
        
    else:    
        
        shapefile_name = shapefile_filepath.split('.shp')[0].split('\\')[-1]
        main_database = h5.File((shapefile_name+'.h5'),'r') 
        database_keys = list(main_database.keys())
        last_known_processed_date = main_database[database_keys[0]][:,0][-1]
        main_database.close()
        
        
        # Find all filepaths to tif NDVI data and use list comprehension to 
        # extract date from each
        
        NDVI_file_list = glob(NDVI_filepath+'\*.tif')
        
        
        new_unformatted_dates = [int(file.split('dekadal.')[1].split('.tif')
                                     [0]) for file in NDVI_file_list]
        
        
        # Check if the data is newer than previous data, create mask and only use new data
        
        new_data_mask = new_unformatted_dates > last_known_processed_date
        
        new_dates = np.array(new_unformatted_dates)[new_data_mask].tolist()
        
        new_NDVI_files = np.array(NDVI_file_list)[new_data_mask].tolist()
        
        
        # If there is no new data the system will exit
        if len(new_NDVI_files) == 0:
            user_input =input('No new files, would you like to create'
                               'a forecast still? If so press y')
             
            if user_input == 'y':
                
                database_name= (shapefile_filepath.split('.shp')[0]
                                .split('\\')[-1])
        
                create_the_forecasts = Forecast.forecast(database_name,
                                                 shapefile_filepath)
        
                create_the_forecasts.open_dataset()
                
            else:
                
                sys.exit('There are no new files, the program will now exit')
        
        
        NDVI_VCI = NDVI_to_VCI.convert_NDVI_to_VCI(new_NDVI_files, new_dates)
        
        NDVI_VCI.read_and_store_data()
        
        VCI_file_list= glob(VCI_filepath+'\*.tif')    
        
        VCI_data_mask = new_data_mask.copy()

        new_data_count = np.count_nonzero(new_data_mask)
        
        # This is the line that adds the extra 8 data points before the most recent
        VCI_data_mask[-new_data_count-8:-new_data_count] = [True] * (
            len(VCI_data_mask[-new_data_count-8:-new_data_count]))
        
        
        new_VCI_files = np.array(VCI_file_list)[VCI_data_mask].tolist()
        
        
        VCI_VCI3M = VCI_To_VCI3M.convert_VCI_to_VCI3M(new_VCI_files)

        VCI_VCI3M.populate_average_list()
        
        VCI3M_file_list = glob(VCI3M_filepath+'\*.tif')
        
        
        
        create_time_series = \
            Aggregate.aggregate_time_series(NDVI_file_list,
                                            VCI_file_list,
                                            VCI3M_file_list,
                                            shapefile_filepath,
                                            create_new_time_series)
            
        create_time_series.open_files()
        
        create_the_forecasts = Forecast.forecast(database_name,
                                                 shapefile_name)
        
        create_the_forecasts.open_dataset()
        
    
    

    
    
if __name__ == "__main__":
    main()