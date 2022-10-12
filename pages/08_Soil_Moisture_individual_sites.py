# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:53:06 2022

@author: msparacino
"""
#%% import packages

import streamlit as st #for displaying on web app

import pandas

import requests

#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

#%% Site data
siteNames = pandas.read_csv("siteNamesListCode.csv")

#%% Define and use Site Filter

site_selected = st.sidebar.selectbox('Select your site:', siteNames.iloc[:,0])

siteCode=siteNames[siteNames.iloc[:,0]==site_selected]
siteCode=siteCode.iloc[0][1]

#%% select elements

elementDF=pandas.DataFrame({0:
                           ["SMS:-2:value",
                            "SMS:-4:value",
                            "SMS:-8:value",
                            "SMS:-20:value",
                            "SMS:-40:value"], 
                           'long': ['2 inch depth', 
                                    '4 inch depth',
                                    '8 inch depth', 
                                    '20 inch depth',
                                    '40 inch depth']})
container=st.sidebar.container()
paramsSelect=elementDF['long']

element_select=container.multiselect('Select depth(s):',paramsSelect)

element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]

#element_select=elementDF.loc[0:1][0]
elementStr=''

for i in range(0,len(element_select)):
    if i <len(element_select)-1:
        elementStr=elementStr + element_select.iloc[i] + ","
    if i==len(element_select)-1:
        elementStr=elementStr+element_select.iloc[i]

#%% SOIL MOISTURE DATA
#Selections
sitecodeSMS=siteCode.replace("SNOTEL:", "" )
sitecodeSMS=sitecodeSMS.replace("_", ":" )

headerAdj=pandas.DataFrame({'ElementCount':[
    0,1,2,3,4,5],
    "HeaderRowCount":[57,58,59,60,61,62]})
headerCount=headerAdj['HeaderRowCount'][headerAdj['ElementCount']==len(element_select)]

base="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
part1="customMultiTimeSeriesGroupByStationReport/daily/start_of_period/"
site=sitecodeSMS
por="%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/"
element=elementStr
part2="?fitToScreen=false"
url=base+part1+site+por+element+part2

s=requests.get(url).text

c=pandas.read_csv(url,header=headerCount.iloc[0],delimiter=',',error_bad_lines=False)
#%% display
# CSS to inject contained in a string
c=c.set_index("Date")

st.header("Data")
c

csv = convert_df(c)
st.download_button(
     label="Download Selected Soil Moisture Data",
     data=csv,
     file_name='SMS_data.csv',
     mime='text/csv',
 )

st.header("URL to download directly from NRCS")
url
