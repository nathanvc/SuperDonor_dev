"""
Created on Sun Apr 30 2017

@author: Nathan V-C

Refactor code for super-donor predictive modeling
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
# import basicfn as bf
import ast
import re

# load donor dataframe from csv (some fields need to be converted to lists)
def load_dondf(filename):
    don_df = pd.read_csv(filename, sep='|')
    don_df['don_text_list'] = don_df['don_text_list'].apply(lambda x: ast.literal_eval(x))
    don_df['don_text_set'] = don_df['don_text_set'].apply(lambda x: ast.literal_eval(x))
    return don_df

# ----------
# Useful functions for manipulating dataframes/text
#-----------

def count_includes(textset, string):
    cnt = 0
    for t in textset:
        if string in t:
            cnt += 1
    return cnt

def set_includes(textset, string):
    for t in textset:
        if string in t:
            return 1
    return 0

def set_return(textset, string):
    list_out = []
    for t in textset:
        if string in t:
            list_out.append(t)
    return list_out

# filter first for a match to a filtered string (lower case match), and then to an exact match for a second string
# return 1 if matched, 0 else
def filtered_set_includes(textset, filt_string, match_string, case_ignore=False):
    for t in textset:
        if filt_string.lower() in t.lower():
            if case_ignore == False:
                if match_string in t:
                    return 1
            if case_ignore == True:
                if match_string.lower() in t.lower():
                    return 1
    return 0

# filter first for a match to a filtered string (lower case match), and then to an exact match for a second string
# return 1 if matched, 0 else
def filtered_return(textset, filt_string, match_string, case_ignore=False):
    list_out = []
    for t in textset:
        if filt_string.lower() in t.lower():
            if case_ignore == False:
                if match_string in t:
                    list_out.append(t)
            if case_ignore == True:
                if match_string.lower() in t.lower():
                    list_out.append(t)
    return list_out

# function to find location of last digit in a string
def last_digit_loc(str1):
    temp = list(enumerate(str1))
    temp.reverse()
    for ind, s in temp:
        if s.isdigit():
            return ind
        else:
            continue

# ----------------
# functions to add blood and eye features to donor dataframe
# ----------------
def add_blood(don_df):
    
    # Dictionary of possible bloodtypes
    BloodDict=['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']
    
    # search text for indicator of "blood" and then exact case match to blood type
    for bld in BloodDict:
        don_df[bld] = don_df['don_text_set'].apply(lambda x: filtered_set_includes(x, 'blood', bld))    
    
    # count bloodtypes indicated (so 0 = none reported, 1 = 1 reported, >1 = multiple reported)
    don_df['inc_blood'] = don_df[BloodDict].sum(axis=1)    
    return don_df

def add_eye(don_df):
    
    # Dictionary of possible eye colors
    EyeDict=['brown','blue','hazel','green']
    
    # search text for indicator of "eye" and then case insensitive match for color
    eyecol=[]
    for eyestr in EyeDict:
        don_df['eye_' + eyestr] = don_df['don_text_set'].apply(lambda x: 
                                  filtered_set_includes(x, 'eye', eyestr, case_ignore=True))  
        eyecol.append('eye_' + eyestr)
      
    # count eye colors indicated (so 0 = none reported, 1 = 1 reported, >1 = multiple reported)
    don_df['inc_eye'] = don_df[eyecol].sum(axis=1)    
    return don_df

# --- Functions for adding weight ---
# function to pull weight from a single string
#------------------------------------

def parse_weight_str(wt_str):
    w = wt_str
    w = w.split('Weight:')[-1].strip()
    ind = 0
    
    wt_dict = {}
    wt_dict['58 kg (128 lbs)'] = 128
    wt_dict['175lbs (80kg)'] = 175
    wt_dict['161 (73 kg)'] = 161
    wt_dict['76 (168 lbs)'] = 168
    wt_dict['? maybe 185'] = 185
    wt_dict['77 kilos/179 lbs'] = 179
    wt_dict['66/146'] = 146
    wt_dict['185/Lg'] = 185
    wt_dict['68/150'] = 150
    wt_dict['140 lbs / 63kg'] = 140
    wt_dict['104kg/229lb'] = 229
    wt_dict['108 kg/238 lbs'] = 238
    wt_dict['1\'70'] = 170
    wt_dict['216/225'] = 220.5
    wt_dict['160 Skin Tone: MedL  Eyes: Hazel Hair: Red/Wavy  Degree: MA/Political Science  Occupation: Public Affairs  Interest: Fencing/Reading/Write'] = 160
    
    while ind == 0:
        if w in wt_dict.keys():
            w = wt_dict[w]
            units = ''
            ind = 1
            continue
        elif 'ft' in w or "\'" in w or '\"' in w or '/' in w or 'Normal' in w or 'Medium Build' in w or 'Thin' in w or 'Slim' in w:
            w = ''
            units = ''
            ind = 1
            continue
        else:
            spl=last_digit_loc(w)
            if spl and spl<len(w)-1:
                units = w[spl+1:].strip()
                w=w[:spl+1]
            else:
                units = ''
            if '--' in w:
                w = np.mean([float(wt) for wt in w.strip(' ').split('--')])
            elif '-' in w:
                w = np.mean([float(wt) for wt in w.strip(' ').split('-')])
            else:
                try:
                    float(w)
                except ValueError:
                    w = ''
                else:
                    w = float(w)
                    if units == 'kg' or units == 'kgs':
                        w=2.20462*w
            ind = 1
            continue
    return(w)

# Take mean of all weight fields in list of Weight text strings
def wt_mean(wt_lst):
    if len(wt_lst)>0:
        temp = [parse_weight_str(wt) for wt in wt_lst]
        temp = [wt for wt in temp if wt != '' and wt > 100 and wt < 400]
        if len(temp)>0:
            return np.nanmean(temp)
        else:
            return np.nan
    else:
        return np.nan
    
def add_weight(don_df):
    don_df['weight'] = don_df['don_text_list'].apply(lambda x: set_return(x, 'Weight:'))  
    don_df['weight'] = don_df['weight'].apply(lambda x: wt_mean(x))
    return don_df

# # --- Functions for adding height ---
# # function to pull weight from a single string
# #------------------------------------

# function to parse multiple height formats to total inches
def get_inches(el_in):
    # regex for the proper format of feet'inches"
    r = re.compile(r"([0-9]+)'([0-9]*\.?[0-9]+)(\'\'|\")")
    r2 = re.compile(r"([0-9]+),([0-9]*\.?[0-9]+)(\'\'|\")")
    r3 = re.compile(r"([0-9]+)\"([0-9]*\.?[0-9]+)")
    r4 = re.compile(r"([0-9]+)\'([0-9]*\.?[0-9]+)")
    r4 = re.compile(r"([0-9]+)\'([0-9]*\.?[0-9]+)")
    r5 = re.compile(r"([0-9]+),([0-9]*\.?[0-9]+)")
    r6 = re.compile(r"([0-9]+)-([0-9]*\.?[0-9]+)")
    r7 = re.compile(r"([0-9]+);([0-9]*\.?[0-9]+)")
    r8 = re.compile(r"([0-9]+)/([0-9]*\.?[0-9]+)")
    r9 = re.compile(r"([0-9]+)\'")
    r10 = re.compile(r"([0-9]+)\"")
    r11 = re.compile(r"([0-9]+)cm")
    r12 = re.compile(r"([0-9]+)[ \t]+([0-9]*\.?[0-9]+)")
    r13 = re.compile(r"([0-9]+)")
    
    el = el_in
    el = el.lower()
    el = el.replace('~', '')
    el = el.replace('1/2', '.5')
    el = el.replace('``', '\"')
    el = el.replace('`','\'')
    el = el.replace('O', '0')
    el = el.replace(" ", "")
    el = el.replace('ft', '\'').replace('feet', '\'').replace('foot', '\'')
    el = el.replace('inches', '\"').replace('in', '\"')
    
    reg_ex = [r, r2, r3, r4, r5, r6, r7, r8]
    for reg in reg_ex:
        m = reg.match(el)
        if m != None:
            return int(m.group(1))*12 + float(m.group(2)) 
    
    m = r9.match(el)
    if m != None:
        return 12*int(m.group(1))

    m = r10.match(el)
    if m != None:
        return int(m.group(1))
    
    m = r11.match(el)
    if m != None:
        return 0.393701*int(m.group(1))
    
    m = r12.match(el_in)
    if m != None:
        return int(m.group(1))*12 + float(m.group(2)) 
    
    m = r13.match(el)
    if m != None:
        print('**', el, '**', m)
        num = int(m.group(1))
        if ((num > 60) & (num < 80)):
            print('--', num)
            return num
        elif ((num > 170) & (num < 205)):
            print('-&-', num)
            return 0.393701*num
            
    return np.nan

def parse_height_str(ht_str):
    h = ht_str
    h = h.split('Height: ')[-1].strip()
    ind = 0
    
    ht_dict = {}
    ht_dict['Between 5\'10\" and 6\'0\"'] = '5\'11\"'
    ht_dict['6'] = '6\'0\"'
    ht_dict['6 4'] = '6\'4\"'
    ht_dict['178 (5\'10\")'] = '5\'10\"'
    ht_dict['183/6-0'] = '6\'0\"'
    ht_dict['Tall, over 6ft 4\"'] = '6\'4\"'
    ht_dict['+6\''] = '6\'0\"'
    ht_dict['6\'4\" approx\''] = '6\'4\"'
    ht_dict['77'] = '77\"'
        
    while ind == 0:
        if h in ht_dict.keys():
            h = ht_dict[h]
            # units = ''
            # ind = 1
            continue
        else:
            h_in = get_inches(h)
            if pd.isnull(h_in):
                print(h)
                print(h_in)
            ind = 1
    return(h_in)

# Take mean of all weight fields in list of Weight text strings
def ht_mean(ht_lst):
    if len(ht_lst)>0:
        for h in ht_lst:
            temp = [parse_height_str(ht) for ht in ht_lst]
            temp = [ht for ht in temp if ht != '']
            print(temp)
            if len(temp)>0:
                return np.mean(temp)
            else:
                print(ht_lst)
                print(temp)
                return np.nan
    else:
        return np.nan
    
def add_height(don_df):
    don_df['height'] = don_df['don_text_list'].apply(lambda x: set_return(x, 'Height:'))  
    don_df['height'] = don_df['height'].apply(lambda x: ht_mean(x))
    return don_df