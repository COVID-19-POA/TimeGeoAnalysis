# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:17:57 2020

"""
import matplotlib.pyplot as mp
import seaborn as sns


class SpecialPlot:
  def super_hist(self, data_list, alpha=0.5, log_scale=True, bins=45):
    """Creates a plot from a list of dataframes overlapped
    
    Arguments:
        data_list {DataFrame[]} -- List of dataframes to be plotted
    
    Keyword Arguments:
        alpha {float} -- Alpha value for the overlapping layout (default: {0.5})
        log_scale {bool} -- Log scale of the plot (default: {True})
        bins {int} -- Size of histogram bins (default: {45})
    """

    fig, _ = mp.subplots(1, 1, figsize=(15, 10), constrained_layout=True)

    names = []
    for data in data_list:
      plot_data = data[data.Day_First_N_Infections != "None"]
      column_data = plot_data["Day_First_N_Infections"].values
      sns.distplot(column_data,
                   kde=False,
                   bins=bins,
                   hist_kws={
                     "linewidth": 1,
                     "alpha": alpha,
                     "edgecolor": 'black',
                     "log": log_scale
                   })

    mp.legend(loc='upper left', fontsize=20)
    mp.xlabel("Days from outbreak to case number " + str(data_list[0].N) +
              " in county",
              fontsize=18)
    mp.ylabel("Frequency", fontsize=18)

    fig.savefig("hist_N" + str(data_list[0].N) + "_" + "_".join(names) +
                ".png")
