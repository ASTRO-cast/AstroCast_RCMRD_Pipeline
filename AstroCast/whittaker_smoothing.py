# -*- coding: utf-8 -*-
"""
Created on Mon May  4 15:57:09 2020

@author: Andrew
"""
import numpy as np
import scipy as sp
import scipy.sparse
import scipy.linalg
from scipy.sparse.linalg import cg
import time
from datetime import datetime
import rasterio
from rasterio.windows import Window
import os
import shutil



def whitsm(y, lmda,data_length,maxiter):

  E = sp.sparse.eye(data_length)
  d1 = -1 * np.ones((data_length),dtype='d')
  d2 = -3 * d1
  d3 =  3 * d1
  d4 = -1 * d1
  D = sp.sparse.dia_matrix(([d1,d2,d3,d4],[0,1,2,3]), shape=(data_length-3, data_length)).asformat("csr")
  z = sp.sparse.linalg.cg(E + lmda * (D.transpose()).dot(D), y,tol=3e-2,maxiter = maxiter)
  return z[0]

def write_image(date,NDVI,meta_data):
    
    
    with rasterio.open('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\smoothed_NDVI\\Smoothed'+
                       str(date)+'.tif', "w",**meta_data)\
                       as dest:
                                
        dest.write(NDVI,indexes=1)
        print(date, ' Smoothed NDVI Tiff has been created')
            

def raw_to_datetime(unformatted_date):
    return datetime.strptime(str(int(unformatted_date)), '%Y%m%d')

  
def read_image(file,pos_x,pos_y,Window_x_size,Window_y_size):
    
        NDVI = rasterio.open(file).read(1,window = 
                                        Window(pos_x,pos_y,Window_x_size,
                                               Window_y_size)) # 1 is the target raster
        
        date = file.split('dekadal.')[1].split('.tif')[0]
        
        
        #meta_data = rasterio.open(file).meta.copy()
        return NDVI,date
    
def smooth_all(smoothing_array,Window_x_size,Window_y_size):

    smoothing_array = np.array(smoothing_array)
    linear_array = np.array([0,10,20,30])
    smoothed_array = np.empty(np.shape(smoothing_array),dtype='float32')    
    
    new_data_length = len(smoothing_array[553:,0,0])
    old_data_length = len(smoothing_array[:563,0,0])
    print(new_data_length,old_data_length)
    maxiter = new_data_length*10
    fill_array = np.full(len(smoothed_array[:]),1.175494351e-38)
    
    for x in range(0,Window_x_size):    
        for y in range(0,Window_y_size):

            if np.count_nonzero(smoothing_array[:563,y,x]==1.175494351e-38) > 400:
                smoothed_array[:,y,x] = fill_array

            else:
                pre_smoothed_NDVI =  smoothing_array[:563,y,x] # This is 2016-08-01
                 
                NDVI  =  smoothing_array[553:,y,x]
                 
                # Make sure there are no drops to zero in the previous data.
                # start_overall = time.time()
                
                for i in range(1,old_data_length-2):
                    if pre_smoothed_NDVI[i] < 0.01 :
                 
                        y2 = pre_smoothed_NDVI[i+2]
                        m = (pre_smoothed_NDVI[i-1]-y2)/-30
                        c = y2 - m*30
                   
                        pre_smoothed_NDVI[i-1:i+3] = (linear_array*m)+c 
                         
                  
                for i in range(1,new_data_length-2):
                    if NDVI[i+1] >= NDVI[i] + 0.2 or NDVI[i] < 0.01 :
                        y2 = NDVI[i+2]
                        m = (NDVI[i-1]-y2)/-30
                        c = y2 - m*30
                   
                        NDVI[i-1:i+3] = (linear_array*m)+c 
                        
                        
                # end = time.time()
                # print(end-start_overall)
                # start_overall = time.time()
                newly_smoothed = whitsm(NDVI,5, new_data_length,maxiter)
                # end = time.time()
                # print(end-start_overall)
                smoothed_array[:,y,x] = np.concatenate((pre_smoothed_NDVI, newly_smoothed[10:]))
            
    return smoothed_array


def smooth_new(smoothing_array,Window_x_size,Window_y_size):

    smoothing_array = np.array(smoothing_array)
    linear_array = np.array([0,10,20,30])
    smoothed_array = np.empty(np.shape(smoothing_array),dtype='float32')    
    
    new_data_length = len(smoothing_array)

    
    maxiter = new_data_length*10
    
    fill_array = np.full(len(smoothed_array[:]),1.175494351e-38)
    
    
    for x in range(0,Window_x_size):    
        for y in range(0,Window_y_size):

            if np.count_nonzero(smoothing_array[:,y,x]==1.175494351e-38) > 400:
                smoothed_array[:,y,x] = fill_array

            else:
                 
                NDVI  =  smoothing_array[:,y,x]
                 
                # start_overall = time.time()
                
                for i in range(1,new_data_length-2):
                    if NDVI[i+1] >= NDVI[i] + 0.2 or NDVI[i] < 0.01 :
                        y2 = NDVI[i+2]
                        m = (NDVI[i-1]-y2)/-30
                        c = y2 - m*30
                   
                        NDVI[i-1:i+3] = (linear_array*m)+c 
                        
                # end = time.time()
                # print(end-start_overall)
                # start_overall = time.time()
                newly_smoothed = whitsm(NDVI,5, new_data_length,maxiter)
                # end = time.time()
                # print(end-start_overall)
                smoothed_array[:,y,x] = newly_smoothed
        print(x,' done')
            
    return smoothed_array



def create_tif(dates,Window_x_size,Window_y_size,meta_data,offset):
    
    for data_no,date in enumerate(dates):
        
        actual_data_no = offset+data_no
        TIFF_NDVI = np.empty((Window_y_size,Window_x_size*157),dtype='float32')
        
        for strip in range(0,157):
            TIFF_NDVI[:Window_y_size,(strip)*Window_x_size:
                      (strip+1)*(Window_x_size)] =  np.load('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\file_dump\\Strip'+str(strip)+
                            'Day'+str(actual_data_no)+'.npy')
        
        write_image(date,TIFF_NDVI,meta_data)
        
        
        
        
def run_smoothing(files,end_only,amount_of_new_files):

    meta_data = rasterio.open(files[0]).meta.copy()
    
    
    # Set window size
    
    Window_x_size = 23
    Window_y_size = 4406
    
    start =time.time()
    for overall_counter,pos_x in enumerate(range(0,3611,23)):
    
            # Empty lists to store the data read in
            dates = []
            smoothing_array =[] 
            
            # Open the data from the files and store in lists so pixel wise smoothing can
            # be performed.
        
            for counter,file in enumerate(files):
                NDVI,date = read_image(file,pos_x,0,Window_x_size,Window_y_size)
                dates.append(date)
                smoothing_array.append(NDVI)
             
                print(counter,' out of ', len(files),' read')
                        

            if end_only:
                Smoothed_NDVI = smooth_new(smoothing_array,Window_x_size,
                                           Window_y_size)
                
                
            else:
                # Perform the pixel-wise smoothing
                Smoothed_NDVI = smooth_all(smoothing_array,Window_x_size,
                                           Window_y_size)

            
            for i in range(0,len(Smoothed_NDVI[:,0,0])):
                np.save('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\file_dump\\Strip'+str(overall_counter)+'Day'+str(i)+'.npy',Smoothed_NDVI[i,:,:])
            
            print(overall_counter,' out of 157 has been done')
    
    if end_only:
        
        offset = len(files) - amount_of_new_files
        
        create_tif(dates[-amount_of_new_files:],Window_x_size,Window_y_size,
                   meta_data,offset)
    else:
        create_tif(dates,Window_x_size,Window_y_size,meta_data,0)
    
            
    overall_end = time.time()
    print(overall_end-start)
    
    shutil.rmtree('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\file_dump')
    
    os.mkdir('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\file_dump')

    

#shape of files = (4406,3611)








