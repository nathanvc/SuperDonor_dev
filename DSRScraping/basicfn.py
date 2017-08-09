# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 15:14:53 2016

@author: nathanvc

Basic functions for data analysis, Nathan VC
Functions generic enough to be used on other projects
"""
import matplotlib.pyplot as plt


# Like matlab find, indices of entries that include a particular string
def findincludes(s, ch):
    return [i for i, ltr in enumerate(s) if ch in str(ltr)]


# Like matlab find, but indices of any entries that include any
# of a list of strings
def findincludes_list(s, ch_list):
    ind_out = []
    for ch in ch_list:
        ind_out.extend(findincludes(s, ch))
    ind_out = list(set(ind_out))
    return ind_out


# Like matlab find, for exactly equality of elements
# (probalby a number/float/int)
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# Like matlab find, for exactly equality of elements
# (probalby a number/float/int) works for a list of possible matches
def find_list(s, ch_list):
    ind_out = []
    for ch in ch_list:
        ind_out.extend(find(s, ch))
    ind_out = list(set(ind_out))
    return ind_out


# Like matlab find, for greater than
def findgreater(s, ch):
    return [i for i, ltr in enumerate(s) if ltr > ch]


# Bring specific figure to front
def show_plot(figure_id=None):

    if figure_id is not None:
        fig = plt.figure(num=figure_id)
    else:
        fig = plt.gcf()
    plt.show()
    plt.pause(1e-9)
    fig.canvas.manager.window.activateWindow()
    fig.canvas.manager.window.raise_()

# remove key from dictionary
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r
    
# detect if digit is in a string
# returns list of length (str1) with entries of 1 for digits and 
# 0 for space and 2 else
def strdigit(str1):
    c = ''
    for s in str1:
        if s.isdigit():
            c += '1'
        else:
            c += '0'
    return c
    
# function to find location of last digit in a string
def last_digit_loc(str1):
    temp = list(enumerate(str1))
    temp.reverse()
    for ind, s in temp:
        if s.isdigit():
            return ind
        else:
            continue
    
# insert space at a particular location in string
# inserts space after index loc (with zero indexing)
def insertspace(str2, loc):
    return str2[:loc+1] + ' ' + str2[loc+1:]

# pull out number from a string -- puts all elements together
def get_num(x):
    return int(''.join(ele for ele in x if ele.isdigit()))