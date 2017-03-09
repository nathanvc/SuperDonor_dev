"""
Created on Wed Mar  2 14:39:23 2016
Updated 2/2017-3/2017

Scraping functions for the donor sibling registry: url_ = 'https://www.donorsiblingregistry.com'

@author: Jeff Mayse, soup functions for loading search url for looping through search (iDict)
@author: Nathan V-C, functions for loading bank data and later analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import spermBank as sbnk
from bs4 import BeautifulSoup
from urllib.request import urlopen

#-------------
#Functions for pulling and organizing data from the search url:'https://www.donorsiblingregistry.com/members/search'
#-------------

# Pull html info from the database search URL using urlopen
def open_url(url_):
    data_ = None
    data_ = urlopen(url_)
    if data_ is not None: #Type check
        return data_
    else:
        print('Call to url{0} failed'.format(url_))


# Convert html_ info from urlopen to soup 
def html_to_soup(html_):
    soup = BeautifulSoup(html_, 'html.parser')
    return soup


# Global search URL creator
def create_search_URL(bdYear = '',bdMo = '',bdDay = '',dType = '',subbedBy = '',facilID = '',facilState = '', facilCountry = ''):
    #Check if all inputs are blank
    if all([bdYear == '',bdMo == '',bdDay == '',dType == '',subbedBy == '',facilID == '',facilState == '', facilCountry == '']):
        print('Error: You must provide at least one argument and use the following keywords: \
        {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format('bdYear', 'bdMo', 'bdDay',
        'dType', 'subbedBy', 'facilID', 'facilState', 'facilCountry'))
        return -1
        
    search_url = """https://donorsiblingregistry.com/members/ListRegistry?keyword=&dtDonorYear={0}&dtDonorMonth={1}&dtDonorDay={2}&dpTypeID={3}&dpIdentityNumber=&faID={5}&usUserName_startswith=&usTypeID={4}&faCity_contains=&faStateID={6}&faCountryID={7}&dpDateCreated_isgreaterthan=&doSearch=Search+Registry&userBrowse=1&userSearch=1&""".format(bdYear, bdMo, bdDay, dType, subbedBy, facilID, facilState, facilCountry)
        
    return search_url
        
def find_form_ids_facil(soup):
    out = dict([]) #Initialize dict
    
    #Find dropdown lists
    form_info = soup.find_all('select', attrs={'class' : 'form-select'}) 
    
    if form_info:
        for forms in form_info:
            ids = []
            names = []
            
            #Find the parent of the dropdown list, which contains the id
            formParent = forms.parent('select')
            
            #Results from findAll must be iterated as lists to use .get
            for item in formParent:
                name_string = item.get('id') #Get id attribute value
                name_split = name_string.rsplit('-') #format is xx-xx-xx-xx, split on hyphen
                name_sep = name_split[-2:] # Take the last two components for unique ID
                name_ = name_sep[0] + '_' + name_sep[1] #Combine them with underscore separator
                if name_ is None: #Check output
                    print('Could not parse name at {0}'.format(item))
                    return -1
            
            out[name_]={}
            
            #Results from findAll must be iterated as lists to use .get
            for option in forms.findAll('option'):
                
                #Append each value to fresh ids list initialized above
                ids.append(option.get('value'))
                # names.append(option.getText()) #This isn't right but I have to dig back into it to get the right call
                names.append(option.getText())
                
                #Check output
                if ids is None:
                    print('Could not parse ids at {0}'.format(name_))
                    return -1
            
            #Assign ids in dropdown list to name_ key in the out dict            
            out[name_]['id'] = ids
            out[name_]['names'] = names
            
    return out

# --------------
# Functions for loading and initial cleaning/organizing of database data
# set up to load by donor type, generating a DF organized by the original listings, and one organized by offspring
# --------------

# Make beautiful soup object from url
def massage_search(search_url):
    
    soup = BeautifulSoup(open_url(search_url), 'html.parser')
    
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

    return soup

# pull message and posting dates
def postdates(drow):
    temp=drow.findAll('td')[2]
    
    # decompose the elements we are done with:
    for st in temp.findAll('strong'):
        st.decompose()
    for a in temp.findAll('a'):
        a.decompose()
    for im in temp.findAll('img'):
        im.decompose()
    
    # get the leftover text:     
    text = temp.get_text(separator='|')
    
    # clean up list
    text_l=text.strip('.').strip('\n').strip('|').split('|')
    text_l=[t.strip(' ') for t in text_l]
    
    # loop through list and make posted and updated dates
    p_date = np.nan
    u_date = np.nan
    for t in text_l:
        if 'posted' in t:
            p_date = t.split(' ')[-1]
        if 'Updated' in t:
            u_date = t.split(' ')[2]
        
    return (p_date, u_date)

# make message_indicator, pull login name ids from login url
def scr_offsp(drow):
    pstby=np.nan
    offsp_l=[]
    l_name=np.nan
    usID=np.nan
    dpID=np.nan
    m_ind=0
    
    # list of kid descriptions
    for k in drow.findAll('td')[2].findAll('strong'):
        offsp_l.append(k.get_text().replace(u'\xa0', ' '))
    
    # posted by
    if drow.findAll('td')[2].find('img'):
        pstby = drow.findAll('td')[2].find('img').attrs['title'].split(' ')[-1]
    
    # pull out message indicator (1 if message posted), login name, & url ids for poster
    for i in drow.findAll('td')[2].findAll('a'):
        if i.get_text() == 'message':
            m_ind = 1;
        else:
            l_name = i.get_text() 
            usID = i.attrs['href'].split('&')[1].split('=')[1]
            dpID = i.attrs['href'].split('&')[-1].split('=')[1]
            
            
    # remove elements already used from the row and use remaining text to grab posted and updated dates
    p_date, u_date = postdates(drow)
    
    return (offsp_l, pstby, l_name, usID, dpID, p_date, u_date)

# count number of times a word appears in offspring list
def split_gen(offsp, word):
    all_txt=''
    for i, o in enumerate(offsp):
        if i>0:
            all_txt += ' '
        all_txt += o
    # return all_txt
    return all_txt.lower().split().count(word) 

# pull birthdate for an individual offspring
def birthdates(offsp):
    date_list=[]
    for i in offsp:
        if 'born' in i:
            date_list.append(i.split('born')[-1].strip())
    if len(date_list)==1:
        date_list=date_list[0]
    return date_list

# add a column combining bank_id with donor id
# should be unique for each listing even if donor numbers repeat across banks
def bankdonid(row):
    return str(int(row['bankid'])) + '_' + str(row['don_id'])

# Creates the dataframe for a particular sperm bank, each row is a "family" listing
# THIS IS THE MAIN SCRAPING FUNCTION
def make_bank_df(soup):

    bankname = soup.findAll('tr')[0].getText().replace('\n','').strip()
    bankid = soup.findAll('tr')[0].find('a').attrs['href'].split('=')[-1]
    
    # get table rows, skipping header
    data_rows = soup.find_all('tr')[3:-1] #the 1: says skip the first
    
    # initialize lists
    don_id=[]
    don_text=[]
    offsp=[]
    posted_by=[]
    lname=[]
    usID=[]
    dpID=[]
    msg_date=[]
    update=[]
    mylists = [offsp, posted_by, lname, usID, dpID, msg_date, update]
    dict_flds = ['offsp', 'posted_by', 'lname', 'usID', 'dpID', 'msg_date', 'update']
      
    # loop through all rows, putting info in lists
    for i in range(len(data_rows)):
        don_id.append(data_rows[i].findAll('td')[0].getText().replace('\n', '').replace('\r', '').replace(u'\xa0', 'nan'))
        don_text.append(data_rows[i].findAll('td')[1].getText().replace('\n', '').replace('\r', ''))
        # offsp_l, pstby, lname, usID, dpID, m_ind, p_date, u_date = scr_offsp(data_rows[i])  
        append_vals = scr_offsp(data_rows[i])
        for x, lst in zip(append_vals, mylists):
            lst.append(x)
    
    # put lists into a dictionary
    info_dict={}
    info_dict['don_id']=don_id
    info_dict['don_text']=don_text
    for z in zip(dict_flds, mylists):
        info_dict[z[0]]=z[1]
    
    # this makes a dataframe from the dictionary of scraped data
    info_df = pd.DataFrame.from_dict(info_dict)
    info_df=info_df[['don_id', 'don_text', 'posted_by', 'offsp', 'usID', 
                         'dpID', 'update', 'msg_date', 'lname']]
    info_df['bankname']=bankname
    info_df['bankid']=bankid
    
    # fill missing donor ids
    info_df['don_id']=info_df['don_id'].replace('nan', np.nan).fillna(method='ffill')

    # split offspring entries and duplicate rows, to make one row per offspring
    info_df['num_girl']=info_df['offsp'].apply(lambda x: split_gen(x, 'girl'))
    info_df['num_boy']=info_df['offsp'].apply(lambda x: split_gen(x, 'boy'))
    info_df['num_child']=info_df['offsp'].apply(lambda x: split_gen(x, 'child'))   
    
    # total kids
    info_df['num_kids']=info_df['num_girl']+info_df['num_boy']+info_df['num_child']
    
    # birth dates
    info_df['offsp_birthdates']=info_df['offsp'].apply(lambda x: birthdates(x))
    
    # combined bankdonorid columns
    info_df['bankdonorid'] = info_df.apply(bankdonid, axis=1)
        
    bank_df=info_df.copy()
    
    return bank_df

# replace an empty list with nan
def rep_empty(i):
    if isinstance(i, list):
        return np.nan
    else:
        return i
    
# pull year only from birthdate
def pull_year(bd):
    try:
        y = round(int(bd[-4:]))
    except:
        y = np.nan
    return y

# Make dataframe of scraped info about each bank
def bank_meta_info(search_url):

    soup = massage_search(search_url)
        
    bank_meta={}
    # build dictionary of bank features
    bank_meta['bankname'] = [soup.findAll('tr')[0].getText().replace('\n','').strip()]
    bank_meta['bankid'] = [soup.findAll('tr')[0].find('a').attrs['href'].split('=')[-1]]
    try:
        bank_meta['bankdesc'] = [soup.findAll('tr')[1].find('td').find('p').getText().replace('\n','').replace('\r','')]    
        # decompose extra info so only have text I want remaining
        soup.findAll('tr')[1].find('td').find('p').decompose()
    except:
        bank_meta['bankdesc'] = ''
    
    if soup.findAll('tr')[1].find('td').find('a'):
        bank_meta['bankurl'] = [soup.findAll('tr')[1].find('td').find('a').attrs['href']]
        soup.findAll('tr')[1].find('td').find('a').decompose()
    else: 
        bank_meta['bankurl'] = np.nan

    
    # format bank address and phone
    txt = soup.findAll('tr')[1].find('td').getText()
    bank_meta['bankaddress'] = [" ".join(txt.split()).split('·')[0:2][0].strip()]
    #bank_meta['bankphone'] = [" ".join(txt.split()).split('·')[0:2][1].strip()]
    #bank_meta['bankphone'] = np.nan
    try:
        phn = " ".join(txt.split()).split('·')[0:2][1].strip()
        if phn == '':
            phn = np.nan
        bank_meta['bankphone'] = [phn]
        
    except:
        bank_meta['bankphone'] = [np.nan]
    
    bank_meta['searchurl'] = [search_url]
    
    bank_meta = pd.DataFrame.from_dict(bank_meta, orient='columns')
    bank_meta=bank_meta[['bankid', 'bankname', 'bankaddress', 'bankphone', 'bankdesc', 'bankurl','searchurl']]
    
    return bank_meta, soup

# scrape data for a list of bank ids and specified donor type
# returns a df of bank information, and a df in the original listings
def load_multi_bank(idlist, dtype):
    bm=[]
    bdata=[]
    
    for id in idlist:
        # generate search url
        search_url = create_search_URL(facilID = id, dType=dtype)
        print(search_url)
        # generate soup for each bank, 
        bank_meta, soup = bank_meta_info(search_url)
        print(bank_meta['bankname'][0], ', id: ', bank_meta['bankid'][0])
        
        # add to list for bank df and process listings provided listings exist
        if 'There are no entries' not in soup.find_all('tr')[3].getText().replace('\n','').strip():
            bm.append(bank_meta)
        
            bank = make_bank_df(soup)
            bdata.append(bank)
            print(len(bank))
        
        # if no listings, move to next id
        else:
            print('No listings for this facility and donor type, moving to next id')
        
    bank_meta_df = pd.concat(bm).reset_index(drop=True)
    bank_meta_df['dontype']=dtype
    bank_df = pd.concat(bdata).reset_index(drop=True)
    bank_df['dontype']=dtype
        
    return bank_meta_df, bank_df

# convert bank_df to dataframe organized by individual level (donor/offspring)
def make_indiv_df(bank_df):
    indiv_df=bank_df[['don_id', 'don_text', 'posted_by', 'offsp', 'usID', 
                         'dpID', 'update', 'msg_date', 'lname', 'bankname', 'bankid', 'bankdonorid', 'dontype']].copy()
    indiv_df['len_offsp']=bank_df['offsp'].apply(lambda x: len(x))
    indiv = indiv_df[indiv_df['len_offsp']<2].reset_index()
    indiv['offsp_sing']=indiv['offsp'].apply(lambda x: x[0] if x else '')
    indiv_mult = indiv_df[indiv_df['len_offsp']>1].reset_index()
    
    for _, row in indiv_mult.iterrows():
        tempdf = pd.concat([row]*row['len_offsp'], ignore_index=True, axis=1).transpose()
        tempdf['offsp_sing']=row['offsp']
        # print(tempdf)
        indiv = pd.concat([indiv, tempdf], axis=0)
        
    indiv = indiv.drop('index', axis=1)
    
    # split offspring entries and duplicate rows, to make one row per offspring
    indiv['num_girl']=indiv['offsp_sing'].apply(lambda x: split_gen([x], 'girl'))
    indiv['num_boy']=indiv['offsp_sing'].apply(lambda x: split_gen([x], 'boy'))
    indiv['num_child']=indiv['offsp_sing'].apply(lambda x: split_gen([x], 'child'))   
    
    # total kids
    indiv['num_kids']=indiv['num_girl']+indiv['num_boy']+indiv['num_child']
    
    # birth dates
    indiv['offsp_birthdates']=indiv['offsp_sing'].apply(lambda x: birthdates([x]))
    indiv['offsp_birthdates']=indiv['offsp_birthdates'].apply(lambda x: rep_empty(x))
    
    # pull year only from birthdates
    indiv['birthyear']=indiv['offsp_birthdates'].apply(lambda x: pull_year(x))

    # drop list of all kids, since this info now included in other column
    indiv = indiv.drop('offsp', axis=1)
    
    # convert dates to datetime format
    indiv_df['update']=pd.to_datetime(indiv_df['update'])
    indiv_df['msg_date']=pd.to_datetime(indiv_df['msg_date'])

    return indiv