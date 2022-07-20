# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 07:43:15 2022

@author: msparacino
"""

import pandas

import streamlit as st

import matplotlib.pyplot as plt

from matplotlib import colors

#%% read weather data
data_raw=pandas.read_csv('DW_weather.csv.gz')

#%% convert to date time and year
data_raw['date']=pandas.to_datetime(data_raw['date'])
data_raw['CY']=data_raw['date'].dt.year

#get year list
yearList=data_raw['CY'].drop_duplicates()

#get month list
monthList=data_raw['Month'].drop_duplicates()
monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

#get parameter list
params=data_raw.columns
params=params[params.isin(["date","precip_rank","site"])==False]

#get site list
sites=data_raw['site'].drop_duplicates()

#%% filter first for parameters
params_select = st.sidebar.selectbox('Select one parameter:', params)

def paramfilter():
    return data_raw.loc[data_raw[params_select] >= 0]

data_param=paramfilter()

#%%
data1=data_param[[params_select,'Month','site','CY']]

#%% filter second for site
site_select = st.sidebar.selectbox('Select one site:', sites)

def sitefilter():
    return data1.loc[data1['site'] == site_select]

data_param_site=sitefilter()

#%%threshold filter
threshold = st.sidebar.number_input('Set %s threshold:'%params_select)

#%%calc statistic for all months
newParamData=[]
newParamData1=[]
for row in yearList:
    tempData=data_param_site[data_param_site['CY']==row]
    for row1 in monthList:
        tempData2=tempData[tempData['Month']==row1]
        tempData2=tempData2.dropna()
        tempData2=tempData2.drop(columns='site')
        median=tempData2.median()
        count=tempData2[tempData2 > threshold].count()
        newParamData.append([row,row1,median[0]])
        newParamData1.append([row,row1,count[0]])

paramDataMerge=pandas.DataFrame(newParamData,columns=['CY','Month',params_select])
paramDataMerge1=pandas.DataFrame(newParamData1,columns=['CY','Month',params_select])

#%%transpose to get days as columns
list=paramDataMerge['CY'].drop_duplicates()
list=list.sort_values()
yearList=[]
for n in list:
    temp1=paramDataMerge[paramDataMerge['CY']==n]
    temp2=temp1.iloc[:,[1,2]].copy()
    temp2=temp2.sort_values(by="Month")
    temp3=temp2.T
    temp3.columns=temp3.iloc[0]
    temp3=temp3.drop('Month')
    yearList.append(temp3)

data4=pandas.concat(yearList)
years=list.values.tolist()
data4['Years']=years
data4=data4.set_index('Years')
data4.columns=monthNames

#%%colormap

def background_gradient(s, m=None, M=None, cmap='OrRd', low=0, high=0):
    print(s.shape)
    if m is None:
        m = s.min().min()
    if M is None:
        M = s.max().max()
    rng = M - m
    norm = colors.Normalize(m - (rng * low),
                            M + (rng * high))
    normed = s.apply(norm)

    cm = plt.cm.get_cmap(cmap)
    c = normed.applymap(lambda x: colors.rgb2hex(cm(x)))
    ret = c.applymap(lambda x: 'background-color: %s' % x)
    # if data4.isnull().values.any():
    #     return 'background-color: white'
    return ret 
    
data4=data4.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
pandas.set_option('display.width',100)
st.markdown("Median of monthly %s values" %params_select)
st.dataframe(data4)

#%%FOR THRESHOLD
#%%transpose to get days as columns
list=paramDataMerge1['CY'].drop_duplicates()
list=list.sort_values()
yearList=[]
for n in list:
    temp1=paramDataMerge1[paramDataMerge1['CY']==n]
    temp2=temp1.iloc[:,[1,2]].copy()
    temp2=temp2.sort_values(by="Month")
    temp3=temp2.T
    temp3.columns=temp3.iloc[0]
    temp3=temp3.drop('Month')
    yearList.append(temp3)

data5=pandas.concat(yearList)
years=list.values.tolist()
data5['Years']=years
data5=data5.set_index('Years')
data5.columns=monthNames

#%%colormap

def background_gradient(s, m=None, M=None, cmap='OrRd', low=0, high=0):
    print(s.shape)
    if m is None:
        m = s.min().min()
    if M is None:
        M = s.max().max()
    rng = M - m
    norm = colors.Normalize(m - (rng * low),
                            M + (rng * high))
    normed = s.apply(norm)

    cm = plt.cm.get_cmap(cmap)
    c = normed.applymap(lambda x: colors.rgb2hex(cm(x)))
    ret = c.applymap(lambda x: 'background-color: %s' % x)
    # if data4.isnull().values.any():
    #     return 'background-color: white'
    return ret 
    
data5=data5.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
pandas.set_option('display.width',100)
st.markdown("Count of days with %s over %s value" %(params_select,threshold))
st.dataframe(data5)

