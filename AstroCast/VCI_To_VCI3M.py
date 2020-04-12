# -*- coding: utf-8 -*-
"""Module used for converting VCI into VCI3M.

The class within this module completes moving average of 9 VCI tif files.
As the tif files are stored in dekadals, 9 tif images will cover the duration 
of 90 days (3 months). This index is used by various organisations as an 
indicator of drought. These images will eventually be aggregated to some level
and the GP code run on it to forecast how it will change over time.
 
Created on Tue Mar 24 15:09:55 2020

@author: Andrew Bowell

"""

import numpy as np
import rasterio 
from glob import glob




class convert_VCI_to_VCI3M:
    """Class that houses the functions for the VCI to VCI3M averaging.
    
    The main bulk of the code will be the moving average.
    
    Attributes
    ----------
    files : :obj:`List` of :obj:`str`
        List of file paths to the VCI tif data
    average_list : :obj:`list` of :obj:`NumPy array`
        A list that will have 9 VCI images in at once. This will allow the 
        calculation of the last 90 days of VCI3M at any given timestep.
    out_meta : :obj:`Dictionary` of :obj:`str`
        Contains different data about the tif file including projection,dtype,
        fill value and more.
    VCI3M : :obj:`NumPy array` of :obj:`float`
        2-D array that contains the averaged 90 days of VCI for the given 
        timestep.
    date : str
        The unformatted (%Y%m%d) date the data was taken on E.g 20010101
    VCI : :obj:`NumPy array` of :obj:`float`
        The data that is read in by rasterio from th VCI file.
    
    
    """
    
    def __init__(self,File_List):
        
        """Defining some attributes.
        
        The sole purpose of __init__ is to initialize values that will be
        needed.
        
        Parameters
        ----------
        File_List : :obj:`List` of :obj:`str` 
            List of filepaths for NDVI raw files
        
        """
        self.files = File_List
        self.average_list = []
        self.out_meta = None
        self.VCI3M = None
        self.date = None 

        self.VCI = None
        
    def read_meta_data(self):
        """Reading the VCI metadata
            
        Function does not return anythign but updates the out_meta attribute.
        
        Returns
        -------
        None.
        """
     
        the_meta_data = rasterio.open(self.files[0])
    
        self.out_meta  = the_meta_data.meta.copy()
        
        
        
    def store_data(self):
        """Storing the calculated VCI3M data into a tif
 
        This function doesn't reutrn anything but does use rasterio to write
        a new tif file.
        
        Returns
        -------
        None.
 
        """
        with rasterio.open('..\\..\\..\\Data\\Processed_Data2\\RCMRD_VCI3M\\'
                           +self.date+'.tif', "w",**self.out_meta) as dest:
             dest.write(np.expand_dims(self.VCI3M,axis=0))
         
        print('VCI3M for ',self.date, ' has now been created')
        

    
    def populate_average_list(self):
        """Load data into the list that will be used to average the VCI.
        
        This function is soley responsible for the first 9 files that are 
        loaded into the class. As we need 9 files to create the average for 
        the VCI3M the first 8 images solely contribute towards the mean. The 
        9th image is then the last one to contribute and is then saved under 
        the 9th images' name.
        
        
        This function does not return anything but does call the next function
        aswell as updating the average_list and VCI attributes.
        
        Returns
        -------
        None.    
        """
        self.read_meta_data()
        
        for i in range(0,9):
            
            self.date = self.files[i].split('RCMRD_VCI\\')[1].split('.tif')[0]
    
            if int(self.date[:4]) >= 2019:
                
                self.VCI = rasterio.open(self.files[i]).read(1)
                
                self.average_list.append(self.VCI)
                                         
            else:
                self.average_list.append(rasterio.open(self.files[i]).read(1))
                
                

        self.VCI3M = np.nanmean(np.array(self.average_list),axis =0)
        
        self.store_data()
        
        self.create_VCI3M()
        
        
        
            
    def create_VCI3M(self):
        """This function performs the moving average.
        
        After the inital 9 files have been added onto the list and averaged,
        this function continues to read in the new images one by one and 
        append each one onto the end, popping the first image (oldest image
        chronologically) out of the list and then taking the new average.
        This allows the pipeline to calculate what the VCI3M is at each time
        step. Again, due to t he file size changing, there is currently a 
        quick check to find what year the data is from. If it is from 2019 the
        change_file_size function is called.
        
        This function does not return anythign but once the average has been 
        calculated, the VCI3M attribute is updated and then the store data
        function is called.
        
        Returns
        -------
        None.
        
        """
        for i in range(9,len(self.files)):
            
            self.date = self.files[i].split('RCMRD_VCI\\')[1].split('.tif')[0]
            
            self.average_list.pop(0)
            
            self.VCI = rasterio.open(self.files[i]).read(1)
            
            if int(self.date[:4]) >= 2019:
                
                self.change_file_size()
                
                self.average_list.insert(-1,self.VCI)
                
            else:
                
                self.average_list.insert(-1,self.VCI)
            
            
            self.VCI3M = np.nanmean(np.array(self.average_list),axis =0)
            
            self.store_data()
    

        
                
    def change_file_size(self):
        """Small function that inserts Nans into the data.
        
        Hopefully this will be removed in future releases. from 2001-2018 the
        file size stays consitent, but in 2019 the size of the files drop by
        13 rows and 10 columns. This function just inserts NaNs round the edges
        of the NDVI file to make it the same size. The numpy.insert function 
        is used to perform this operation.
        
        This function does not return anything, but does update the NDVI 
        attribute.
        
        Returns
        -------
        None.
   
        """
        for x in range(7):
             self.VCI = np.insert(self.VCI,0,
                                   np.nan, axis=0)
            
        for x in range(6):
             self.VCI = np.insert(self.VCI,
                                   len(self.VCI[:,0]),
                                   np.nan, axis=0)
            
        for y in range(5):
             self.VCI = np.insert(self.VCI,0, np.nan, 
                                   axis=1)
            
        for y in range(5):
             self.VCI = np.insert(self.VCI,
                                   len(self.VCI[0,:]),
                                   np.nan, axis=1)    
                                        
        

        
      
     
