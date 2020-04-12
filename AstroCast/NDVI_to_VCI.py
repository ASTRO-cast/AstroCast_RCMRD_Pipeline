# -*- coding: utf-8 -*-
""" Class containing functions that convert NDVI tif images to VCI

This module takes an input of a file path and an unformatted date.
A class is then used to house several functions that break the code
down into small, simple chunks. First, the raw data is read, followed
by the data for the mins and maxes of each pixel. The VCI is then 
calculated using said data and then saved into it's own tif file.

Created on Thu Mar 12 12:05:50 2020
@author: Andrew Bowell

"""
# Importing modules needed

import numpy
from glob import glob
import numpy as np
import rasterio


class convert_NDVI_to_VCI:
    """This class is used to convert the NDVI tif to a VCI tif.
    
    A file path and an unformatted date, which can be extracted from the
    file path should be passed into this function when it is initialized.
    This class was built to use dekadal NDVI data from RCMRD.
    
    Attributes
    ----------
    
    file_paths : :obj:`List` of :obj:`str` 
        List of filepaths for NDVI raw files
    dates : :obj:`list` of :obj:`str`
        List of dates in the format of %Y%m%d e.g 20200101
    NDVI : :obj:`NumPy masked array` of :obj:`float32`
        2-D NumPy masked array containing float32 values. 
    meta_data : :obj:`Dictionary` of :obj:`str`
        Contains different data about the tif file including projection,dtype,
        fill value and more.
    maxes : :obj:`NumPy array` of :obj:`float`
        Contains max values for each  pixel at each timestep. 
    mins : :obj:`NumPy  array` of :obj:`float` 
        Contains min values for each pixel at each timestep. 
    VCI : :obj:`NumPy array` of :obj: `float32`
        Contains the VCI for each pixel in the type float32 so that it can be
        stored along with the standard metadata
            
    """
    def __init__(self,file_paths,unformatted_dates):
        """Defining some attributes.
        
        The sole purpose of __init__ is to initialize values that will be
        needed.
        
        
        Parameters
        ----------
        file_paths : :obj:`List` of :obj:`str` 
            List of filepaths for NDVI raw files
        unformatted_dates : :obj:`list` of :obj:`str`
            List of dates in the format of %Y%m%d e.g 20200101
        
        """
        self.file_paths = file_paths
        self.dates = unformatted_dates
        self.NDVI  = None
        self.meta_data = None
        self.maxes = None
        self.mins = None
        self.VCI = None
        self.date = None
        
    def read_and_store_data(self):
        """Open tif file extract data and meta data.
        
        Use a module called rasterio to open the raster in the tif file at the
        target file path. Numpy is then used to get rid of any NDVI values 
        that are/around 0 so that cloud cover is eliminated. A copy of the 
        meta data is also saved.
        
        This function does not return anything, but does update the meta_data
        attribute,NDVI attribute, the date attribute and then calls the 
        read_min_max function so that the NDVI that has just been read can be 
        converted into VCI.
        
        Returns
        -------
        None.
        
        """
        for file,date in zip(self.file_paths,self.dates):
            
            NDVI = rasterio.open(file).read(1) # 1 is the target raster
            
            self.NDVI = np.ma.array(np.where(NDVI <= 0.000001, np.nan, NDVI)
                                    ,dtype='float32')
            
            self.meta_data=rasterio.open(file).meta.copy()
                        
            self.date = date         
            
            self.read_min_max()
            
                              
            

            
    def read_min_max(self):
        """Load in min and max values for each pixel.
        
        Using NumPy load in dumped masked arrays that contain the minimum 
        and maximum for each pixel. allow_pickle must be true and the type
        must be kept as float32 as when saved with the original metadata that
        is the type specified.
        
        This function does no return anything but instead updates the mins and
        maxes attributes and then calls the functions that calculates the VCI.
        
        Returns
        -------
        None.
        
        """
        self.maxes = np.array(np.load('..\\..\\..\\Data\\Min_Max_Pixels\\Max_'
                                      + str(self.date)[4:],allow_pickle=True),
                                      dtype='float32')
        
        self.mins =  np.array(np.load('..\\..\\..\\Data\\Min_Max_Pixels\\Min_'
                                      + str(self.date)[4:],allow_pickle=True),
                                      dtype='float32')
        
        self.calc_vci()
        
        
    def calc_vci(self):
        """ Calculate the VCI for each pixel.
        
        The VCI is calculated from the NDVI and the mins/maxes for each pixel.
        
        Nothing is returned form this function. The VCI attribute is updated
        and the save_data fnuction is called.

        Returns
        -------
        None.

        """
        
        if int(str(self.date)[0:4]) >= 2019:
            self.VCI = 100*((self.NDVI-self.mins[6:-7,5:-5])
                            /(self.maxes[6:-7,5:-5]-self.mins[6:-7,5:-5]))
            
        else:
            
            self.VCI = 100*(self.NDVI-self.mins)/(self.maxes-self.mins)
        
        self.save_data()
        
        
    def save_data(self):    
        """Write the resultant VCI data to a tiff
        
        Reshape the VCI so it has one extra dimention, this is to specifiy the
        raster. Then using rasterio, save the data with the meta data from the
        original file
        
        Nothing is  returned from this function and only the VCI attribute is 
        changed slightly so that it can be saved to a file.
        
        Returns
        -------
        None.
        """
        self.VCI= self.VCI.reshape((1,)+self.VCI.shape)

        with rasterio.open('..\\..\\..\\Data\\Processed_Data2\\RCMRD_VCI\\'+
                           str(self.date)+'.tif', "w",**self.meta_data)\
                           as dest:
                                    
            dest.write(self.VCI)
        print(self.date, ' has been written to tif')
        
