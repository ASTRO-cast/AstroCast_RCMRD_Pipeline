# -*- coding: utf-8 -*-
"""This module creates the reports from the forecasts and saves as PDF

The class in this module is rather large and does not contain any calcualtions
,only the set up of the report. It has been made as clear as possible as this 
sort of thing in matplotlib is not ideal. If things are changed there can be a
butterfly effect very easily.

Created on Mon Nov 18 17:59:36 2019

@author: Andrew Bowell

"""
# Import the needed modules

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mp
import matplotlib.gridspec as gridspec
from datetime import timedelta
import h5py as h5

class createPDF:
    """Class housing the functions to set up the report
    
    Attributes
    ----------
    dataset : str 
        Name of dataset being looked at. This will become title for report and
        graphs in report.
    dataset_no : int
        The number of the dataset. This is so it can be looked up by comparing
        to the index of the shapefile.
    dates : :obj:`NumPy array` of :obj:`float`
        Dates of the known data and the forecast. Used for x-axis of plot and 
        the table as well. 
    VCI3M : :obj:`NumPy array` of :obj:`float`
        Known VCI3M as well as the forecast VCI3M.
    last_date : str
        Last date of which data was collected. This allows us to seperate the 
        forecast data from the known data.
    errors : :obj:`List` of :obj:`float` 
        Errors on the forecast at each week. Layout will change as these are
        just place holders at the moment.
    ax1 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax1 will be used 
        to plot the colorbar. 
    ax2 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax2 will be used 
        to plot the shapefile/map.
    ax3 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax3 will be used 
        to display the trend. (Bit useless. Fig text will be used in future 
       update)
    ax4 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax4 will be used 
        to plot the graph of the VCI3M time series. 
    ax5 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax5 will be used 
        to plot the table of VCI3M. 
    figure : Matplotlib Figure
        This is a matplotlib figure upon which axes can be placed.
    cmap : Matplotlib colourmap
        matplotlib colomap which can assign colours to different values or 
        different ranegs of values.
    norm : Matplotlib colourmap bounds 
        Uses the colormap to create the bounds. (min/max values)
    shapefile_path : str
        file path to the shapefile.
    database : str
        file path to the database file
    
    """ 
    def __init__(self,dataset,dataset_no,dates,predicted_VCI3M,last_known_date,
                 shapefile_path,database_path,column_name):
        """Initiate the attributes.

        Parameters
        ---------
        dataset : str 
           Name of dataset being looked at. This will become title for report 
           and graphs in report.
        dataset_no : int
           The number of the dataset. This is so it can be looked up by
           comparing to the index of the shapefile.
        dates : :obj:`NumPy array` of :obj:`float`
           Dates of the known data and the forecast. Used for x-axis of plot 
           and the table as well. 
        predicted_VCI3M : :obj:`NumPy array` of :obj:`float`
           Known VCI3M as well as the forecast VCI3M.
        last_known_date : str
           Last date of which data was collected. This allows us to seperate 
           the forecast data from the known data.
        database_path : str
            Databse name or file path so that errors can be read and calculated
            
        """
        self.dataset = dataset
        self.dataset_no = dataset_no
        self.dates = dates
        self.VCI3M = predicted_VCI3M
        self.last_date = last_known_date
        self.errors = np.empty(10,dtype=float)
        self.ax1,self.ax2,self.ax3,self.ax4,self.ax5 = None,None,None,None,None
        self.figure = None
        self.cmap = None
        self.norm = None
        self.shapefile_path = shapefile_path
        self.database = database_path
        self.column_name = column_name
        
        
    
    def forecast_store(self):
        
         file = h5.File(('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Databases\\'+self.database+'.h5'), 'r+')
         database_file = file[self.dataset]
         database_file[-10,4:] = self.VCI3M[-10:]
         file.close()
        
    def error_calc(self):
        """This function uses the hindcast data to calcualte the errors
        
        This function opens the main database file and compares the hindcast
        data for each lag time with the actual data. This is done by 
        calculating the residuals (actual-forecasted) for each prediction time
        step and then taking the standard deviation of the residuals. This is
        then multiplied by two so that 99% of future predictions will fall
        within our calculated uncertainty. 
        

        Returns
        -------
        None.

        """
        file = h5.File(('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Data\\Databases\\'+self.database+'.h5'), 'r+')
        print(self.dataset)
        dataset_array = np.array(file[self.dataset],dtype=float)
        dataset_array[dataset_array==0] = np.nan
        
        self.errors[0] = 0
        
        for jump_ahead in range(1,10):
            self.errors[jump_ahead] = np.nanstd(dataset_array[:-1,3]-
                                           dataset_array[1:,jump_ahead+3])
            
        file.close()
        
        self.set_up_figure()
        
        
    def set_up_figure(self):
        """This function creates the figure and axes.
        
        Matplotlib's gridspec function is used to assin different parts of the
        figure to different parts of the report. The axis is turned of for 
        some of the axes like the map so there is not a square box around it.
        The title of the figure is also set as well as adding some text about 
        where the forecasts can currently be found. The colour_bar and 
        create_map functions are then called.
    
        Returns
        -------
        None.

        """
        self.forecast_store()
        self.figure = plt.figure(figsize=(11.69*2,8.27*2))
        
        layout = gridspec.GridSpec(ncols=141, nrows=100, figure=self.figure)
        
        self.ax1 = self.figure.add_subplot(layout[5:8, 0:60])
        
        self.ax2 = self.figure.add_subplot(layout[0:, 0:60])
        
        self.ax3 = self.figure.add_subplot(layout[6:18, 0:])
        
        self.ax4 = self.figure.add_subplot(layout[5:45,65:])
        
        self.ax5 = self.figure.add_subplot(layout[65:85,1:20])
        
        self.ax2.axis('off')
        self.ax3.axis('off')
        self.ax5.axis('off')
        
        plt.subplots_adjust(hspace = -.175)
        plt.subplots_adjust(wspace = +1.5)
    
        self.figure.suptitle(str(self.dataset)+" Vegetation Outlook",
                             fontsize=24)
        
        self.figure.subplots_adjust(top=0.95)
    
        self.figure.patch.set_facecolor('lightblue')
        
        img = plt.imread('AC_logo.png')
        self.ax5.imshow(img)
        
        # self.figure.text(0.577,0.26, ("Please find our weekly forecasts (MCD43 at the" 
        #                        "link below \n \n"
        #                        "       https://tinyurl.com/AstroCastForecasts")
        #                        ,fontsize=18)
        
        plt.subplots_adjust(left=0.15, bottom=0.005, right=0.93, top=0.95, 
                        wspace=0, hspace=0)
        
        self.colour_bar()
        self.create_map()
    
    def colour_bar(self):
        """ This function creates the colourbar
        
        The bounds of the colourbar are set along with the colours. The colour
        bar is then added onto ax1 as well as sorting out the tick frequency.
        The title of the colourbar is also set.

        Returns
        -------
        None.

        """
        
        bounds = [0,0.00001, 10, 20, 35,50,100]
        self.cmap = mp.colors.ListedColormap(['white','r', 'darkorange',
                                              'yellow','limegreen',
                                              'darkgreen'])
        
        self.norm = mp.colors.BoundaryNorm(bounds, self.cmap.N)
        
        mp.colorbar.ColorbarBase(ax=self.ax1, cmap=self.cmap,norm=self.norm,
                                 orientation='horizontal')



    
        self.ax1.set_title('VCI3M Forecast For ' +
                           str(self.dates[-7].date()),fontsize=20)
        
        self.ax1.tick_params(labelsize=20)
        
        labels = [tick.get_text() for tick in self.ax1.get_xticklabels()]
        labels[0] = 'No Data'
        self.ax1.set_xticklabels(labels)
        
        
    def create_map(self):
        """This function plots the map of a shapefile using geopandas.
        
        Using geopandas the shapefile is read and a new column of VCI3M is 
        added onto it. Everything is set to zero apart from the dataset we are
        creating the report for. The shapefile is then plotted based on it's
        VCI3M. The set_trend function is then called.

        Returns
        -------
        None.

        """
        
        shapefile = gpd.read_file(self.shapefile_path).sort_values(
            [self.column_name])

        map_VCI3M = np.full(len(shapefile),0)
        
        map_VCI3M[int(self.dataset_no)] = self.VCI3M[-7]
        
        shapefile['VCI3M'] = map_VCI3M
        
        self.ax2 = shapefile.plot(ax=self.ax2,column ='VCI3M',cmap = self.cmap,
                                  norm=self.norm,legend= False,
                                  edgecolor='Black',
                                  label= shapefile[self.column_name])
        
        self.set_trend()



    def set_trend(self):
        """ This function sets the trend for the VCI3M
        
        The trend will simply be up or down. It just checks if the VCI3M value
        in a few weeks will be larger than that in a couple of weeks. The text 
        is then displayed to ax3

        Returns
        -------
        None.

        """
            
        if self.VCI3M[-6] > self.VCI3M[-7]:
            self.ax3.text(0.277,0.45,'Trend = Up',verticalalignment='center',
                          horizontalalignment='right',
                          transform=self.ax3.transAxes, fontsize=22)
        else:
            self.ax3.text(0.277,0.45,'Trend = Down',verticalalignment='center',
                          horizontalalignment='right',
                          transform=self.ax3.transAxes,fontsize=22)
            
        self.VCI3M_graph()    

    def VCI3M_graph(self):
        """This function handles the grpahing of the time series.
        
        The matplotlib fill between function allows a shaded region to be 
        created where there is uncertainty. We know that the predicted VCI3M 
        will just be the last 9 values so this is easy enough. The whole time
        series is then plotted as a solid black line and then a black, vertical
        dashed line is used to signify the last known date data was collected
        on. As currently, the data is quite noisey the VCI3M can dip below 
        0. There is a small if statement that checks for this and then changes
        the limits on the plot so that all the data can be seen. The background
        is then shaded in using the colourmap created earlier.
        This is all plotted to ax4.
    
        Returns
        -------
        None.

        """
        #------------------- VCI3M Graph -----------------------#
            
        # The 4th axis plots the past 30 weeks of actual data and then the 
        #predicted data is also plotted
        # The data then has the error shaded onto it. 
            
        self.ax4.fill_between(self.dates[-10:], self.VCI3M[-10:]-self.errors,
                              self.VCI3M[-10:] + self.errors,lw=3,
                              label='Forecast VCI3M',color='blue',
                              alpha=0.45,zorder=4,interpolate=True)
        
        
        self.ax4.plot(self.dates,self.VCI3M, linestyle = 'solid' ,
                      lw = 3, color = 'black',label='')
        
        self.ax4.vlines(self.last_date,-100,110,linestyle = '--',color = 'black',
                        lw = 3, label = 'Day of last observation')
        
    
        self.ax4.set_xlim(self.dates[-40],self.dates[-1]+timedelta(days=7))
        
        max_value,min_value =np.max(self.VCI3M[-40:]), np.min(self.VCI3M[-40:])
                                                              
        if min_value < 0 :
            self.ax4.set_ylim(min_value-10,100)
        
            self.ax4.axhspan(-100, 10, alpha=0.5, color='r')
        else:
            self.ax4.set_ylim(0,100)
            self.ax4.axhspan(0, 10, alpha=0.5, color='r')
            
        
        # Shading the background based on where the VCI3M is
        
        
        self.ax4.axhspan(10, 20, alpha=0.5, color='darkorange')
        self.ax4.axhspan(20, 35, alpha=0.5, color='yellow')
        self.ax4.axhspan(35, 50, alpha=0.5, color='limegreen')
        self.ax4.axhspan(50, 200, alpha=0.5, color='darkgreen')
        self.ax4.set_title(str(self.dataset) + ' VCI3M',fontsize=20)
        
        self.ax4.legend()
        
        self.table()


    def table(self):
        """Small function creating the table for the report.
            
        A table is created with the dates and corresponding VCI3M predicted 
        values. The background is set to be the same colours as the cmap 
        created earlier. This is also plotted to ax4 as tables need to be
        accompanied by graphs when using matplotlib.
        
        Returns
        -------
        None.

        """
        TableList = [np.round(self.VCI3M[-10:],1)]
        RowLabels = ['VCI3M']
        self.ax4.table(cellText=TableList,
                  colLabels = [date.date() for date in self.dates[-10:]],
                      rowLabels =RowLabels,bbox=[0.0,-0.5,1,.28],fontsize=30,
                          cellColours=self.cmap(self.norm(TableList)))
        
        self.save_show_fig()
        
    def save_show_fig(self):
        """Small function that saves the figure.
        
        Save the figure with the name of the dataset and the data which the
        data was last measured on. Also show the figure,

        Returns
        -------
        None.

        """
        plt.savefig('C:\\Rangeland\\image_data\\Andrew\\RCMRD Pipeline\\Forecasts\\Forecast for '+str(self.dataset)+' dated' +
                   str(self.dates[-11].date())+'.pdf',dpi = 400,
                       facecolor=self.figure.get_facecolor())
       
        plt.show()





    
    
    
    
    
    
    
