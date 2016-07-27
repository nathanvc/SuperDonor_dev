# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 15:54:34 2016

@author: nathanvc

Functions to reorganize DSR data for analysis and plotting
"""

import DSR_basicfn as bf
import numpy as np
import itertools as it
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import scipy

# -----------
# Calculate female/male offspring counts
# -----------
def FM_Counts(AllBanks, banklist, Counts):

    FM_Counts = {
        'Offspring': {},
        'Parent': {},
        'Egg': {},
        'Sperm': {}
    }

    for key in FM_Counts:
        FM_Counts[key] = {
            'F_cnt': [],
            'M_cnt': [],
            'FM_tot': []
            }

    for i, b in enumerate(banklist):
        # loop perform F/M count for each "posted by" group
        for key in FM_Counts:
            FM_Counts[key]['F_cnt'].append(len([x for x in bf.find(AllBanks[b]['Sex'], 1)
                                           if x not in Counts[b]['Unknown_Inds'] and
                                           AllBanks[b]['PostedBy'][x] == key]))
            FM_Counts[key]['M_cnt'].append(len([x for x in bf.find(AllBanks[b]['Sex'], 2)
                                           if x not in Counts[b]['Unknown_Inds'] and
                                           AllBanks[b]['PostedBy'][x] == key]))
            FM_Counts[key]['FM_tot'].append(FM_Counts[key]['F_cnt'][-1] +
                                            FM_Counts[key]['M_cnt'][-1])

    # for FM_Counts, add a final entry that is sum of all included banks
    for key in FM_Counts:
        for cnt in FM_Counts[key]:
            FM_Counts[key][cnt].append(np.sum(FM_Counts[key][cnt]))

    # Add entry that is proportion of total for Female and Male per bank,
    # only do this for those posted by offspring or parent
    for key in ['Parent','Offspring']:
    
        # only take ratios if no zero counts
        #if not bf.find(FM_Counts[key]['M_cnt'],0) and not bf.find(FM_Counts[key]['F_cnt'],0):
        FM_Counts[key]['F_prop'] = [f/t if t > 0 else np.nan for f, t in zip(FM_Counts[key]['F_cnt'],
                                    FM_Counts[key]['FM_tot'])]
                                    
        FM_Counts[key]['M_prop'] = [m/t if t > 0 else np.nan for m, t in zip(FM_Counts[key]['M_cnt'],
                                    FM_Counts[key]['FM_tot'])]
        
        # difference in sex ratio from one
        FM_Counts[key]['MF_ratio'] = [m/f-1 if f > 0 else np.nan for m, f in zip(FM_Counts[key]['M_cnt'],
                                      FM_Counts[key]['F_cnt'])]
                                    
    return FM_Counts


# -----------
# Calculate offspring counts & features per donor
# -----------
def offsp_cnts(AllBanks, banklist):
    Counts = {}
    for i, b in enumerate(banklist):
        #print(b)
        Counts[b] = {
            'Unq_Donors': [],
            'Unknown_Inds': [],
            'Sp_kids': [],
            'Egg_kids': [],
            'Self_inds': [],
            'Parent_inds': [],
            'Offsp_Cnt': [],
            'Donor_Inds': {},
            'Donor_Desc': {},
            'Offsp_Year': []
        }

        # list of unique donors
        Counts[b]['Unq_Donors'] = list(set(AllBanks[b]['DonorID']))

        # indices for unknown donors
        Counts[b]['Unknown_Inds'] = bf.find(AllBanks[b]['DonorID'], 'unknown')

        # Remove unknown donors from "unique donors" list
        if Counts[b]['Unknown_Inds']:
            Counts[b]['Unq_Donors'].remove('unknown')

        # Identify indices for kids posted by sperm & egg donors.
        # We will mostly disregard these.
        Counts[b]['Sp_kids'] = bf.find(AllBanks[b]['PostedBy'], 'Sperm')
        Counts[b]['Egg_kids'] = bf.find(AllBanks[b]['PostedBy'], 'Egg')

        # Remove donors who only have donor-posted offspring
        # this means there is no bank offspring group posted
        for i, d in enumerate(Counts[b]['Unq_Donors']):
            # if no kids for this donor are NOT posted by Egg/Sperm donor
            # then remove that donor from list
            if not list(np.setdiff1d(bf.find(AllBanks[b]['DonorID'], d),
                              Counts[b]['Sp_kids']+Counts[b]['Egg_kids'])):
                del Counts[b]['Unq_Donors'][i]

        # Make list of indices for kids for each unique donor,
        # disregard kids posted by sperm or egg donor
        for d in Counts[b]['Unq_Donors']:
            Counts[b]['Donor_Inds'][d] = [x for x in bf.find(AllBanks[b]['DonorID'], d)
                                          if x not in Counts[b]['Sp_kids'] +
                                          Counts[b]['Egg_kids']]

        # Counts for non-unknown donors posted by both self and parent
        Counts[b]['Offsp_Cnt'] = [len(Counts[b]['Donor_Inds'][d]) for d in Counts[b]['Unq_Donors']]

        # Average birthyear for donor offspring
        Counts[b]['Offsp_Year'] = []
        for d in Counts[b]['Unq_Donors']:
            temp_yr_list=[]
            #print(len(Counts[b]['Donor_Inds'][d]))
            for k in Counts[b]['Donor_Inds'][d]:
                temp_yr_list.append(AllBanks[b]['Birthyear'][k])
            if temp_yr_list:
                avg_yr=np.nanmean(temp_yr_list)
            else:
                avg_yr=np.nan
            #print(temp_yr_list)
            #print(avg_yr)
            Counts[b]['Offsp_Year'].append(avg_yr)

        # Donor descriptions dictionary
        for d in Counts[b]['Unq_Donors']:
            Counts[b]['Donor_Desc'][d] = [AllBanks[b]['DonorDesc'][x] for x in
                                          Counts[b]['Donor_Inds'][d]]
    return Counts


# -----------
# Reformat description strings organized by donor,
# split all entries on periods, take only unique entries
# -----------
def desc_split(Counts, banklist):

    DescList = {}
    for b in banklist:
        DescList[b] = {}
        for d in Counts[b]['Unq_Donors']:
            DescList[b][d] = {
                'AllText': [],
                'Weight': [],
                'Height': [],
                'BloodType': [],
                'Eyes': [],
                'Jewish': [],
                'AA': [],
                'Latino': [],
                'Pairs': []
                }
            for lst in Counts[b]['Donor_Desc'][d]:
                if type(lst) is str:
                    DescList[b][d]['AllText'].extend(lst.split('. '))
            # strip leading space
            DescList[b][d]['AllText'] = [t.strip() for t in DescList[b][d]['AllText']]
            # keep only unique entries (note there will still be overlap)
            DescList[b][d]['AllText'] = list(set(DescList[b][d]['AllText']))
            # remove empty strings
            if '' in DescList[b][d]['AllText']:
                DescList[b][d]['AllText'].remove('')

            # Most entries contain weight and height, potentially many times,
            # put these in their own fields
            DescList[b][d]['Weight'] = [DescList[b][d]['AllText'][f] for f in
                                        bf.findincludes_list
                                        (DescList[b][d]['AllText'],
                                        ['Weight: '])]
                                        #['Weight', 'weight'])]

            # Most entries contain weight and height, potentially many times,
            # put these in their own fields
            DescList[b][d]['Height'] = [DescList[b][d]['AllText'][f] for f in
                                        bf.findincludes_list
                                        (DescList[b][d]['AllText'],
                                        ['Height', 'height'])]

            # Blood type
            DescList[b][d]['BloodType'] = [DescList[b][d]['AllText'][f]
                                           for f in bf.findincludes_list
                                           (DescList[b][d]['AllText'],
                                           ['Blood type '])]
                                           #['Blood Type', 'blood type',
                                           # 'Blood type', 'blood Type'])]

            # Eyes
            DescList[b][d]['Eyes'] = [DescList[b][d]['AllText'][f]
                                      for f in bf.findincludes_list
                                      (DescList[b][d]['AllText'],
                                      ['eyes', 'Eyes'])]

            # Jewish
            DescList[b][d]['Jewish'] = [DescList[b][d]['AllText'][f]
                                        for f in bf.findincludes_list
                                        (DescList[b][d]['AllText'],
                                        ['Jewish', 'jewish',
                                         'Jew', 'jew', 'ashkenazi',
                                         'Ashkenazi'])]

            # African/black (using black doesn't work, gives you karate black
            # belts and black hair), most list "african american" or specific
            # african ancestry
            DescList[b][d]['AA'] = [DescList[b][d]['AllText'][f]
                                    for f in bf.findincludes_list
                                    (DescList[b][d]['AllText'],
                                    ['African', 'african'])]

            # Latino & Hispanic, this list of descriptors will need expanding
            DescList[b][d]['Latino'] = [DescList[b][d]['AllText'][f]
                                        for f in bf.findincludes_list
                                        (DescList[b][d]['AllText'],
                                        ['Mexican', 'mexican', 'Latino',
                                         'latino', 'Hispanic', 'hispanic',
                                         'Cuban', 'cuban', 'Latin-american',
                                         'Peru', 'peru', 'Puerto', 'Dominican',
                                         'dominican', 'Brazil', 'brazil',
                                         'venez', 'Venez', 'Salvador',
                                         'salvador', 'Guatemal', 'guatemal',
                                         'Colombia', 'colombia', 'Hondura',
                                         'hondura', 'Equador', 'equador',
                                         'Bolivia', 'bolivia'])]

            for f in bf.findincludes_list(DescList[b][d]['Latino'],
                                          ['food', 'Food', 'movie', 'nut']):
                del DescList[b][d]['Latino'][f]
            
            # Find text indicating possible pairs of donors
            DescList[b][d]['Pairs'] = [DescList[b][d]['AllText'][f]
                                    for f in bf.findincludes_list
                                    (DescList[b][d]['AllText'],
                                    # ['same donor','Same donor','same donor'])] 
                                    ['Same', 'same', 'Donor', 'donor', 'CCB', 'NECC', 
                                    'Fairfax', 'Xytex', 'TSBC', 'Cryogenic'])]

    return DescList


# ---------
# Organize text information into categorical lists for plots
# ----------
# cats1 are fields that should be divided into a simple yes/no
# based on an entry existing or not in that field in DescList
# cats2 are fields that are multiple yes/no categories pulled from a
# single field
def desc_cat(DescList, Counts, banklist, cats1, cats2):

    # this is lower case for eyes, cats2 is specific to eyes here, need to fix)
    eye_cats_lwr = ['blue', 'green', 'hazel', 'brown']

    DescCat = {}
    for b in banklist:
        DescCat[b] = {}
        # Make field in dictionary for each category
        for c in cats1 + cats2:
            DescCat[b].update({c: []})
        # Loop through individual donors in the same order as Counts
        for d in Counts[b]['Unq_Donors']:
            # Enter a 1 if category is non-empty, 0 if empty
            for categ in cats1:
                if DescList[b][d][categ]:
                    DescCat[b][categ].extend([1])
                if not DescList[b][d][categ]:
                    DescCat[b][categ].extend([0])
            # cats2 all read from same field in DescList
            for i, eye in enumerate(cats2):
                if bf.findincludes_list(DescList[b][d]['Eyes'],
                                        [eye, eye_cats_lwr[i]]):
                                        DescCat[b][eye].extend([1])
                if not bf.findincludes_list(DescList[b][d]['Eyes'],
                                            [eye, eye_cats_lwr[i]]):
                                            DescCat[b][eye].extend([0])
    return DescCat

# function for formatting text categories that take on a multiple values
# here written for bloodtype, but can be made to be more general
def cont_cat(DescList, Counts, banklist, contcats):
    ContCat = {}
    for b in banklist:
        ContCat[b] = {}
        # Make field in dictionary for each category
        for c in contcats:
            ContCat[b].update({c: []})
        # Loop through individual donors in the same order as Counts
        for d in Counts[b]['Unq_Donors']:
            # Put descriptions into an ordered list
            for categ in contcats:
                if categ == 'BloodType':
                    if DescList[b][d]['BloodType']:
                        templist=[]
                        for ent in DescList[b][d]['BloodType']:
                            templist.append(DescList[b][d]['BloodType'][0][11:].strip('.'))
                        ContCat[b][categ].append(templist)
                    else:
                        ContCat[b][categ].append([])    
    return ContCat

# function for formatting text categories that take on a multiple values
# But no filtering or reshaping of list
# convert categorical list of lists to 0/1 valued vectors depending on category
def convert_cat(List_vals, list_cat, banklist, categories):
    convert_cat={}
    for b in banklist:
        convert_cat[b]={}
        for c in categories:
            convert_cat[b].update({c: []})
        for val in List_vals[b][list_cat]:
            for c in categories:
                if bf.findincludes(val,c):
                    convert_cat[b][c].extend([1])
                else:
                    convert_cat[b][c].extend([0])

            #print(single, c, convert_cat[b][c][-1], len)co
    return convert_cat


def parse_weight(wt_list):
    wt_list_out = wt_list.copy()
    units=[]
    pound_list=[]
    for i, wt in enumerate(wt_list):
        units.append([])
        wt_list_out[i] = [st.split('Weight:')[-1].strip() for st in wt]
        #print(wt_list_out[i])
        for k,w in enumerate(wt_list_out[i]):
            if 'ft' in w or "\'" in w or '\"' in w or '/' in w or 'Normal' in w or 'Medium Build' in w or 'Thin' in w or 'Slim' in w:
                wt_list_out[i][k] = ''
                units[i].append('')
                continue
            if w == '58 kg (128 lbs)':
                wt_list_out[i][k] = 128
                units[i].append('')
                continue
            if w == '175lbs (80kg)':
                wt_list_out[i][k] = 175
                units[i].append('')
                continue
            if w == '161 (73 kg)':
                wt_list_out[i][k] = 161
                units[i].append('')
                continue
            if w == '76 (168 lbs)':
                wt_list_out[i][k] = 168
                units[i].append('')
                continue
            if w == '? maybe 185':
                wt_list_out[i][k] = 185
                units[i].append('')
                continue
            # if w == '180 lbs (81kg)':
            #     wt_list_out[i][k] = 180
            #     units[i].append('')
            #     continue
            spl=bf.last_digit_loc(wt_list_out[i][k])
            if spl and spl<len(w)-1:
                units[i].append(w[spl+1:].strip())
                wt_list_out[i][k]=w[:spl+1]
            else:
                units[i].append('')
            if '--' in wt_list_out[i][k]:
                 wt_list_out[i][k] = np.mean([float(w) for w in wt_list_out[i][k].strip(' ').split('--')])
            elif '-' in wt_list_out[i][k]:
                 wt_list_out[i][k] = np.mean([float(w) for w in wt_list_out[i][k].strip(' ').split('-')])
            else:
                try:
                    float(wt_list_out[i][k])
                except ValueError:
                    #print("Not a float")
                    wt_list_out[i][k] = ''
                else:
                    wt_list_out[i][k] = float(wt_list_out[i][k])
                    if units[i][k]=='kg' or units[i][k]=='kgs':
                        wt_list_out[i][k]=2.20462*wt_list_out[i][k]
        #print(wt_list_out[i])
    for i, wt in enumerate(wt_list_out):
        mn_w=[w for w in wt if w is not '' and w >120 and w < 300]
        pound_list.extend([np.mean(mn_w).tolist()])
    return(pound_list)
 

# -------------
# Arrange count-per donor data, bank id, individual donor ids, offpring birth
# year into a list of lists for plotting/reference.
# lists are appended in order of banklist
# --------------
def cnts_list(Counts, banklist):

    list_allcnts = []
    allbanks_cnts = []
    donorid_list = []
    allbanks_bkind = []
    allbanks_offspyr = []

    for i, b in enumerate(banklist):
        list_allcnts.append(Counts[b]['Offsp_Cnt'])
        allbanks_cnts = allbanks_cnts + Counts[b]['Offsp_Cnt']
        donorid_list = donorid_list + Counts[b]['Unq_Donors']
        allbanks_bkind = allbanks_bkind + [i]*len(Counts[b]['Offsp_Cnt'])
        allbanks_offspyr = allbanks_offspyr + Counts[b]['Offsp_Year']
    list_allcnts.append(allbanks_cnts)

    return(allbanks_cnts, allbanks_bkind, list_allcnts, donorid_list, allbanks_offspyr)


# -------------
# Arrange feature data into list for all banks
# for plotting, lists are appended in order of banklist
# --------------
def feat_list(DescCat, banklist, cats):
    allbanks_cat = {}

    # initialize fields in dictionary
    for c in cats:
        allbanks_cat.update({c: []})
    for b in banklist:
        for c in cats:
            allbanks_cat[c] = allbanks_cat[c] + DescCat[b][c]
    return allbanks_cat


# Function to compile multiple categories into a single categorical list
# with integer entries. This function generates a unique integer for
# every possible combination of categories, use for "like" features
# (like eye color), label is a shorter reference to each category (use for
# generating shorter labels per integer automatically).
# ------------------
def compile_cat(allbanks_cat, cats, lab):

    comp_cat = []
    # loop through categories, 1 X len(cats) list, entry of for each category
    for c in cats:
        comp_cat.append(allbanks_cat[c])

    # loop through groups of all possible sizes
    k = 1
    cat_out = [0]*len(allbanks_cat[cats[0]])
    cat_lab = ['None']
    for n in range(1, len(cats)+1):
        for i in it.combinations(range(0, len(cats)), n):
            temp = []
            lab_temp = ''
            for _ in i:
                # make temporary list of lists for this grouping
                temp.append(comp_cat[_])
                # make label entry
                lab_temp += lab[_]
                lab_temp += '/'
            lab_temp = lab_temp[:-1]
            new_inds = bf.find(list(np.prod(np.array(temp), 0)), 1)
            for b in new_inds:
                # Enter value k for all with this combo.
                # Note that higher values (more categories) overwrite lower.
                cat_out[b] = k
            cat_lab.append(lab_temp)
            k = k+1
    return (cat_out, cat_lab)


# Recategorize data into fewer categories
# red_cats is a list of lists, each entry is input categories to group.
# Entries in comp_cat entries that match red_cats[i] will be changed to i.
# Values not included red_cats are [] in output
# -------------------
def reduce_cat(comp_cat, red_cats):
    red_out = [[] for i in range(len(comp_cat))]
    for k, r in enumerate(red_cats):
        inds = bf.find_list(comp_cat, r)
        for i in inds:
            red_out[i] = k
    return red_out


# -----------------
# Function to concatenate all categories into lists over all donors that
# that include text
# -----------------
def desc_text_list(DescList, Counts, banklist, cats):
    DescTextList = {}
    for c in cats:
        DescTextList.update({c: []})
    for b in banklist:
        # Loop through individual donors in the same order as Counts
        for d in Counts[b]['Unq_Donors']:
            # Enter a 1 if category is non-empty, 0 if empty
            for categ in cats:
                DescTextList[categ].append(DescList[b][d][categ])
    return DescTextList


# -----------------
# Input list of lists of strings
# Join strings in each sub-list with input string in beetween
# Output list of concatenated strings
# -----------------
def single_desc_list(InputList, joinstr):
    SingleTextList = []
    for s in InputList:
        SingleTextList.append(joinstr.join(s))
    return SingleTextList


# ----------
# NLP functions
# ----------
# function to tokenize, stem & remove stop words from a language string
# ----------
def clean_split_stem(rawstring):
    stop = stopwords.words('english')
    out_str = rawstring.split()
    porter = PorterStemmer()
    out_str = [porter.stem(word) for word in out_str]
    out_str = [word for word in out_str if word not in stop]
    return out_str


# ----------
# function to calculate euclidean distance over all possible pairs of vectors
# ----------
def dist_all(vect_in):
    # DistAll=np.empty(shape=(len(vect_in),len(vect_in)))
    # DistAll[:] = np.NAN
    DistAll = []
    Coords = []
    for j in it.combinations(range(0, len(vect_in)), 2):
        DistAll.extend([scipy.spatial.distance.euclidean(vect_in[j[0]], vect_in[j[1]])])
        Coords.extend([j])
        # DistAll[j[0]][j[1]]=scipy.spatial.distance.euclidean(vect_in[j[0]],vect_in[j[1]])
    return (DistAll, Coords)
    
    
    

