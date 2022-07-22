# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 07:43:15 2022

@author: msparacino
"""

import pandas

import streamlit as st

import matplotlib.pyplot as plt

from matplotlib import colors

import datetime

import arrow

import pymannkendall as mk

#%%
st.set_page_config(page_title="Temperature Individual Sites", page_icon="📈")

#%% read weather data
data_raw=pandas.read_csv('DW_weather.csv.gz')

#%% convert to date time and year
data_raw['date']=pandas.to_datetime(data_raw['date'])
data_raw['CY']=data_raw['date'].dt.year

#get month list
monthList=data_raw['Month'].drop_duplicates()
monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

#get parameter list
params=data_raw.columns
params=params[params.isin(["maxt","mint","meant"])==True]

paramsDF=pandas.DataFrame(params)
paramsDF['long']=['Max Temp (F)', 'Min Temp (F)', 'Mean Temp (F)']
paramsSelect=paramsDF['long']


#get site list
sites=data_raw['site'].drop_duplicates()

#%% filter first for parameters
params_select = st.sidebar.selectbox('Select one parameter:', paramsSelect)
param=paramsDF.loc[paramsDF['long']==params_select][0]

def paramfilter():
    return data_raw.loc[data_raw[param.iloc[0]] >= 0]

data_param=paramfilter()

#%%
data1=data_param[[param.iloc[0],'Month','site','CY']]

#%% filter second for site
site_select = st.sidebar.selectbox('Select one site:', sites)

def sitefilter():
    return data1.loc[data1['site'] == site_select]

data_param_site=sitefilter()

#%% filter third for date
startY=1950
startM=10
startD=1
start_date = "%s-%s-0%s"%(startY,startM,startD) #if start day is single digit, add leading 0
end_dateRaw = arrow.now().format('YYYY-MM-DD')

#dates for st slider need to be in datetime format:
min_date = datetime.datetime(startY,startM,startD)
max_date = datetime.datetime.today() #today

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Calendar Year:', min_value=startY, max_value=int(end_dateRaw[:4]),value=1950)
endYear = st.sidebar.number_input('Enter Ending Calendar Year:',min_value=startY, max_value=int(end_dateRaw[:4]),value=2022)

data_param_site_date=data_param_site[(data_param_site['CY']>=startYear)&(data_param_site['CY']<=endYear)]


#%%threshold filter
thresholdHigh = st.sidebar.number_input('Set Upper %s threshold:'%params_select)

thresholdLow = st.sidebar.number_input('Set Lower %s threshold:'%params_select)

#%%calc statistic for all months
yearList=data_param_site_date['CY'].drop_duplicates()
newParamData=[]
newParamData1=[]
for row in yearList:
    tempData=data_param_site_date[data_param_site_date['CY']==row]
    for row1 in monthList:
        tempData2=tempData[tempData['Month']==row1]
        tempData2=tempData2.dropna()
        tempData2=tempData2.drop(columns='site')
        median=tempData2.median()
        count=tempData2[(tempData2 > thresholdHigh)&(tempData2 < thresholdLow)].count()
        newParamData.append([row,row1,median[0]])
        newParamData1.append([row,row1,count[0]])
        
paramDataMerge=pandas.DataFrame(newParamData,columns=['CY','Month',params_select])
paramDataMerge1=pandas.DataFrame(newParamData1,columns=['CY','Month',params_select])

#%%transpose to get months as columns
list=paramDataMerge['CY'].drop_duplicates()
list=list.sort_values(ascending=False)
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

medianData=pandas.DataFrame([monthNames,data4.median()])

manK=[]
data4_sort=data4.sort_index(ascending=True)
for (columnName, columnData) in data4_sort.iteritems():
    tempMK=mk.original_test(columnData)
    if tempMK[0]=='no trend':
        manK.append(-9999)
    else:
        manK.append(tempMK[7].round(2))  
        
manK=pandas.DataFrame(manK).T
sumStats=pandas.concat([medianData, manK],ignore_index=True)
sumStats.columns=sumStats.iloc[0]
sumStats=sumStats[1:]
sumStats=sumStats.rename({1:'Median',2:'Trend Slope'})


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
    
tableData=data4.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
#pandas.set_option('display.width',100)
st.header("Median of monthly %s values" %params_select)
st.dataframe(tableData)

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(data4)

st.download_button(
     label="Download Table Data as CSV",
     data=csv,
     file_name='Stats_Data_%s_%s.csv'%(params_select,site_select),
     mime='text/csv',
 )


sumStats1=sumStats.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})
sumStats1
st.markdown("(note '-9999' indicates no trend)")

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(sumStats)

st.download_button(
     label="Download Table Data as CSV",
     data=csv,
     file_name='Sum_Stats_Data_%s_%s.csv'%(params_select,site_select),
     mime='text/csv',
 )

#%%FOR THRESHOLD
#%%transpose to get Months as columns
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
    
countTableData=data5.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
pandas.set_option('display.width',100)
st.header("Count of days with %s between %s and %s value" %(params_select,thresholdLow, thresholdHigh))
st.dataframe(countTableData)

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(data5)

st.download_button(
     label="Download Count Data as CSV",
     data=csv,
     file_name='Count_Data.csv',
     mime='text/csv',
 )
