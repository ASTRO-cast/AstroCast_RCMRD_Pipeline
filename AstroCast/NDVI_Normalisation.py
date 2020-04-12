# -*- coding: utf-8 -*-
""" Class containing functions that find the min and max for each pixel.

This class takes the input of a list of file paths for NDVI tif images. 
It will then take these images, and for each time step (each of the 36 dekadals)
the minimum and the maximum will be found for each pixel accross all years.
This data will then be dumped to a file so that it can be read later.

Created on Thu Mar 12 10:08:43 2020 @author: Andrew Bowell
"""

# Importing the needed modules

import rasterio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from glob import glob
import pandas as pd




class NDVI_normalisation:
    """Class that finds the min/max of each pixel at each timestep.


    Attributes
    ----------
    
    files : :obj:`NumPy array` of :obj:`object`
        Array of file paths to NDVI tif data
    timesteps : :obj:`list` of :obj:`str`
        List of different timesteps (e.g each dekadal) format of %m%d e.g 0101
    NDVI : :obj:`2-D NumPy array` of :obj:`float`
        NDVI data read in from tif file
    maxes : :obj:`2-D NumPy Array` of :obj:`float`
        Max value for each pixel computed for each timestep using the numpy
        fmax function. NaNs are ignored.
    mins : :obj:`2-D Numpy array` of :obj:`float`
        min value for each pixel computed for each timestep using the numpy
        fmin function. NaNs are ignored.
    timestep : str
        Singular timestep in format of %m%d e.g 0101

    """    
    
    def __init__(self,NDVI_file_list):
        """Initiate the attributes.
        
        Some small computations in here to make sure data is in the format 
        needed
        
        Note
        ----
        Numpy arrays created as type object so strings can be stored
        
        Parameters
        ----------
        NDVI_file_list : :obj:`List` of :obj:`string`
            List of filepaths for the NDVI tif files.
        
        """
        
        self.files = np.array(NDVI_file_list,dtype=object)[:684]
        self.timesteps = [path.split('dekadal.')[1].split('.tif')[0][4:8]
                          for path in self.files[:36]]
        self.NDVI = None
        self.maxes = None
        self.mins = None
        self.timestep = None

    
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
             self.NDVI = np.insert( self.NDVI,0,
                                   np.nan, axis=0)
            
        for x in range(6):
             self.NDVI = np.insert(self.NDVI,
                                   len( self.NDVI[:,0]),
                                   np.nan, axis=0)
            
        for y in range(5):
             self.NDVI = np.insert( self.NDVI,0, np.nan, 
                                   axis=1)
            
        for y in range(5):
             self.NDVI = np.insert( self.NDVI,
                                   len( self.NDVI[0,:]),
                                   np.nan, axis=1)    
             
             

                                        
        
    def save_file(self):
        """Small function that saves the min/max arrays to a file.
    
        Not much to mention here, the files are saved with the name being the
        timestep (E.g. The dekadal, 0101 or 1221 for example). This is so that 
        the data can then be retreived  at a later date and used to create VCI
        from the NDVI.
        
        This function does not return anything, but does update the mins and 
        maxes attribute.
        
        Returns
        -------
        None.
    
        """        
        self.mins.dump('..\\..\\..\\Data\\Min_Max_Pixels2\\Min_'+
                     str(self.timestep))
        self.maxes.dump('..\\..\\..\\Data\\Min_Max_Pixels2\\Max_'+
                     str(self.timestep))
        print(self.timestep, ' file has been created')
                

    def normalise(self):
        """The function calculates the min and maxes for each pixel.
            
        The function iterates through each timestep (dekadal) and compares it 
        with the name of the file. If the name of the file matches that of the
        time step it is included in the min and max calcualtion. This is 
        repeated for each timestep. The function relies on rasterio to open
        the raw NDVI file and read it, then the NumPy fmax/fmin function is
        used to find the min and maxes. 
        
        This function does not return anything but does call the save_file
        function to save the file.
        
        Returns
        -------
        None.
    
        """
    
        for self.timestep in self.timesteps:
            for number,file in enumerate(self.files):
                date = file.split('dekadal.')[1].split('.tif')[0][4:8]
                if str(self.timestep) in str(date):
               
                    self.NDVI=rasterio.open(file).read(1)


                    self.NDVI = np.ma.array(np.where(self.NDVI <= 0.000001,
                                                     np.nan,self.NDVI))
                    
                    if number == 0:
                        self.maxes = self.NDVI
                        self.mins = self.NDVI
                        
                    else:
                        if int(file.split('dekadal.')[1].split('.tif')[0][0:4]\
                               )  >= 2019:
                            
                            self.change_file_size()
                            
                            self.maxes = np.fmax(self.maxes, self.NDVI)
                            self.mins = np.fmin(self.mins,self.NDVI)
                             
                        else:   
                            self.maxes = np.fmax(self.maxes, self.NDVI)
                            self.mins = np.fmin(self.mins,self.NDVI)
                    
                    print(file.split('dekadal.')[1],' is done')
            
            self.save_file()
             

                    
