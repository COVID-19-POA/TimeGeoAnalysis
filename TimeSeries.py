# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 14:41:44 2020

"""
import matplotlib.pyplot as mp
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
    fig, plot = mp.subplots(1, 1, figsize=(10, 10), constrained_layout=True)

    filtered_data = data[data.Day_First_N_Infections != "None"]
    plot.hist(filtered_data["Day_First_N_Infections"].values, bins=divs)
    mp.xlabel(x_label, fontsize=18)
    mp.ylabel("Frequency", fontsize=18)
    mp.title(title, fontsize=22)
    fig.savefig(out_file)

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
