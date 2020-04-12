
# -*- coding: utf-8 -*-
"""Module used for create timeseries of NDVI,VCI and VCI3M

This module is designed to take in a shapefile and create individual timeseries
for each shape in the file. An example use would be using the counties of Kenya
but it would be equally valid to just have a shapefile of the country and 
create a time series for the whole country. This module also handels any
cloud coverage too.

Created on Mon Apr  6 13:46:02 2020

@author: Andrew Bowell

"""
# Import modules needed 

import numpy as np
import rasterio
import geopandas as gpd
import json
from rasterio.mask import mask
from glob import glob
import h5py as h5



class aggregate_time_series:
    """Class that houses the functions to aggregate and create timeseries
    
    
    Attributes
    ----------
    NDVI_files : :obj:`List` of :obj:`str`
        List of filepaths for the NDVI tif files.
    VCI_files : :obj:`List` of :obj:`str`
        List of filepaths for the VCI tif files.
    VCI3M_files : :obj:`List` of :obj:`str`
        List of filepaths for the VCI3M tif files.
    shapefile_path : str
        Filepath to the shapefile that is to be used
    new : bool
        Whether or not a new time series is to be created
    shapefile_data : :obj:`Geopandas dataframe` of :obj:`object`
        Shapefile data is read in and converted to the same scale as the tif
        images.
    datasets : :obj:`List` of :obj:`str`
        List of the names of each shape. This is so that when the data is saved
        to the database, each dataset is created with its name.
    final_array : :obj:`NumPy array` of :obj:`float`
        This array contains, for each shape, the date and the mean NDVI,VCI
        and VCI3M over the specified areal.
    raw_NDVI : :obj:`NumPy array` of :obj:`float`
        NumPy array of the raw NDVI read in from the file by rasterio
    raw_VCI : :obj:`NumPy array` of :obj:`float`
        NumPy array of the raw VCI read in from the file by rasterio
    raw_VCI3M : :obj:`NumPy array` of :obj:`float`
        NumPy array of the raw VCI3M read in from the file by rasterio
    NDVI : :obj:`NumPy array` of :obj:`float`
        NumPy array of the cropped NDVI
    VCI : :obj:`NumPy array` of :obj:`float`
        NumPy array of the cropped VCI
    VCI3M: :obj:`NumPy array` of :obj:`float`
        NumPy array of the cropped VCI3M
    final_NDVI : :obj:`NumPy array` of :obj:`float`
        The final NumPy masked array of the cropped NDVI after cloud coverage
        etc has been taken out.
    final_VCI : :obj:`NumPy array` of :obj:`float`
        The final NumPy masked array of the cropped VCI after cloud coverage
        etc has been taken out.
    final_VCI3M : :obj:`NumPy array` of :obj:`float`
        The final NumPy masked array of the cropped VCI3M after cloud coverage
        etc has been taken out.
    date : str 
        Unformatted date %Y%m%d E.g 20090921
    date_counter : int 
        Simple loop counter. Helps with storage of data in arrays
    shape_counter : int
        Simple loop conuter, aids with sotrage of data in arrays
    
    """
    def __init__(self,NDVI_files,VCI_files,VCI3M_files,shape_file_path,new):
        """Defining some attributes.
        
        The sole purpose of __init__ is to initialize values that will be
        needed.
        
        Parameters
        ----------
        NDVI_files : :obj:`List` of :obj:`str` 
            List of filepaths for NDVI raw files
        VCI_files : :obj:`List` of :obj:`str` 
            List of filepaths for VCI raw files
        VCI3M_files : :obj:`List` of :obj:`str` 
            List of filepaths for VCI3M raw files
        shape_file_path : str
            Filepath to the shapefile that is to be used.
        new : bool
            Whether or not a new time series is to be created or an old time
            series will have data appeneded.
        
        Note
        ---- 
        Some calculations occur in the definitions of the attributes. See 
        source code
    
        """
        self.NDVI_files = NDVI_files
        self.VCI_files = VCI_files
        self.VCI3M_files = VCI3M_files
        self.shapefile_path = shape_file_path
        self.new = new
        
        
        self.shapefile_data = gpd.read_file(shape_file_path).to_crs(
                              crs=rasterio.open(self.VCI3M_files[0]).crs.data)
        
        self.datasets = [slash.replace('/', '-') for slash in
                         self.shapefile_data['Name'].tolist()]
        
        self.final_array = np.empty((len(self.datasets),len(self.VCI3M_files),
                                     4),dtype='float')
        
        
        self.raw_NDVI = None
        self.raw_VCI = None
        self.raw_VCI3M = None
        self.NDVI = None
        self.VCI = None
        self.VCI3M = None
        self.final_NDVI = None
        self.final_VCI = None
        self.final_VCI3M = None
        self.date = None
        self.date_counter = None
        self.shape_counter = None
        

        
    
    @staticmethod
    def get_features(unformatted_features):
        """ Function to grab features of shapes from shapefile
        
        Parameters
        ----------
        unformatted_features : :obj:`list` of :obj:`float`
            Data about the size/edges of the shape in the shapefile
            
        Returns
        -------
        Features and geomerty of shapefile
        
        """
        return [json.loads(unformatted_features.to_json())
                ['features'][0]['geometry']]
        
    
    def open_files(self):
        """Use rasterio to open each of the NDVI,VCI and VCI3M tifs.
        
        This functions simply loops over each filepath in each list and opens
        all three(NDVI,VCI and VCI3M). The date is also extracted from the 
        filepath and then the crop_to_shapefile function is called. Once all 
        the files ahve been open,read,cropped and aggregated the save_to_hdf
        function is called.
        
        This functio ndoes not return anything but does update the raw_NDVI,raw
        _VCI,raw_VCI3M,date and date_counter attributes
        
        Returns
        -------
        None.
        """
        for self.date_counter,(NDVI_file,VCI_file,VCI3M_file) in \
                enumerate(zip(self.NDVI_files,self.VCI_files,self.VCI3M_files)):
            
        
            self.raw_NDVI   =  rasterio.open(NDVI_file)
            self.raw_VCI    =  rasterio.open(VCI_file)
            self.raw_VCI3M  =  rasterio.open(VCI3M_file)

            self.date = VCI3M_file.split('RCMRD_VCI3M\\')[1].split('.tif')[0]
            
            self.crop_to_shapefile()
            
            
            print(self.date,' is complete')
            
        self.save_to_hdf()   


    def crop_to_shapefile(self):
        """ Use rasterio to crop the tif image to specified shape.
        
        The tif image is croped to shape using rasterio and then the null data
        is masked so that when averaged it is not included.
        
        This module does not return anything but does update various
        attributes, see source code.
            
        Returns
        -------
        None.
        
        """
        for shape_counter in range(0,len(self.datasets)):
            
            crop_boundaries=self.get_features(self.shapefile_data[self.
                                        shapefile_data.index==shape_counter])
            
            NDVI,  to_ignore = mask(self.raw_NDVI,  crop_boundaries, crop=True)
            VCI,   to_ignore = mask(self.raw_VCI,   crop_boundaries, crop=True)
            VCI3M, to_ignore = mask(self.raw_VCI3M, crop_boundaries, crop=True)
            
            
            self.NDVI   = np.ma.masked_array(NDVI)
            self.VCI    = np.ma.masked_array(VCI)
            self.VCI3M  = np.ma.masked_array(VCI3M)
            
            
            self.final_NDVI   = np.ma.masked_values(NDVI,1.175494351e-38)
            self.final_VCI    = np.ma.masked_values(VCI,1.175494351e-38)
            self.final_VCI3M  = np.ma.masked_values(VCI3M,1.175494351e-38)
            
            self.shape_counter = shape_counter

            self.check_cloud_store()
        

    def check_cloud_store(self):
        """This function checks for cloud cover
        
        In the previous processing, cloud cover had been taken out leaving the
        fill value. This function checks that when each shapefile has been 
        aggregated that it still contains more than 1% of the original data.
        If it does not, then instead of the average being inserted into the 
        time series, a NaN value is.
        
        This function does not return anyting but does update various 
        attributes, see source code.
        
        Returns
        -------
        None.
        
        """

        
        if self.final_NDVI.count()  <  self.NDVI.count()/100:
            
            self.final_NDVI  = np.nan
            
        if self.final_VCI.count()   <  self.VCI.count()/100:
            
            self.final_VCI   = np.nan
            
        if self.final_VCI3M.count() <  self.VCI3M.count()/100:
            
            self.final_VCI3M = np.nan


        self.final_array[self.shape_counter,self.date_counter,0] = self.date
        
        self.final_array[self.shape_counter,self.date_counter,1] = \
            np.nanmean(self.final_NDVI)
            
        self.final_array[self.shape_counter,self.date_counter,2] = \
            np.nanmean(self.final_VCI)
            
        self.final_array[self.shape_counter,self.date_counter,3] = \
            np.nanmean(self.final_VCI3M)
            
        
    def save_to_hdf(self):
        """This function saves the time series to HDF format.
            
        If new is true then a new HDF file will be created and the data will
        be stored there. The name of the file will be the name of the shapefile
        that was used to aggregate the data. There are four columns that are 
        saved, the date,NDVI, VCI and VCI3M. This is stored as a dataset in the
        HDF file for each shape in the shapefile.
        
        If new is false, the data is just appended into a previously created 
        timeseries database.
        
        Returns
        -------
        None.
        
        """
        
        
        if self.new:
            
            file_name = self.shapefile_path.split('.shp')[0].split('\\')[-1]
            
            storage_file = h5.File((str(file_name)+'.h5'), 'w')
            
            for dataset_counter,dataset in enumerate(self.datasets):
                
                storage_file.create_dataset(dataset,data=self.final_array
                                            [dataset_counter,:,:],
                                            compression='lzf',
                                            maxshape=(None,None))      
                             
                storage_file[dataset].attrs['Column_Names'] = ['Date',
                                                              'NDVI','VCI',
                                                              'VCI3M'] 
                
                
                                             
            storage_file.close()
            
            print('The new data has been added to the database successfully')
        
            
        else:
        
            file_name = self.shapefile_path.split('.shp')[0].split('\\')[-1]
            
            storage_file = h5.File((str(file_name)+'.h5'), 'a')
            
            for dataset_counter,dataset in enumerate(self.datasets):
                
                
                dataset = storage_file[dataset]
                
                dataset_length = len(dataset)
            
                dataset.resize(dataset_length+len(self.final_array[0,:,0]),
                               axis=0)
                dataset[dataset_length:,:] =self.final_array[dataset_counter,
                                                             :,:]
                                             
            storage_file.close()
                
            print('The new data has been added to the database successfully')

   