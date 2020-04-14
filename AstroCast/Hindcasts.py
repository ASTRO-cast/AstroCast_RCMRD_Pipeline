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
import matplotlib.pyplot as plt
#import GaussianProcesses


class hindcast:
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
    def __init__(self,database_path):
        """Initiate the attributes.
        
        Parameters
        ---------
        database_path : str
            Path to the HDF5 file that contains all of time series.

        """
        self.database = database_path
        self.file =  None
        self.hindcast_results =  None
        self.database_file = None
        self.data_halfway_point = None

    
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
    
    
    def create_hindcast(self):
        """ Function to run the hindcasts
        
        This function is structured in a way similiar to that of the forecasts.
        The way this function differs is that the data is first split in half. 
        The first half of the data is used to train the model and then 
        forecasts are performed, incrementing one dekadel at a time. This data
        is then saved to the master file where the create PDF file can open it 
        up and calcualte the errors for the reports.

        Returns
        -------
        None.

        """
        raw_to_datetime_Vec = np.vectorize(self.raw_to_datetime)

        
        dataset_names = list(self.file.keys())
        
        data_length =int(len(self.file[dataset_names[0]][:,0]))
        
        self.data_halfway_point = int(data_length/2)
        
        self.hindcast_results =  np.full((data_length-
                                          self.data_halfway_point+10,10),0.0)
        
        
        for dataset_no,dataset in enumerate(dataset_names):
            
            self.database_file = self.file[dataset]
                
            for run_counter,hindcast_counter in \
                enumerate(range(self.data_halfway_point,data_length)):
      
                dataset_array = np.array(self.database_file,
                                         dtype=float)[:hindcast_counter]
              
                dataset = dataset.replace("?","")
                
                dates = raw_to_datetime_Vec(dataset_array[:,0])
            
                days = np.array([(date-dates[0]).days for date in dates])
                
                nan_mask = np.isnan(dataset_array[:,3])
                
                VCI = dataset_array[:,3][~nan_mask]
                
                days = days[~nan_mask]
                
                dates = dates[~nan_mask]

                
                predicted_days,predicted_VCI3M = \
                    GaussianProcesses.forecast(days,VCI)
                    
                    
                predicted_dates = [dates[0] + timedelta(days=day) for day in 
                                   predicted_days]

                unformatted_dates = [float(date.strftime('%Y%m%d')) for 
                                     date in predicted_dates]

                for save_counter in range(0,10):

                    self.hindcast_results[run_counter+save_counter,
                                          save_counter] = \
                        predicted_VCI3M[-10+save_counter]
      

                print(hindcast_counter,'out of',data_length)     
                
            self.save_the_data()

            
    def save_the_data(self):
        """Small function that saves the hindcast data to HDF
        
        This function resizes the dataset so that the different hindcast data
        can be stored to HDF. The column attributes are also updated so that 
        the file can be easily read. 
        
        Returns
        -------
        None.

        """
        
        self.database_file.resize(len(self.database_file)+10,axis=0)
        self.database_file.resize(14,axis=1)
        self.database_file.attrs['Column_Names'] = ['Date',
                                          'NDVI','VCI',
                                          'VCI3M','0 lag time',
                                          '10 day lag time',
                                          '20 day lag time','30 day lag time',
                                          '40 day lag time','50 day lag time',
                                          '60 day lag time','70 day lag time',
                                          '80 day lag time','90 day lag time'] 
        
        self.database_file[self.data_halfway_point:,4:] =self.hindcast_results
                                         
        print(self.database_file)
          

            
            
    def open_dataset(self):
        """This function opens the HDF5 dataset and closes it once done.
        
        Returns
        -------
        None.

        """
        self.file = h5.File((self.database+'.h5'), 'a')     
        self.create_hindcast()
        self.file.close()
            
