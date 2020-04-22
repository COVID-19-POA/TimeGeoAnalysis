# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 14:41:44 2020

"""
import matplotlib.pyplot as mp
from matplotlib.ticker import MaxNLocator
from DataService import DataService


class TimeSeries:
  def __init__(self):
    self.data_service = DataService.getInstance()

  def __hist_first_infections(self, data, out_file, x_label, title, divs):
    """Creates a histogram of the provided data
    
    Arguments:
        data {DataFrame} -- DataFrame to be used on the histogram
        out_file {str} -- Name of the image file
        x_label {str} -- Label for the X axis
        title {str} -- Title of the plot
        divs {int} -- Size of histogram bins
    """
    
    tick = mp.figure(figsize=(15,10)).gca()
    tick.yaxis.set_major_locator(MaxNLocator(integer=True))
    filtered_data = data[data.Day_First_N_Infections != "None"]
    tick.hist(filtered_data["Day_First_N_Infections"].values, 
              bins=divs,
              edgecolor='black',
              linewidth=1)
    mp.xlabel(x_label, fontsize=18)
    mp.ylabel("Frequency", fontsize=18)
    mp.xlim(left=-1,right=max(filtered_data["Day_First_N_Infections"].values)+1)
    mp.title(title, fontsize=22)
    
    
    mp.savefig(out_file)

  def brasil_hist_first_infections(self,
                                   out_file="brasil_history",
                                   x_label="",
                                   title="",
                                   divs=45,
                                   options=None):
    """Creates a histogram of Brasil
    
    Keyword Arguments:
        out_file {str} -- Name of the image file (default: {"brasil_history"})
        x_label {str} -- Label for the X axis (default: {""})
        title {str} -- Title of the plot (default: {""})
        divs {int} -- Size of histogram bins (default: {45})
        options {BrasilOptions} -- Options to be used to filter data
    """

    data = self.data_service.get_filtered_brasil_io_data(options)

    self.__hist_first_infections(data, out_file, x_label, title, divs)

  def jhu_hist_first_infections(self,
                                out_file="jhu_history",
                                x_label="",
                                title="",
                                divs=45,
                                options=None):
    """Creates a histogram of JHU Data
    
    Keyword Arguments:
        out_file {str} -- Name of the image file (default: {"brasil_history"})
        x_label {str} -- Label for the X axis (default: {""})
        title {str} -- Title of the plot (default: {""})
        divs {int} -- Size of histogram bins (default: {45})
        options {JhuOptions} -- Options to be used to filter data
    """

    data = self.data_service.get_filtered_jhu_data(options)

    self.__hist_first_infections(data, out_file, x_label, title, divs)
    
  def jhu_global_hist_first_infections(self,
                                       out_file="jhu_history",
                                       x_label="",
                                       title="",
                                       divs=45):
    """Creates a histogram of JHU global Data
    
    Keyword Arguments:
        out_file {str} -- Name of the image file (default: {"brasil_history"})
        x_label {str} -- Label for the X axis (default: {""})
        title {str} -- Title of the plot (default: {""})
        divs {int} -- Size of histogram bins (default: {45})
    """
  
    data = self.data_service.get_clustered_global_jhu_data()
    
    self.__hist_first_infections(data, out_file, x_label, title, divs)

  def euod_hist_fist_infections(self,
                                       out_file="euod_history",
                                       x_label="",
                                       title="",
                                       divs=45):
    """Creates a histogram of EU OpenData global dataset
    """
    data = self.data_service.time_series_euod()
    
    self.__hist_first_infections(data, out_file, x_label, title, divs)