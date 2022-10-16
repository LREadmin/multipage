# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:53:06 2022

@author: msparacino
"""
#%% import packages

import streamlit as st #for displaying on web app

import pandas as pd

import requests

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

import numpy as np
import matplotlib.pyplot as plt #for plotting
from matplotlib import colors #for additional colors

import pymannkendall as mk #for trend anlaysis
#%% Define data download as CSV function
#functions
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def convert_to_WY(row):
    if row.month>=10:
        return(pd.datetime(row.year+1,1,1).year)
    else:
        return(pd.datetime(row.year,1,1).year)
    
def background_gradient(s, m=None, M=None, cmap='gist_earth_r', low=0.1, high=1):
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

#dictionaries
months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

#constants
dayCountThres=25
startY=1950
startM=10
startD=1

#%% Site data
siteNames = pd.read_csv("siteNamesListCode.csv", dtype=str)

#%% Left Filters

#01 Select System
container=st.sidebar.container()

all=st.sidebar.checkbox("Select both systems")

if all:
    system_selected = container.multiselect('Select your system(s):', siteNames.iloc[:,2].unique(), siteNames.iloc[:,2].unique())
    siteNamesInSys=siteNames[siteNames['2']==system_selected]

else: 
    system_selected = container.multiselect('Select your system(s):', siteNames.iloc[:,2].unique(), default=siteNames.iloc[0,2])
    siteNamesInSys=siteNames

#02 Select Site 

site_selected = st.sidebar.selectbox('Select your site:', siteNamesInSys.iloc[:,0])
siteCode=siteNames[siteNames.iloc[:,0]==site_selected].iloc[0][1]

#03 Select Depths
elementDF=pd.DataFrame({0:["SMS:-2:value","SMS:-4:value", "SMS:-8:value","SMS:-20:value","SMS:-40:value"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})

container=st.sidebar.container()
paramsSelect=elementDF['long']
element_select=container.multiselect('Select depth(s):',paramsSelect,default=elementDF['long'])
element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]
elementStr= ','.join(element_select)

#04 Select Water Year
start_date = "%s-%s-0%s"%(startY,startM,startD) 
end_dateRaw = arrow.now().format('YYYY-MM-DD')

min_date = datetime.datetime(startY,startM,startD) #dates for st slider need to be in datetime format:
max_date = datetime.datetime.today() 

startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=int(end_dateRaw[:4]),value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY, max_value=int(end_dateRaw[:4]),value=2021)


#%% SOIL MOISTURE DATA filtered by site, parameter and date
#Selections
sitecodeSMS=siteCode.replace("SNOTEL:", "" )
sitecodeSMS=sitecodeSMS.replace("_", ":" )

headerAdj=pd.DataFrame({'ElementCount':[0,1,2,3,4,5],"HeaderRowCount":[57,58,59,60,61,62]})
headerCount=headerAdj['HeaderRowCount'][headerAdj['ElementCount']==len(element_select)]

base="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
part1="customMultiTimeSeriesGroupByStationReport/daily/start_of_period/"
site=sitecodeSMS
por="%7Cid=%22%22%7Cname/" + str(startYear-1) + "-10-01," + str(endYear-1) + "-09-30/"
element=elementStr
part2="?fitToScreen=false"
url=base+part1+site+por+element+part2

s=requests.get(url).text

urlData=pd.read_csv(url,header=headerCount.iloc[0],delimiter=',',error_bad_lines=False)
#%% Download Daily Soil Moisture Data

urlData['year']=pd.DatetimeIndex(urlData['Date']).year
urlData['month']=pd.DatetimeIndex(urlData['Date']).month
urlData['WY']= urlData.apply(lambda x: convert_to_WY(x), axis=1)

#filter by WY
dateFiltered=urlData[(urlData['WY']>=startYear)&(urlData['WY']<=endYear)]


st.header("Soil Moisture Percent (pct) Start of Day Values")

dateFiltered.set_index('Date')

csv = convert_df(dateFiltered)
st.download_button(
     label="Download Daily Soil Moisture Data",
     data=csv,
     file_name='SMS_data.csv',
     mime='text/csv',
 )

# st.header("URL to download directly from NRCS")
# url

#%% Create pivot table using average soil moisture and show medians by WY
dateFiltered['averageSoilMoisture']=(dateFiltered[urlData.columns[1:-3]]).mean(axis=1)
dateFiltered_nonans = dateFiltered.dropna(subset=['averageSoilMoisture'])

#filter by months with days > 25 that have average soil moisture data 
smData=dateFiltered_nonans.groupby(['month','WY']).filter(lambda x : len(x)>=dayCountThres)

pvTable=pd.pivot_table(smData, values=['averageSoilMoisture'],index='WY', columns={'month'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
pvTable=pvTable["averageSoilMoisture"].head(len(pvTable))

pvTable=pvTable.rename(columns = months)

#display pivot table 
tableData=pvTable.style\
    .set_properties(**{'width':'10000px','color':'white'})\
    .apply(background_gradient, axis=None)\
    .format(precision=1)

st.dataframe(tableData)

#download pivot table
csv = convert_df(pvTable)
st.download_button(
     label="Download Table Data as CSV",
     data=csv,
     file_name='Median_SoilMoisture_byWY.csv',
     mime='text/csv',
 )


#%% Statistics Table

medianTable=pvTable.median()
medianTable=medianTable.to_frame('Median')
medianTable=medianTable.transpose()

#calculate trends using data that has no nans and count of days > 25
trendData=smData[['averageSoilMoisture','month','WY']]
trendData=trendData.set_index('WY').sort_index(ascending=True)
months_list=trendData.month.unique()
# trendData=trendData.set_index('month')
manK=[]
for i in months_list:
    try:
        print(str(i))
        tempMK=mk.original_test(trendData[trendData.month==i][['averageSoilMoisture']])
        print(tempMK)
        if tempMK[2]>0.1:
            manK.append(float('nan'))
        else:
            manK.append(tempMK[7])  
    except:
        manK.append(float('nan'))

manKdf=pd.DataFrame(manK,columns={'Trend'}).transpose()
manKdf.columns=[months[x] for x in months_list]

medianTableData=medianTable.append(manKdf)

#display pivot table 
st.markdown("Trend (Theil-Sen Slope (inches/year) if Mann-Kendall trend test is significant (p-value <0.1); otherwise nan). Months with less than 25 days of data are not included in the analysis.")

displayTableData=medianTableData.style\
    .set_properties(**{'width':'10000px','color':'white'})\
    .apply(background_gradient, axis=None)\
    .format(precision=2)

st.dataframe(displayTableData)

#download pivot table
csv = convert_df(medianTableData)
st.download_button(
     label="Download Statistics Table Data as CSV",
     data=csv,
     file_name='StatisticsTablebyMonth.csv',
     mime='text/csv',
 )

