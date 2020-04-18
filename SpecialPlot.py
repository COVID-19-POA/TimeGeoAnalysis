# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:17:57 2020

"""
import matplotlib.pyplot as mp
import seaborn as sns

class SpecialPlot:
    
    def super_hist(self, ts_list, alpha=0.5, log_scale=True, bins=45):
        """
        Gera grafico com histogramas superpostos

        Parameters
        ----------
        ts_list : lista de objetos TimeSeries

        Returns
        -------
        None.

        """
        fig, plot = mp.subplots(
            1, 1, figsize=(15, 10), constrained_layout=True)
        
        names = []
        for ts in ts_list:
            names.append(ts.territory)
            plot_data = ts.data[ts.data.Day_First_N_Infections != "None"]
            column_data = plot_data["Day_First_N_Infections"].values
            sns.distplot(
                column_data, 
                kde=False, 
                label=ts.territory, 
                bins=bins,
                hist_kws={"linewidth": 1, "alpha": alpha,
                          "edgecolor": 'black',
                          "log": log_scale})

        mp.legend(loc='upper left', fontsize=20)
        mp.xlabel(
            "Days from outbreak to " + str(ts_list[0].N) + " cases in county",
              fontsize=18)
        mp.ylabel("Frequency", fontsize=18)
        
        fig.savefig(
            "hist_N" + str(ts_list[0].N) + "_" + "_".join(names) + ".png")
