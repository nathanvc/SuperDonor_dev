# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 18:22:34 2016
@author: nathanvc
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import DSR_basicfn as bf

# ------------
# Functions for two slider plot examples (winslider & barslider)
# These sort categorized data according to the first input list,
# and plot proportions of each categorized item in a subset of
# the data, controled by "window" sliders and "center" sliders
# Window controls the % of total input data included in each window
# and center controls the center location in the sorted data
# Both lists need to be integers (designed for donor
# group size and some other discrete feature (e.g. bank, eye color))
# ------------


# Calculate proportion of each category (2nd input) for each discrete
# value of 1st input, allcats is all possible categories of the 2nd input
def prop_cnt(data, categ, allcats):
    prop_cnt = [[], []]
    ol = 0
    # loop through each unique value in the data
    for o in np.unique(data):
        # initialize prop_cnt vector long enough for all values of data
        # (this is where the integer dependence is)
        if o-ol > 1:
            for e in np.arange(ol+1, o, 1):
                prop_cnt.insert(o, [])
        prop_cnt.insert(o, [])
        inds = bf.find(data, o)
        # for c in np.unique(categ):
        for c in allcats:
            cat_temp = [categ[i] for i in inds]
            prop_temp = len(bf.find(cat_temp, c))/len(inds)
            prop_cnt[o].insert(c, prop_temp)
        ol = o
    return prop_cnt


# Function to find proportions of each catetory in +/- win elements from a
# center element near the start and end of list, pulls a smaller sample
# (cuts off first and last samples) whole list needs to contain integer
# numeric categories. Window includes center elements (so 2*win+1 elements)
def prop_win(center, win, data_reord, categ_reord, prop_cnt):
    prop_banks = []
    temp_data = []
    prop_sum = [0]*len(np.unique(data_reord))
    if center >= win and center <= len(data_reord)-win:
        temp_data = data_reord[center-win:center+win+1]
    if center < win:
        temp_data = data_reord[:2*win+1]
    if center > len(data_reord) - win:
        temp_data = data_reord[len(data_reord)-2*win:]
    for d in np.unique(temp_data):
        pv = len(bf.find(temp_data, d))/len(temp_data)
        prop_banks = [pv*p for p in prop_cnt[d]]
        prop_sum = [ps + pb for ps, pb in zip(prop_sum, prop_banks)]
    return (prop_sum, np.min(temp_data), np.max(temp_data))


# Calculate proportion of each category value in the full data list
def prop_full(categ_reord, allcats):
    return [len(bf.find(categ_reord, a))/len(categ_reord) for a in allcats]


# Plot single pie chart
# centperc is input between 0 and 1, for center point of plot values
# normalized to length of the input data list
# win is the width (in percent of total data included in the window)
# allcats is all possible categories, lab is labels for each category
# axis is location where plot should be made, col is colors
# title_string self explanatory
def plot_pie(centperc, winperc, data_reord, categ_reord, allcats, lab, ax,
             col, title_string):
    # calculate proportion of each category (2nd input) for each discrete
    # value of 1st input
    pc = prop_cnt(data_reord, categ_reord, allcats)
    # find location for center index
    center = np.round(centperc * len(data_reord)).astype(int)
    # calculate half width of window
    win = np.round(winperc * len(data_reord) * 0.5).astype(int)
    pie_data = prop_win(center, win, data_reord, categ_reord, pc)
    ax.pie(pie_data[0], labels=lab, autopct='%1.1f%%', shadow=False,
           startangle=90, colors=col)
    ax.axis('equal')
    ax.text(-1.7, 0.9, 'Total Donors:' + str(2*win+1))
    ax.text(1.1, 0.9, 'Group Size:' + str(pie_data[1]) + '-' + str(pie_data[2]))


# Plot single sorted bar chart (including baseline data in gray from prop_all)
# centperc is input between 0 and 1, for center point of plot values
# normalized to length of the input data list
# win is the width (in percent of total data included in the window)
# allcats is all possible categories, lab is labels for each category
# axis is location where plot should be made, col is colors
# title_string self explanatory, order is the sorted order of the bars,
# prop_all is the proportions to plot against (the gray bars)
def plot_bar(centperc, winperc, data_reord, categ_reord, allcats, lab, ax, col,
             title_string, prop_all, order):
    # calculate proportion of each category (2nd input) for each discrete
    # value of 1st input
    pc = prop_cnt(data_reord, categ_reord, allcats)
    # find location for center index
    center = np.round(centperc * len(data_reord)).astype(int)
    # calculate half width of window
    win = np.round(winperc * len(data_reord) * 0.5).astype(int)
    bar_data = prop_win(center, win, data_reord, categ_reord, pc)
    # reorder data to sort
    bar_data_sort = [bar_data[0][o] for o in order]
    prop_all_sort = [prop_all[o] for o in order]
    lab_sort = [lab[o] for o in order]
    col_sort = [col[o] for o in order]
    bw = 0.35
    #ax.yaxis.grid(color='gray', linestyle='dashed')
    #ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.barh(np.arange(len(allcats)), prop_all_sort, bw, alpha=0.5, color='k')
    ax.barh(np.arange(len(allcats))+0.35, bar_data_sort, bw, alpha=0.5, color=col_sort)
    plt.legend(['All donors', 'Subsample'], loc=4, fontsize=15)
    plt.xlabel('Proportion (%)', fontsize=15)
    plt.yticks(np.arange(len(lab))+bw, lab_sort, fontsize=15)
    plt.xticks(np.arange(0, 0.6, 0.1), np.arange(0, 70, 10))
    ax.text(0.2, 0.5, 'Total Donors:' + str(2*win+1), fontsize=15)
    ax.text(0.2, 1, 'Group Size:' + str(bar_data[1]) + '-' + str(bar_data[2]), fontsize=15)
    ax.set_xlim([0, 0.5])
    #ax.set_ylim([20,len(lab)])
    plt.tick_params(axis='x', which='major', labelsize=15)


# Plot sliding pie window chart,
# lab is labels for each category
# axis is location where plot should be made, col is colors
# title_string self explanatory
def winslider(data, category, allcats, lab, col, title_string):

    # sort data based on first list and reorder both input lists
    order_all = np.argsort(data).tolist()
    categ_reord = [category[o] for o in order_all]
    data_reord = [data[o] for o in order_all]

    # Values for initial pie chart
    ax = plt.subplot(111)
    plt.subplots_adjust(left=.1, bottom=0.25)
    a0 = 0.05
    f0 = 0.5

    # generate initial plot
    plot_pie(f0, a0, data_reord, categ_reord, allcats, lab, ax,
             col, title_string)

    # initialize sliders and axes
    axcolor = 'lightgray'
    axcent = plt.axes([0.2, 0.1, 0.65, 0.03], axisbg=axcolor)
    axwin = plt.axes([0.2, 0.15, 0.65, 0.03], axisbg=axcolor)
    scent = Slider(axcent, 'Center', 0, 1, valinit=f0, color='gray')
    swin = Slider(axwin, 'Window', 0, 1, valinit=a0, color='gray')
    plt.text(0.5, 26.5, title_string, horizontalalignment='center', fontsize=20)

    # function to update pie chart
    def update(val):
        cent = scent.val
        win = swin.val
        ax.clear()
        plot_pie(cent, win, data_reord, categ_reord, allcats, lab, ax,
                 col, title_string)

    # update if slider is clicked
    scent.on_changed(update)
    swin.on_changed(update)

    plt.show()


# Plot sorted bar chart with sliding window,
# also includes proportions of full data set (gray)
# allcats is all possible categories, lab is labels for each category
# axis is location where plot should be made,
# lab is label for each category, col is colors
# title_string is self explanatory
def barslider(data, category, allcats, lab, col, title_string):

    # sort data based on first list and reorder both input lists
    order_all = np.argsort(data).tolist()
    categ_reord = [category[o] for o in order_all]
    data_reord = [data[o] for o in order_all]

    # Values for initial bar chart
    ax = plt.subplot(111)
    plt.subplots_adjust(left=.1, bottom=0.25)
    a0 = 0.05
    f0 = 0.5

    prop_all = prop_full(category, allcats)
    # sort the proportion categories for full data set
    order = sorted(range(len(prop_all)), key=lambda k: prop_all[k])
    # generate initial plot
    plot_bar(f0, a0, data_reord, categ_reord, allcats, lab, ax, col,
             title_string, prop_all, order)

    # initialize sliders and axes
    axcolor = 'lightgray'
    axcent = plt.axes([0.2, 0.1, 0.65, 0.03], axisbg=axcolor)
    axwin = plt.axes([0.2, 0.15, 0.65, 0.03], axisbg=axcolor)
    scent = Slider(axcent, 'Center', 0, 1, valinit=f0, color='gray')
    swin = Slider(axwin, 'Window', 0, 1, valinit=a0, color='gray')
    plt.text(0.5, 26.5, title_string, horizontalalignment='center', fontsize=20)

    # function to update bar chart
    def update(val):
        cent = scent.val
        win = swin.val
        ax.clear()
        plt.subplot(111)
        plot_bar(cent, win, data_reord, categ_reord, allcats, lab, ax, col,
                 title_string, prop_all, order)

    # update if slider is clicked
    scent.on_changed(update)
    swin.on_changed(update)

    plt.show()
