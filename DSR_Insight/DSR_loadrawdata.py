"""
Created on 2-12-2016

@author: %nathanvc

Pilot analysis of data from the donor sibling registry
Sample set of 6 banks: Xytex, Fairfax, CCB, TSBC, Repromed, NECC
"""

import pandas as pd
import os
import numpy as np
import DSR_basicfn as bf
import itertools as it


# function to load abbreviations for all banks
# current mappingfile is DSR_urlkeys.xlsx
def load_bank_ids(mappingfile):
    xl = pd.ExcelFile(mappingfile)
    df = xl.parse('urlkeys')
    banklist = df['Abbrev'].tolist()
    return banklist
    
    
def load_pairs(pairfile):
    xl = pd.ExcelFile(pairfile)
    pairdf = xl.parse('multibankonly_clean_cull')
    pairlist=[]
    allpairs=[]
    for j in range(len(pairdf)):
        pairlist=[];
        pairlist.append((pairdf.iloc[j]['Bank1'],pairdf.iloc[j]['ID1']))
        pairlist.append((pairdf.iloc[j]['Bank2'],pairdf.iloc[j]['ID2']))
        if not pd.isnull(pairdf.iloc[j]['Bank3']):
            pairlist.append((pairdf.iloc[j]['Bank3'],pairdf.iloc[j]['ID3']))
        if not pd.isnull(pairdf.iloc[j]['Bank4']):  
            pairlist.append((pairdf.iloc[j]['Bank4'],pairdf.iloc[j]['ID4']))
        if not pd.isnull(pairdf.iloc[j]['Bank5']):
            pairlist.append((pairdf.iloc[j]['Bank5'],pairdf.iloc[j]['ID5']))
        indpairs_temp=it.combinations(pairlist,2)
        indpairs_list=[list(p) for p in indpairs_temp]
        allpairs.extend(indpairs_list)
        
    return allpairs
    
def load_groups(pairfile):
    xl = pd.ExcelFile(pairfile)
    pairdf = xl.parse('multibankonly_clean_cull')
    grouplist=[]
    allgroups=[]
    for j in range(len(pairdf)):
        grouplist=[];
        grouplist.append((pairdf.iloc[j]['Bank1'],pairdf.iloc[j]['ID1']))
        grouplist.append((pairdf.iloc[j]['Bank2'],pairdf.iloc[j]['ID2']))
        if not pd.isnull(pairdf.iloc[j]['Bank3']):
            grouplist.append((pairdf.iloc[j]['Bank3'],pairdf.iloc[j]['ID3']))
        if not pd.isnull(pairdf.iloc[j]['Bank4']):  
            grouplist.append((pairdf.iloc[j]['Bank4'],pairdf.iloc[j]['ID4']))
        if not pd.isnull(pairdf.iloc[j]['Bank5']):
            grouplist.append((pairdf.iloc[j]['Bank5'],pairdf.iloc[j]['ID5']))
        allgroups.append(grouplist)
        
    return allgroups

# Make list of raw data file names
# directory can contain only data files, one per bank
# ------------
def list_rawfiles(d):
    list_rf = [os.path.join(d, f) for f in os.listdir(d) if f[0] != '.' and f[0] != '~']
    for l in list_rf:
        print(l)
    return list_rf


# Function that reads in raw data file in excel, at location "file",
# and returns cleaned data (dictionary of lists indexed by donor offspring)
# ----------
def reformat_offsp(rawfile, sheetname):

    # read in & parse excel file
    xl = pd.ExcelFile(rawfile)
    df = xl.parse(sheetname, skiprows=4)
    df_mat = df.values  # matrix object for easier use with numpy

    # take cumulative sum of non-nan values,
    # this will give index of value to take for donor that applies in each row
    donor_ind = pd.notnull(df).cumsum()-1

    # find non-nan values of the donor column of df
    donor_list = np.array(np.where(pd.notnull(df.iloc[:, 0].values))).T

    # replace the nans with relevant donor information
    donors_fill = df_mat[donor_list[donor_ind.values[:, 0]], 0]

    # ---------
    # Collect index for each child
    # ---------
    # find girl indices (space important to exclude logins with "girl" in name)
    g_ind = bf.findincludes(df_mat[:, 2], 'Girl ')

    # find boy indices (space important to exclude logins with "boy" in name)
    b_ind = bf.findincludes(df_mat[:, 2], 'Boy ')

    # find child indices
    c_ind = bf.find(df_mat[:, 2], 'Child')
    # ---------

    posted = []

    # Define ending index for each family block in raw data
    end_ind = bf.findincludes(df_mat[:, 2], 'Updated on')
    for i, e in enumerate(end_ind):
        if 'Posted by' in df_mat[e+1, 2]:
            end_ind[i] = e+1
            posted.append(str.split(df_mat[e+1, 2])[2][0:])
        else:
            posted.append(np.nan)
    start_ind = [0] + [ei + 1 for ei in end_ind[0:-1]]
    familyid = [0]*len(df_mat)
    for s in start_ind:
        familyid[s] = 1
    familyid = np.cumsum(familyid)

    # make long posted by list
    posted_long = []
    for i, p in enumerate(posted):
        posted_long += [p] * (end_ind[i] - start_ind[i] + 1)
    # add nan for last entry (replaces count of matches for the bank)
    posted_long.append(np.nan)

    # find indices of lines that indicate username (used to make 'UserID')
    user_long = []
    user_ind = bf.findincludes(df_mat[:, 2], 'Updated on')
    for i, u in enumerate(user_ind):
        user = str.split(df_mat[u, 2])[-1][0:-1]
        user_long += [user] * (end_ind[i] - start_ind[i] + 1)
    # add nan for last entry (replaces count of matches for the bank)
    user_long.append(np.nan)

    # attach donor description entered for each family
    desc_list = df_mat[start_ind, 1]
    # shift index back by 1, bc cumsum starts at 1
    desc_long = [desc_list[i-1] for i in familyid]

    # ----------
    # Make the clean data output
    # ----------
    data_clean = {
        'OrigIndex': g_ind + b_ind + c_ind,  # original indices
        'DonorID': [],
        'DonorDesc': [],
        'Sex': [],
        'Birthyear': [],
        'FamilyID': [],
        'UserID': [],
        'Bank': [],
        'PostedBy': []
    }

    # -- Pull Donor IDs per kid from the original loaded excel file
    # data_clean['DonorID'] = donors_fill[data_clean['OrigIndex'], 0].tolist()
    donor_temp = donors_fill[data_clean['OrigIndex'], 0].tolist()
    bad_chars=[' ', '"']
    data_clean['DonorID']=[]
    for d in donor_temp:
        tempstr=str(d).replace('"','').replace(' ','')
        data_clean['DonorID'].append(tempstr)

    # -- Pull Donor Description per kid from the original loaded excel file
    # data_clean['DonorDesc'] = desc_long[data_clean['OrigIndex']].tolist()
    # data_clean['DonorDesc'] = desc_long[data_clean['OrigIndex']].tolist()
    data_clean['DonorDesc'] = [desc_long[i] for i in data_clean['OrigIndex']]

    # -- make gender indicator list (order, girls, boys, child)
    data_clean['Sex'] = [1]*len(g_ind) + [2]*len(b_ind) + [3]*len(c_ind)

    # --enter birthyear if it exists, NaN if it does not
    for i, d in enumerate(df_mat[data_clean['OrigIndex'], 2]):
        cand_year = d[-4:]  # pull out a candidate year
        #print(cand_year)
        #print(d, cand_year, cand_year[0])
        if cand_year[0] == '2' or cand_year[0] == '1':
            data_clean['Birthyear'].append(int(cand_year))
        else:
            data_clean['Birthyear'].append(np.nan)
        #print(data_clean['Birthyear'][-1])


    # --ID number per family
    # --(indexed per bank, deal with duplicates if concatenating)
    data_clean['FamilyID'] = familyid[data_clean['OrigIndex']].tolist()

    # --UserID who posted the listing (this may allow linking
    # families across banks/donors)
    data_clean['UserID'] = [user_long[i] for i in data_clean['OrigIndex']]

    # --Make entry for bank, so can concatenate all banks into single dataframe
    bank = str.split(str.split(rawfile, '/')[-1], '_')[0]
    data_clean['Bank'] = [bank] * len(data_clean['OrigIndex'])

    # --Category of who posted the listing (sperm donor, offspring, parent,
    #  nan if not listed)
    data_clean['PostedBy'] = [posted_long[i] for i in data_clean['OrigIndex']]

    return data_clean


# Load and clean all bank files in a given directory d
# data files must be named with bank tag first,
# one file per bank in the directory
def load_clean_allbanks(rawdatafile):

    # current mappingfile is DSR_urlkeys.xlsx
    banklist = load_bank_ids('../DSR_rawdata_update/DSR_urlkeys.xlsx')

    # clean each one, and put cleaned output into a dictionary
    numfam = []
    AllBanks = {}
    for bank in banklist:
        print(bank)
        AllBanks[bank] = reformat_offsp(rawdatafile, bank)
        # Replace the family id field incrementing by the prior values,
        # so ids unique over all loaded banks
        AllBanks[bank]['FamilyID'] = [id + np.sum(numfam)
                                      for id in AllBanks[bank]['FamilyID']]
        numfam.append(len(np.unique(AllBanks[bank]['FamilyID'])))

    return (AllBanks, banklist)



