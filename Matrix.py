# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:04:05 2020
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as mp
from matplotlib import cm
from matplotlib.colors import ListedColormap
from DataService import DataService


class Matrix:
  def __init__(self):
    self.data_service = DataService.getInstance()

  def __parse_data(self, data, metadata):
    """Creates a matrix with time differences since outbreak to case N
    
    Arguments:
        data {DataFrame} -- DataFrame of csv to be used to create the matrix
        metadata {Metadata} -- Metadata from data used
    
    Returns:
        {DataFrame} -- Matrix with time differences since outbreak to case N
    """
    matrix_data = pd.DataFrame(data, columns=["UID"])
    uid_positive = metadata["uid_positive"]

    size = len(uid_positive)
    # Calcula as diferencas de data
    count = 0
    for i in uid_positive:
      di = data.loc[data['UID'] == i, "Day_First_N_Infections"].values[0]
      new_column = []
      for j in uid_positive:
        dj = data.loc[data['UID'] == j, "Day_First_N_Infections"].values[0]
        if (not np.isnan(di)) and (not np.isnan(dj)):
          new_column.append(di.values[0] - dj.values[0])
        else:
          new_column.append('NULL')
      count = count + 1

      # Exibe progresso para aliviar a impaciencia
      progress = (count / size) * 100
      print('\r%.2f%% completo.' % progress, end="\r")
      matrix_data[i] = new_column
    return matrix_data

  def __get_matrix_colorcode_plot(self, data, metadata, file_name):
    """Creates Colorcode Plot from matrix
    
    Arguments:
        data {DataFrame} -- DataFrame of csv to be used to create the matrix
        metadata {Metadata} -- Metadata from data used
        file_name {str} -- Name of the output image file
    """
    matrix = self.__parse_data(data, metadata)

    top = cm.get_cmap('Oranges_r', 128)
    bottom = cm.get_cmap('Blues', 128)
    newcolors = np.vstack(
      (top(np.linspace(0, 1, 128)), bottom(np.linspace(0, 1, 128))))
    newcmp = ListedColormap(newcolors)
    fig, plot = mp.subplots(1, 1, figsize=(10, 10), constrained_layout=True)

    data_m = matrix.drop('UID', axis=1)
    data_m = data_m.drop(data_m.index[0])

    psm = plot.pcolormesh(data_m, cmap=newcmp, rasterized=True)
    fig.colorbar(psm, ax=plot)
    mp.show()
    fig.savefig(file_name.replace(".csv", ".png"), dpi=600)

  def jhu_matrix_colorcode_plot(self, file_name, options=None):
    """Creates Colorcode Plot from JHU Data
    
    Arguments:
        file_name {str} -- Name of the output image file
    
    Keyword Arguments:
        options {BrasilOptions} -- Options to be used in the filter
    """
    data = self.data_service.get_filtered_jhu_data(options)
    metadata = self.data_service.jhu_metadata

    self.__get_matrix_colorcode_plot(data, metadata, file_name)

  def brasil_matrix_colorcode_plot(self, file_name, options=None):
    """Creates Colorcode Plot from Brasil Data
    
    Arguments:
        file_name {str} -- Name of the output image file
    
    Keyword Arguments:
        options {BrasilOptions} -- Options to be used in the filter
    """
    data = self.data_service.get_filtered_brasil_io_data(options)
    metadata = self.data_service.brasil_io_metadata

    self.__get_matrix_colorcode_plot(data, metadata, file_name)
