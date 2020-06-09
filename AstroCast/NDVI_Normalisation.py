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
        
        self.files = np.array(NDVI_file_list,dtype=object)[:648]
        self.timesteps = [path.split('\\')[-1].split('.tif')[0][12:]
                          for path in self.files[:36]]
        self.NDVI = None
        self.maxes = None
        self.mins = None
        self.timestep = None#
        self.meta_data = rasterio.open(self.files[0]).meta.copy()

        
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

        with rasterio.open('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Min_Max_Pixels\\Min_'+ str(self.timestep)+\
                           '.tif', "w",**self.meta_data) as dest:
                                    
           dest.write(self.mins,1)
           
        with rasterio.open('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Min_Max_Pixels\\Max_'+str(self.timestep)+\
                          '.tif', "w",**self.meta_data) as dest:
                                    
           dest.write(self.maxes,1)
           
           
        print(self.timestep, ' has been written to tif')
                

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
                date = file.split('\\')[-1].split('.tif')[0][12:]
                if str(self.timestep) in str(date):
               
                    self.NDVI=rasterio.open(file).read(1)


                    #self.NDVI = np.ma.array(np.where(self.NDVI <= 0.000001,
                                                   #  np.nan,self.NDVI))
                    
                    if number == 0:
                        
                        self.maxes = self.NDVI
                        self.mins = self.NDVI
                        
                    else:

                        self.maxes = np.fmax(self.maxes, self.NDVI)
                        self.mins = np.fmin(self.mins,self.NDVI)
                    
                    print(file.split('\\')[-1],' is done')
            
            self.save_file()
             

                    
