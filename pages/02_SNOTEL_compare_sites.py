# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:15:03 2020

@author: msparacino
"""
import pandas

import numpy

import matplotlib.pyplot as plt

import streamlit as st

import datetime

import arrow

import pymannkendall as mk


#%% set working directory
st.set_page_config(page_title="Individual Site", page_icon="📈")

st.markdown("# Site Comparison")
st.sidebar.header("Site Comparison")


#%% read measurement data
data_raw=pandas.read_csv('SNOTEL_data_raw.csv.gz')

#%% read site data
sites_df=pandas.read_csv('SNOTEL_sites.csv.gz')
with open("siteNamesListNS.txt") as f:
    siteNamesList=f.read().split(", ")
siteNamesList = [s.replace("[", "") for s in siteNamesList]
siteNamesList = [s.replace("]", "") for s in siteNamesList]
siteNamesList = [s.replace("'", "") for s in siteNamesList]
siteNames=pandas.DataFrame([sub.split(",") for sub in siteNamesList])
siteNames.columns=['Site','System']

siteKey=sites_df[['index','name']]
siteKey.columns=['code','Site']

#%% read POR data
sites_POR=pandas.read_csv('SNOTEL_data_POR.csv.gz')

#%% merged df
combo_data=pandas.merge(data_raw,siteKey,on="Site",how='inner')
combo_data1=pandas.merge(combo_data,siteNames,on="Site",how='inner')
combo_data2=pandas.merge(combo_data1,sites_POR,on="code",how='inner')
combo_data2['Date']=pandas.to_datetime(combo_data2['Date'])
combo_data2['por_start']=pandas.to_datetime(combo_data2['por_start'])
combo_data2['por_end']=pandas.to_datetime(combo_data2['por_end'])

#%% get POR median
median=[]
for row in siteNames['Site']:
    temp=combo_data2[combo_data2['Site']==row]
    temp_median=temp['SWE_in'].median()
    median.append(temp_median)
median=pandas.DataFrame(median)
siteNames['POR_median_SWE_in']=median
por_median=siteNames[['Site','POR_median_SWE_in']]

combo_data2=pandas.merge(combo_data2,por_median,on="Site",how='inner')
#%%System Selection
system=combo_data2['System'].drop_duplicates()
system_select = st.sidebar.selectbox('Select your system:', system)

def systemfilter():
    return combo_data2[combo_data2['System']==system_select]

system_data=systemfilter()

#%% multi site selection
sites=system_data['Site'].drop_duplicates()

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select = container.multiselect('Select one or more sites:', sites, sites)

else:
    multi_site_select = container.multiselect('Select one or more sites:', sites,default=sites.iloc[0])

    
def multisitefilter():
    return system_data[system_data['Site'].isin(multi_site_select)]
    
system_site_data=multisitefilter()

#%%start and end dates needed for initial data fetch
startY=1950
startM=10
startD=1
start_date = "%s-%s-0%s"%(startY,startM,startD) #if start day is single digit, add leading 0
end_date = arrow.now().format('YYYY-MM-DD')

#dates for st slider need to be in datetime format:
min_date = datetime.datetime(startY,startM,startD)
max_date = datetime.datetime.today() #today

with st.sidebar:
    st.write("Date range:")
    start_date = st.date_input("Pick a start date", min_value=min_date, max_value=max_date) #force start date at least 1 year before end date
    end_date = st.date_input("Pick an end date", min_value=min_date, max_value=max_date)
    
if start_date >= end_date:
    st.sidebar.error('Use Selection to change start date (default has been set to %s)'%min_date)
    start_date=min_date

start_date=pandas.to_datetime(start_date,utc=True) 
final_data=system_site_data[(system_site_data['Date']>start_date)]

summary=pandas.DataFrame()#columns=['Site','System','POR Start','POR End','Median'])
#st.dataframe(summary)
#summary=[]
median=[]
for row in multi_site_select:
    temp=final_data[final_data['Site']==row]
    temp_median=temp['SWE_in'].median()
    median.append(temp_median)
    temp1=temp[['Site','System','por_start','por_end','POR_median_SWE_in']]
    temp1=temp1.drop_duplicates()
    summary=pandas.concat([summary,temp1],ignore_index=True)
    
median=pandas.DataFrame(median)
summary=pandas.concat([summary,median],axis=1)
summary.columns=['Site','System','POR Start','POR End','SWE median for POR (in)','SWE Median For Selected Date Range (in)']

st.dataframe(summary)

#st.dataframe(final_data)
#st.dataframe(multi_site_select)
#median=pandas.DataFrame(final_data['SWE_in'].median()).T
#st.dataframe(median)

