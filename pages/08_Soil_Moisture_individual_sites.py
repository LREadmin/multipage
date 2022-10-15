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

#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def convert_to_WY(row):
    if row.month>=10:
        return(pd.datetime(row.year+1,1,1).year)
    else:
        return(pd.datetime(row.year,1,1).year)


#%% Site data
siteNames = pd.read_csv("siteNamesListCode.csv")

#%% Left Filters

#01 Select Site 
site_selected = st.sidebar.selectbox('Select your site:', siteNames.iloc[:,0])
siteCode=siteNames[siteNames.iloc[:,0]==site_selected].iloc[0][1]

#02 Select Depths
elementDF=pd.DataFrame({0:["SMS:-2:value","SMS:-4:value", "SMS:-8:value","SMS:-20:value","SMS:-40:value"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})

container=st.sidebar.container()
paramsSelect=elementDF['long']
element_select=container.multiselect('Select depth(s):',paramsSelect,default=elementDF['long'])
element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]
elementStr= ','.join(element_select)

#03 Select Water Year
start_date = "%s-%s-0%s"%(1950,10,1) 
end_dateRaw = arrow.now().format('YYYY-MM-DD')

min_date = datetime.datetime(1950,10,1) #dates for st slider need to be in datetime format:
max_date = datetime.datetime.today() 

startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=1950, max_value=int(end_dateRaw[:4]),value=1950)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=1950, max_value=int(end_dateRaw[:4]),value=2021)


#%% SOIL MOISTURE DATA
#Selections
sitecodeSMS=siteCode.replace("SNOTEL:", "" )
sitecodeSMS=sitecodeSMS.replace("_", ":" )

headerAdj=pd.DataFrame({'ElementCount':[0,1,2,3,4,5],"HeaderRowCount":[57,58,59,60,61,62]})
headerCount=headerAdj['HeaderRowCount'][headerAdj['ElementCount']==len(element_select)]

base="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
part1="customMultiTimeSeriesGroupByStationReport/daily/start_of_period/"
site=sitecodeSMS
por="%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/"
element=elementStr
part2="?fitToScreen=false"
url=base+part1+site+por+element+part2

s=requests.get(url).text

urlData=pd.read_csv(url,header=headerCount.iloc[0],delimiter=',',error_bad_lines=False)
#%% display

urlData['year']=pd.DatetimeIndex(urlData['Date']).year
urlData['month']=pd.DatetimeIndex(urlData['Date']).month
urlData['WY']= urlData.apply(lambda x: convert_to_WY(x), axis=1)

#filter by WY
dateFiltered=urlData[(urlData['WY']>=startYear)&(urlData['WY']<=endYear)]

st.header("Data")
dateFiltered.set_index('Date')
dateFiltered
csv = convert_df(dateFiltered)
st.download_button(
     label="Download Selected Soil Moisture Data",
     data=csv,
     file_name='SMS_data.csv',
     mime='text/csv',
 )

st.header("URL to download directly from NRCS")
url

#%%
