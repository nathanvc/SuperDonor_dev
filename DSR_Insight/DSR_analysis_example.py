# -*- coding: utf-8 -*-
"""
2/12/2016 - 7/25/2016

@author: nathanvc

Analysis of data from the donor sibling registry
Sample set of 32 banks
Initial descriptive analysis of 6 banks winter 2016
Expand to 32 banks and develop super-donor duplicate detection June/July 2016
"""

import numpy as np
import matplotlib.pyplot as plt
import DSR_basicfn as bf
import DSR_loadrawdata as ld
import DSR_reformatdata as rf
import DSR_sliderfigs as sf
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfTransformer

pairs = ld.load_pairs('../DSR_rawdata_update/DSR_multibank_donors.xlsx')

# Load and clean all raw data, organized as 1 file per bank in directory
# ------------------
d = '../DSR_rawdata_update/DSR_rawdata_6_6_2016.xlsx'
(AllBanks, banklist) = ld.load_clean_allbanks(d)

# -----------------
# GROUP SIZE ANALYSIS
# -----------------
# Generate dictionary with counts per donor,
# designation of who posted, and description list
# organized by bank
Counts = rf.offsp_cnts(AllBanks, banklist)

# Arrange count-per donor data into a list of lists, final entry is full sample
(allbanks_cnts, allbanks_bkind, list_allcnts, donorid_list) = rf.cnts_list(Counts, banklist)

# calculate mean, median & std deviation per bank
bk_mean = [np.mean(list_allcnts[i]) for i in range(len(list_allcnts))]
bk_median = [np.median(list_allcnts[i]) for i in range(len(list_allcnts))]
bk_std = [np.std(list_allcnts[i]) for i in range(len(list_allcnts))]

# ticklabels and locations for plotting
ticklab = banklist[:]
ticklab.append('Total')
index = np.arange(len(ticklab))

# Make Plot of Counts per individual donor, different color per bank
# -----------
plt.figure(0)
colors = plt.cm.rainbow(np.linspace(0, 1, len(banklist)))
bank_cnt = []
print('---')
for b, c in zip(banklist, colors):
    print(b)
    plt.scatter(np.sum(bank_cnt)+np.arange(len(Counts[b]['Unq_Donors'])),
                Counts[b]['Offsp_Cnt'], color=c)
    bank_cnt.append(len(Counts[b]['Unq_Donors']))
    plt.legend(banklist, loc=2, fontsize=15)
    plt.ylabel('Offspring Count per Donor', fontsize=15)
    plt.xlabel('Individual Donors', fontsize=15)
    plt.xlim(-50,4000)
plt.show()

# -----------
# OFFSPRING SEX ANALYSIS
# -----------
# Generate structure with Female/Male Counts
# Output organized by who posted the offspring
# (Offspring, Parent, Egg or Sperm donor)
# FM_Counts = rf.FM_Counts(AllBanks, banklist, Counts)

# Bar plots of counts & proportions divided by sex, separate by who posted
# ----------
# NOTE: offspring posted by parents are disproportionately male
# NOTE: offspring posted by self are biased towards female (~3:1 ratio)

#bar_width = 0.35
#opacity = 0.4
#f_ind = 2
#for key in ['Parent','Offspring']:
#
#    # Plot raw counts by bank
#    plt.figure(f_ind)
#    plt.subplot(2, 1, 1)
#    plt.bar(index, FM_Counts[key]['F_cnt'], bar_width,
#            alpha=opacity, color='g')
#    plt.bar(index+bar_width, FM_Counts[key]['M_cnt'], bar_width,
#            alpha=opacity, color='c')
#    plt.title('Posted by ' + key)
#    plt.xticks(index + bar_width, ticklab)
#    plt.ylabel('Offspring Count')
#    plt.legend(('F', 'M'), loc=2)
#
#    # plot proportions by bank
#    plt.subplot(2, 1, 2)
#    plt.bar(index, FM_Counts[key]['F_prop'], bar_width,
#            alpha=opacity, color='g')
#    plt.bar(index+bar_width, FM_Counts[key]['M_prop'], bar_width,
#            alpha=opacity, color='c')
#    plt.xticks(index + bar_width, ticklab)
#    plt.ylabel('Proportion')
#    plt.ylim(0, 0.9)
#    plt.show()
#    f_ind = f_ind + 1
#
#
## Plot comparison of M:F ratio (difference from 1) to world and US average
## for offspring posted by parent
## ---------------
#plt.figure(4)
#plt.bar(index+bar_width/2, FM_Counts['Parent']['MF_ratio'],
#        bar_width, alpha=opacity, color='b')
#plt.xticks(index + bar_width, ticklab)
#plt.plot([0, len(ticklab)], [0.04, 0.04], color='g')
#plt.plot([0, len(ticklab)], [0.06, 0.06], color='r')
#plt.ylabel('M/F, difference from 1')
#plt.legend(('US', 'World'))
#plt.plot([0, len(ticklab)], [0, 0], color='k')
#plt.title('M:F ratio comparison, posted by Parent')
#plt.ylim(-0.12, 0.3)
#plt.show()


# -----------
# LANGUAGE ANALYSIS OF DESCRIPTIONS AND DONOR FEATURES
# -----------
# Reformat description strings organized by donor,
# split all entries on '. ', keep only unique entries
DescList = rf.desc_split(Counts, banklist)

# -----
# organize substrings into fields by height, weight, eye color,
# blood type, race/ethnicity
# -----
# features that map to single field
feat_cats = ['Jewish', 'AA', 'Latino', 'AllText']
# multiple features read out from single field
eye_cats = ['Blue', 'Green', 'Hazel', 'Brown']
DescCat = rf.desc_cat(DescList, Counts, banklist, feat_cats, eye_cats)

# -------------
# Arrange categorical data into big list of all entries, indexed by
# donorid list (all donor ids concatentated in order of banklist, see
# cnts_list fn at top)
# --------------
allbanks_cat = rf.feat_list(DescCat, banklist, feat_cats + eye_cats)

# eye color analysis
# ----------
# shorter label for eye colors
eye_lab_sh = ['Bl', 'Gr', 'H', 'Br']
# compile categorical data into single list and corresponding labels
(allbanks_eyecat, eye_lab) = rf.compile_cat(allbanks_cat, eye_cats, eye_lab_sh)


# recategorize so that all colors with multiple colors listed are in one group
allbanks_eyecat_red = rf.reduce_cat(allbanks_eyecat,
                                    [[0], [1], [2], [3], [4], [5, 6, 7, 8, 9,
                                     10, 11, 12, 13, 14, 15]])
eye_lab_red = ['None', 'Blue', 'Green', 'Hazel', 'Brown', 'Multi']


# cut out the zero ('none' values)
allbanks_eyecat_cull = [allbanks_eyecat_red[i] for i, j in
                        enumerate(allbanks_eyecat_red) if j > 0]
allbanks_cnts_eyecull = [allbanks_cnts[i] for i, j in
                         enumerate(allbanks_eyecat_red) if j > 0]


# ------------------
# MAKE INTERACTIVE SLIDER PLOTS
# ------------------
# Interactive slider plots of group size
# -----------
def bank_slider(allbanks_cnts=allbanks_cnts, allbanks_bkind=allbanks_bkind,
                banklist=banklist):
    poss_cat = range(0, len(banklist))
    cs = plt.cm.rainbow(np.linspace(0, 1, len(poss_cat)))
    plt.figure()
    sf.winslider(allbanks_cnts, allbanks_bkind, poss_cat, banklist, cs,
                 'Banks & Group Size')


def bar_bank_slider(allbanks_cnts=allbanks_cnts, allbanks_bkind=allbanks_bkind,
                    banklist=banklist):
    poss_cat = range(0, len(banklist))
    cs = plt.cm.rainbow(np.linspace(0, 1, len(poss_cat)))
    plt.figure()
    sf.barslider(allbanks_cnts, allbanks_bkind, poss_cat, banklist, cs,
                 'Banks & Group Size')


# Make interactive slider plots of eye color
# ------------
def eye_slider():
    poss_cat = range(0, 6)
    cs = ['gray', 'cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.winslider(allbanks_cnts, allbanks_eyecat_red, poss_cat, eye_lab_red,
                 cs, 'Eye Color & Group Size')


# Make interactive slider plot of eye color,
# removing donors with no reported value
def eye_slider_cull():
    poss_cat = range(1, 6)
    cs = ['cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.winslider(allbanks_cnts_eyecull, allbanks_eyecat_cull, poss_cat,
                 eye_lab_red[1:], cs, 'Eye Color & Group Size, reported only')


# Make interactive slider plot of eye color,
# removing donors with no reported value
def bar_eye_slider_cull():
    poss_cat = range(1, 6)
    cs = ['cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.barslider(allbanks_cnts_eyecull, allbanks_eyecat_cull, poss_cat,
                 eye_lab_red[1:], cs, 'Eye Color & Group Size, reported only')



# ----------
# NLP Description, detect donor similarity, beginning steps...
# ----------
# concatenate "All Text" into big list organized by donors
# indexing of donors is same as alldonors_list
AllText_AllDon = rf.desc_text_list(DescList, Counts, banklist, ['AllText'])
SingleText_AllDon = rf.single_desc_list(AllText_AllDon['AllText'], ' ')
# split up, remove stop words, tokenize, stem
Split_AllDon = [rf.clean_split_stem(st) for st in SingleText_AllDon]
# rejoin tokenized version of description
Rejoin_Clean = rf.single_desc_list(Split_AllDon, ' ')
docs = np.array(Rejoin_Clean)

# make bag of words for each donor (sparse matrix form)
count = CountVectorizer()
# calculate tf-idf
tfidf = TfidfTransformer()
np.set_printoptions(precision=2)
don_bags_tfidf = tfidf.fit_transform(count.fit_transform(docs)).toarray()

# Calculate euclidean distance for all donors (this takes a long time)
# (Dist_All, Coords) = rf.dist_all(don_bags_tfidf)

# --------------
# ANALYSIS OF FAMILY GROUPS
# --Assumption: all offspring posted with same user name are same family
# --This analysis doesn't make much sense for subsampled data
# --------------
alluserID = []
userID_indiv_len = []
for b in banklist:
    alluserID = alluserID+AllBanks[b]['UserID']
    userID_indiv_len.append(len(set(AllBanks[b]['UserID'])))
alluserID = list(set(alluserID))
# If Num_crosslist > 0, indicates there are user IDs that list
# children from multiple banks
Num_crosslist = sum(userID_indiv_len)-len(alluserID)

# ----------------
# Count number of kids, banks, and donors per userID
# ----------------
UserID_cnt = {
    'UserIDinds': {},
    'DonorID_user': {},
    'kidcnt': [],
    'bankcnt': [],
    'donorcnt': []
}
for u in alluserID:
    bankcount = 0
    kidcount = 0
    donorcount = 0
    UserID_cnt['UserIDinds'][u] = {}
    UserID_cnt['DonorID_user'][u] = []

    for b in banklist:
        UserID_cnt['UserIDinds'][u][b] = bf.find(AllBanks[b]['UserID'], u)
        if UserID_cnt['UserIDinds'][u][b]:
            bankcount += 1
            UserID_cnt['DonorID_user'][u].append(set([AllBanks[b]['DonorID'][x]
                                                 for x in UserID_cnt['UserIDinds'][u][b]]))
            donorcount += len(UserID_cnt['DonorID_user'][u])
        kidcount += len(UserID_cnt['UserIDinds'][u][b])

    UserID_cnt['kidcnt'].append(kidcount)
    UserID_cnt['bankcnt'].append(bankcount)
    UserID_cnt['donorcnt'].append(donorcount)


# from census, 1 child, 15.9million, 2 child 13.4 million, 3 children,
# 5.4 million, 4 children 2.4 million, 2012 census


# Printout to look more carefully for pair training set
# for b in banklist:
#     for d in Counts[b]['Unq_Donors']:
#         if DescList[b][d]['Pairs']:
#             print(b, d, DescList[b][d]['Pairs'])

#----------------------
# Examine pair descriptions
#----------------------

pairs = ld.load_pairs('../DSR_rawdata_update/DSR_multibank_donors.xlsx')

for i,p in enumerate(pairs):
    print(p)
    if DescList[p[0][0]][p[0][1]]['AllText']:
        DescList[p[0][0]][p[0][1]]['AllText']
    else:
        print('no pair 0')
    if DescList[p[1][0]][p[1][1]]['AllText']:
        DescList[p[1][0]][p[1][1]]['AllText']
    else:
        print('no pair 1')
    print('---')    


# ------------------
# MAKE INTERACTIVE SLIDER PLOTS
# ------------------
# Interactive slider plots of group size
# -----------
def bank_slider(allbanks_cnts=allbanks_cnts, allbanks_bkind=allbanks_bkind,
                banklist=banklist):
    poss_cat = range(0, len(banklist))
    cs = plt.cm.rainbow(np.linspace(0, 1, len(poss_cat)))
    plt.figure()
    sf.winslider(allbanks_cnts, allbanks_bkind, poss_cat, banklist, cs,
                 'Banks & Group Size')


def bar_bank_slider(allbanks_cnts=allbanks_cnts, allbanks_bkind=allbanks_bkind,
                    banklist=banklist):
    poss_cat = range(0, len(banklist))
    cs = plt.cm.rainbow(np.linspace(0, 1, len(poss_cat)))
    plt.figure()
    sf.barslider(allbanks_cnts, allbanks_bkind, poss_cat, banklist, cs,
                 'Banks & Group Size')


# Make interactive slider plots of eye color
# ------------
def eye_slider():
    poss_cat = range(0, 6)
    cs = ['gray', 'cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.winslider(allbanks_cnts, allbanks_eyecat_red, poss_cat, eye_lab_red,
                 cs, 'Eye Color & Group Size')


# Make interactive slider plot of eye color,
# removing donors with no reported value
def eye_slider_cull():
    poss_cat = range(1, 6)
    cs = ['cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.winslider(allbanks_cnts_eyecull, allbanks_eyecat_cull, poss_cat,
                 eye_lab_red[1:], cs, 'Eye Color & Group Size, reported only')


# Make interactive slider plot of eye color,
# removing donors with no reported value
def bar_eye_slider_cull():
    poss_cat = range(1, 6)
    cs = ['cornflowerblue', 'sage', 'darkkhaki', 'sienna', 'mediumpurple']
    plt.figure()
    sf.barslider(allbanks_cnts_eyecull, allbanks_eyecat_cull, poss_cat,
                 eye_lab_red[1:], cs, 'Eye Color & Group Size, reported only')

'''
# ----------
# NLP Description, detect donor similarity, beginning steps...
# ----------
# concatenate "All Text" into big list organized by donors
# indexing of donors is same as alldonors_list
AllText_AllDon = rf.desc_text_list(DescList, Counts, banklist, ['AllText'])
SingleText_AllDon = rf.single_desc_list(AllText_AllDon['AllText'], ' ')
# split up, remove stop words, tokenize, stem
Split_AllDon = [rf.clean_split_stem(st) for st in SingleText_AllDon]
# rejoin tokenized version of description
Rejoin_Clean = rf.single_desc_list(Split_AllDon, ' ')
docs = np.array(Rejoin_Clean)

# make bag of words for each donor (sparse matrix form)
count = CountVectorizer()
# calculate tf-idf
tfidf = TfidfTransformer()
np.set_printoptions(precision=2)
don_bags_tfidf = tfidf.fit_transform(count.fit_transform(docs)).toarray()
'''



# Make box & whisker plots for donor count for each bank
# -----------
#
# plt.figure(1)
# ticklab = banklist[:]
# ticklab.append('Total')
# index = np.arange(len(ticklab))
# colors = plt.cm.rainbow(np.linspace(0,1,len(banklist)))
# bank_cnt=[]
# for b, c in zip(banklist, colors):
#    plt.boxplot(list_allcnts)
#    bank_cnt.append(len(Counts[b]['Unq_Donors']))
#    plt.xticks(index+1,ticklab)
#    plt.ylabel('Offspring Count per Donor')
#    plt.title('Distribution of Offspring Cnt per Donor')
# plt.show()

# # Plot the normalized histogram of counts per donor
# # color plot for bank over gray plot for overall average
# # Note I have not normalized for the different sample sizes from each bank
# # This means that CCB dominates the average
# #------------
# f = plt.figure()
# for i, l in enumerate(zip(banklist, colors)):
#    plt.subplot(len(banklist)/2,2,i+1)
#    plt.hist(list_allcnts[-1],color = 'k',
#             bins = np.arange(1,70,5), normed = 1, alpha = 0.3)
#    plt.hist(list_allcnts[i],color = l[1],
#             bins = np.arange(1,70,5), normed = 1, alpha = 0.3)
#    plt.title(l[0])
# f.set_figheight(15)
# f.set_figwidth(15)
# plt.show()

# Reformat dictionary into dataframe containing entries for all banks
# -----------
# df_temp = {}
# print('-----')
# for bank in banklist:
#    print(bank)
#    df_temp[bank]=pd.DataFrame.from_dict(AllBanks[bank])
# df_bk = pd.concat(df_temp, ignore_index=True)
# 
# count of entries per donor (not yet excluding direct donor offspring):
# test_group = df_bk.groupby('DonorID')['Bank'].size()
# 
# syntax for making dataframe for posted by parent
# df_par = df_bk[df_bk['PostedBy']=='Parent']
# 
# syntax for making dataframe for posted by offspring
# df_offsp = df_bk[df_bk['PostedBy']=='Offspring']
# 
# dataframe of only posted by parent or offspring (no nan, no sperm or egg donors)
# df_paroff = pd.concat([df_bk[df_bk['PostedBy']=='Offspring'], df_bk[df_bk['PostedBy']=='Parent']])
# 
# count offspring per donor (only offspring and parent postings)
# offsp_count = df_paroff.groupby('DonorID')['Bank'].size()
# 
# count offspring per donor (only offspring and parent postings)
# offsp_count = df_paroff.groupby(['Bank','DonorID']).size()
# 
# plot donor count, all one color
# plt.figure()
# offsp_count.plot(style = 'o')
# 
# plot grouped by bank
# for b, c in zip(banklist, colors):
#   temp_df = offsp_count[b]
#   plt.figure()
#   temp_df.plot(style='o')
#   plt.title(b)
#   plt.show()
    





# example of sorting by donor ID and bank (some banks may duplicate donor IDs)
# df_bk.sort_index(by=['DonorID','Bank'])['DonorID','Bank']


# #bad first plot of donor counts
# test_group.plot(style='o')

# sns.FactGrid(data=test_group)


# df = pandas.DataFrame({
#     'Height (cm)': numpy.random.uniform(low=130, high=200, size=N),
#     'Weight (kg)': numpy.random.uniform(low=30, high=100, size=N),
#     'Gender': numpy.random.choice(_genders, size=N)
# })
# 
# fg = seaborn.FacetGrid(data=df, hue='Gender', hue_order=_genders, aspect=1.61)
# fg.map(pyplot.scatter, 'Weight (kg)', 'Height (cm)').add_legend()

