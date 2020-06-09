# -*- coding: utf-8 -*-
""" This module handles the preperation of the data before the GP.

The entire purpose of this module is to prepare the data into the foremat 
needed for the GP to handle.

Created on Mon Apr  6 17:59:53 2020

@author: Andrew Bowell 
"""

import h5py as h5
import numpy as np
from datetime import datetime,timedelta

import CreatePDF
import GaussianProcesses


class forecast:
    """Class that houses the functions needed to convert the data
    
    Attributes
    ----------
    databse : str
        Path to the HDF5 file that contains all of time series.
    file : HDF5 datareader
        Contains the contents of the HDF5 file. Each dataset must then be read 
        from this.
    shapfile_path : str
        The path to the shapefile needed to create the reports
    """
    def __init__(self,database_path,shapefile_path,name_of_shapefile_column):
        """Initiate the attributes.
        
        Parameters
        ---------
        database_path : str
            Path to the HDF5 file that contains all of time series.
        shapfile_path : str
            The path to the shapefile needed to create the reports
        name_of_shapefile_column : str
            The column of the shapefile that will be used. E.g name of each 
            county or the region ID. 
    
        """
        self.database = database_path
        self.file =  None
        self.shapefile_path = shapefile_path
        self.column_name = name_of_shapefile_column
    
    def raw_to_datetime(self,unformatted_date):
        """Convert raw string date to datetime

        Parameters
        ----------
        unformatted_date : str
            Date in unformatted form of %Y%m%d

        Returns
        -------
        datetime
            Python datetime version of the unformatted date entered

        """
        
        return datetime.strptime(str(int(unformatted_date)), '%Y%m%d')
    
    
    def create_forecast(self):
        """ Function to create the forecast
        
        This function grabs the dataset names from the HDF5 file and loops over
        them, opening each dataset, masking any NaN elements (NaNs cannot be 
        passed into the GP function) and then masking the days that these
        NaN values occur on too. The dates are also converted into days since
        the first measurement (Julian calender).
        
        Once the forecast has been created the reports are created by calling
        a seperate module. (This module structure could change in the future)
        

        Returns
        -------
        None.

        """

        
        raw_to_datetime_Vec = np.vectorize(self.raw_to_datetime)

        
        dataset_names = list(self.file.keys())
        
        
        for dataset_no,dataset in enumerate(dataset_names):
        
            dataset_array = np.array(self.file[dataset],dtype=float)

          
            #dataset = dataset.replace("?","")
            

            
            zero_mask = np.isnan(dataset_array[:-10,0])
            
            
            
            dates = raw_to_datetime_Vec(dataset_array[:-10,0])
            
            
        
            days = np.array([(date-dates[0]).days for date in dates])
            
            nan_mask = np.isnan(dataset_array[:-10,3])
            
            VCI = dataset_array[:-10,3][~nan_mask]
            
            days = days[~nan_mask]
            
            dates = dates[~nan_mask]
            
            predicted_days,predicted_VCI3M = GaussianProcesses.forecast(days,
                                                                         VCI)
            predicted_dates = [dates[0] + timedelta(days=day) for day in \
                                                               predicted_days]

            create_report = CreatePDF.createPDF(dataset,dataset_no,
                                                predicted_dates,
                                                predicted_VCI3M,dates[-1],
                                                self.shapefile_path,
                                                self.database,
                                                self.column_name)    

            create_report.error_calc()
            
    def open_dataset(self):
        """This function opens the HDF5 dataset and closes it once done.
        
        Returns
        -------
        None.

        """
        self.file = h5.File(('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Databases\\'+self.database+'.h5'), 'r+')     
        self.create_forecast()
        self.file.close()
            
        
        
 
    
