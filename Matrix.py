# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:04:05 2020
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as mp
from matplotlib import cm
from matplotlib.colors import ListedColormap

class Matrix:
    
    def __init__(self, time_series):
        """
        Inicia uma matrix com as diferencas de tempo do outbreak ate o caso N

        Parameters
        ----------
        time_series : objeto TimeSeries

        Returns
        -------
        None.

        """
        
        self.matrix_data = pd.DataFrame(
            time_series.data, columns=["UID"])
        
        size = len(time_series.uid_positive)
        # Calcula as diferencas de data
        count = 0
        for i in time_series.uid_positive:
            di = time_series.data.loc[
                time_series.data['UID'] == i,
                "Day_First_N_Infections"].values[0]
            new_column = []
            for j in time_series.uid_positive:
                dj = time_series.data.loc[
                    time_series.data['UID'] == j,
                    "Day_First_N_Infections"].values[0]
                if (not np.isnan(di)) and(not np.isnan(dj)):
                    new_column.append(di.values[0]-dj.values[0])
                else:
                    new_column.append('NULL')
            count = count + 1
        
            # Exibe progresso para aliviar a impaciencia
            progress = (count/size)*100
            print('\r%.2f%% completo.' % progress, end="\r")
            self.matrix_data[i] = new_column

    def matrix_colorcode_plot(self, file_name):
        """ Salva grafico com colorcode da matriz
        """
        top = cm.get_cmap('Oranges_r', 128)
        bottom = cm.get_cmap('Blues', 128)
        newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                           bottom(np.linspace(0, 1, 128))))
        newcmp = ListedColormap(newcolors)
        fig, plot = mp.subplots(1, 1, figsize=(10, 10), constrained_layout=True)

        data_m = self.matrix_data.drop('UID', axis=1)
        data_m = data_m.drop(data_m.index[0])

        psm = plot.pcolormesh(data_m, cmap=newcmp, rasterized=True)
        fig.colorbar(psm, ax=plot)
        mp.show()
        fig.savefig(file_name.replace(".csv", ".png"), dpi=600)