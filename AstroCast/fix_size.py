# -*- coding: utf-8 -*-
"""
Created on Mon May  4 12:36:10 2020

@author: Andrew
"""
import rasterio
import numpy as np
from glob import glob



def change_file_size(new_files,NDVI_filepath):
    
    if len(new_files) != 0:
        meta_data = rasterio.open(new_files[0]).meta.copy()
        
    for file in new_files:
        
        if int(file.split('.tif')[0].split('dekadal.')[-1][0:4]) >= 2017:
        
            name = file.split('.tif')[0].split('\\')[-1]
            
            NDVI = rasterio.open(file).read(1)
            print(name,file)
            if NDVI.size != 15910066:
            
                for x in range(7):
                     NDVI = np.insert(NDVI,0,
                                           1.175494351e-38, axis=0)
                    
                for x in range(6):
                     NDVI = np.insert(NDVI,
                                           len(NDVI[:,0]),
                                           1.175494351e-38, axis=0)
                    
                for y in range(5):
                     NDVI = np.insert(NDVI,0, 1.175494351e-38, 
                                           axis=1)
                    
                for y in range(5):
                     NDVI = np.insert( NDVI,
                                           len(NDVI[0,:]),
                                           1.175494351e-38, axis=1)    
                
            
                with rasterio.open((NDVI_filepath+'\\'+name
                                   +'.tif'), "w",**meta_data)\
                                   as dest:
                 dest.write(NDVI,1)
                
            
            

        

        
        
        
        
        
        
        
        
        
        
        
        
        
        