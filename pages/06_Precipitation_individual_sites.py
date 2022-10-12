# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 04:42:06 2022

@author: msparacino
@modfiications: mpedrazas
"""



#%% Import Libraries
import pandas #for dataframe

import matplotlib.pyplot as plt #for plotting

from matplotlib import colors #for additional colors

import streamlit as st #for displaying on web app

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

#%% Website display information
st.set_page_config(page_title="Precipitation Individual Sites", page_icon="🌦")

#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

#%% Read in raw weather data
data_raw=pandas.read_csv('DW_weather.csv.gz')

#%% Convert to date time and year
data_raw['date']=pandas.to_datetime(data_raw['date'])
data_raw['CY']=data_raw['date'].dt.year

#get month list
monthList=data_raw['Month'].drop_duplicates()
monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

#get parameter list
params=data_raw.columns
params=params[params.isin(["cumm_precip"])==True]

paramsDF=pandas.DataFrame(params)
paramsDF['long']=["Accumulated Precipitation (in)"]
paramsSelect=paramsDF['long']

#get site list
sites=pandas.DataFrame(data_raw['site'].drop_duplicates())
sites['long']=['Anterro (AN)','Cheesman (CM)','DIA (DI)','Dillon (DL)','DW Admin (DW)','Evergreen (EG)',
               'Eleven Mile (EM)','Gross (GR)','Kassler (KS)','Moffat HQ (MF)','Ralston (RS)','Central Park (SP)',
               'Strontia (ST)','Williams Fork (WF)']

#%% filter first for parameters
params_select = "Accumulated Precipitation (in)"
param=paramsDF.loc[paramsDF['long']==params_select][0]

def paramfilter():
    return data_raw.loc[data_raw[param.iloc[0]] >= 0]

data_param=paramfilter()

#%%
data1=data_param[[param.iloc[0],'pcpn','Month','site','CY','WY']]

#%% filter second for site
site_select_long = st.sidebar.selectbox('Select one site:', sites['long'])

site_select=sites['site'][sites['long']==site_select_long]

def sitefilter():
    return data1.loc[data1['site'] == site_select.iloc[0]]

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
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=int(end_dateRaw[:4]),value=1950)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY, max_value=int(end_dateRaw[:4]),value=2021)

def dateSelection():
    return data_param_site[(data_param_site['WY']>=startYear)&(data_param_site['WY']<=endYear)]

data_param_site_date=dateSelection()

#%%threshold filter
thresholdHigh = st.sidebar.number_input('Set Upper Precipitation threshold (in/day):',step=0.1,min_value=0.0, value=4.0,format="%.1f")

thresholdLow = st.sidebar.number_input('Set Lower Precipitation threshold (in/day):',step=0.1,min_value=0.0, value=0.0,format="%.1f")

#%%calc statistic for all months
yearList=data_param_site_date['WY'].drop_duplicates()
newParamData=[]
newParamData1=[]

for row in yearList:
    tempData=data_param_site_date[data_param_site_date['WY']==row]

    #filter by day count threshold
    dayCountThres=25
    tempData=tempData.groupby('Month').filter(lambda x : len(x)>=dayCountThres)
    
    for row1 in monthList:
        tempData2=tempData[tempData['Month']==row1]
        tempData2=tempData2.dropna()
        tempData2=tempData2.drop(columns='site')
        # sumMonth=tempData2.pcpn.sum()
        monthlyCumPrecip=tempData2.pcpn.sum() #calculate monthly total
        count=tempData2[(tempData2 <= thresholdHigh)&(tempData2 >= thresholdLow)].count()
        newParamData.append([row,row1,monthlyCumPrecip])
        newParamData1.append([row,row1,count[1]])
        
paramDataMerge=pandas.DataFrame(newParamData,columns=['WY','Month',params_select]) #sum pcpn
paramDataMerge1=pandas.DataFrame(newParamData1,columns=['WY','Month',params_select]) #count

#%%transpose to get months as columns
list=paramDataMerge['WY'].drop_duplicates()
list=list.sort_values(ascending=False)
yearList=[]
for n in list:
    temp1=paramDataMerge[paramDataMerge['WY']==n]
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
    try:
        tempMK=mk.original_test(columnData)
        if tempMK[2]>0.1:
            manK.append(float('nan'))
        else:
            manK.append(tempMK[7])  
    except:
        manK.append(float('nan'))
        
manK=pandas.DataFrame(manK).T
sumStats=pandas.concat([medianData, manK],ignore_index=True)
sumStats.columns=sumStats.iloc[0]
sumStats=sumStats[1:]
sumStats=sumStats.rename({1:'Median',2:'Trend'})


#%%colormap


def background_gradient(s, m=None, M=None, cmap='cool_r', low=0, high=0):
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

    return ret 

# pandas.set_option("display.precision", 1)
tableData=data4.style\
    .set_properties(**{'width':'10000px','color':'white'})\
    .apply(background_gradient, axis=None)\
    .format(precision=1)
#%%display
#pandas.set_option('display.width',100)
st.header("Monthly %s " %params_select)
st.dataframe(tableData)

#%% download table data
csv = convert_df(data4)

st.download_button(
     label="Download Table Data as CSV",
     data=csv,
     file_name='Stats_Data_%s_%s.csv'%(params_select,site_select.iloc[0]),
     mime='text/csv',
 )

sumStats1=sumStats.style\
    .format('{:,.2f}')\
    .set_properties(**{'width':'10000px'})

st.markdown("Trend (Theil-Sen Slope (inches/year) if Mann-Kendall trend test is significant (p-value <0.1); otherwise nan)")
sumStats1

#%% download Summary table data
csv = convert_df(sumStats)

st.download_button(
     label="Download Summary Table Data as CSV",
     data=csv,
     file_name='Sum_Stats_Data_%s_%s.csv'%(params_select,site_select.iloc[0]),
     mime='text/csv',
 )

#%%FOR THRESHOLD
#%%transpose to get Months as columns
yearList=[]
for n in list:
    temp1=paramDataMerge1[paramDataMerge1['WY']==n]
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

def background_gradient(s, m=None, M=None, cmap='cool_r', low=0, high=0):
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
st.header("Count of days with Precipitation between %s and %s inches" %(thresholdLow, thresholdHigh))
st.dataframe(countTableData)

#%% download count data
csv = convert_df(data5)

st.download_button(
     label="Download Count Data as CSV",
     data=csv,
     file_name='Count_Data.csv',
     mime='text/csv',
 )




