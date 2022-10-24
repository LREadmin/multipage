# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:53:06 2022

@author: msparacino
"""
#%% import packages

import pandas as pd

import requests

import numpy as np

#%%dictionaries
months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

#constants
dayCountThres=25
startY=1950
startM=10
startD=1

#%% Site data
siteNames = pd.read_csv("siteNamesListCode.csv",usecols=[1])

sitecodeSMS=siteNames["1"].str.replace("SNOTEL:", "")
sitecodeSMS=sitecodeSMS.str.replace("_", ":" )

for site in sitecodeSMS:
    print(site)
    base="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
    part1="customMultiTimeSeriesGroupByStationReport/daily/start_of_period/"
    por="%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/"
    element="SMS:-2:value,SMS:-4:value,SMS:-8:value,SMS:-20:value,SMS:-40:value"
    part2="?fitToScreen=false"
    url=base+part1+site+por+element+part2

    s=requests.get(url).text
    
    urlDataRaw=pd.read_csv(url,header=62,delimiter=',',error_bad_lines=False)#headerCount.iloc[0]

    #filter out data >100%
    datecol=urlDataRaw['Date']
    cols=urlDataRaw.columns[1:]
    urlData=urlDataRaw[cols].applymap(lambda x: np.nan if x > 100 else x)
    urlData['Date']=datecol
    cols2=urlData.columns.tolist()
    cols2 = [cols2[-1]]+cols2[:-1] 
    urlData=urlData.reindex(columns=cols2)
    
    urlData.columns=['Date','minus_2inch_pct','minus_4inch_pct','minus_8inch_pct','minus_20inch_pct','minus_40inch_pct']
    
    urlData['site']=site
    
    urlData.to_csv("C:\\Users\msparacino\streamlit\SMS_Data\POR_data_site_%s.csv"%site[:3],index=False)
    