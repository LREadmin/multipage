# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 14:13:39 2022

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
st.set_page_config(page_title="Temperature Site Comparison", page_icon="📈")

#%% read weather data
data_raw=pandas.read_csv('DW_weather.csv.gz')

#%%get site list
sites=data_raw['site'].drop_duplicates()

#%%summary
sumSites=pandas.DataFrame(sites)
sumSites=sumSites.set_index(['site']) #empty dataframe with sites as index

#%% add POR
data=data_raw
data=data_raw[['site','date','maxt','mint','meant']]
data['date']=pandas.to_datetime(data['date'])
data['CY']=data['date'].dt.year

#%%select stat
#statistic
stat_selection= st.sidebar.selectbox(
     'Select one statistic:',
     ('maxt','mint','meant'))

#%%calulcate params for POR
manKPOR=[]
por=[]
medstat=[]
for site in sites:
    dataBySite=data[data['site']==site]
    porS=dataBySite['date'].min()
    porE=dataBySite['date'].max()
    por.append([site,porS,porE])
    
    #get medians
    dataBySiteParam=dataBySite[stat_selection]
    tempstat=dataBySiteParam.median()
    medstat.append(tempstat)
    
    #Man Kendall Test
    dataforMK=dataBySite[[stat_selection,'CY']]
    tempPORMKMedian=dataforMK.groupby(dataforMK['CY']).median()
    tempPORManK=mk.original_test(tempPORMKMedian)
    if tempPORManK[0]=='no trend':
        manKPOR.append([site,-9999])
    else:
        manKPOR.append([site,tempPORManK[7].round(2)])       #slope value 

manKPOR=pandas.DataFrame(manKPOR)
manKPOR=manKPOR.set_index([sites])
manKPOR.columns=(['Site','ManKPOR'])
    
pordf=pandas.DataFrame(por)
pordf=pordf.set_index([0])
pordf.columns=["POR Start","POR End"]

medstatdf=pandas.DataFrame(medstat)
medstatdf=medstatdf.set_index([sites])
medstatdf.columns=['POR %s'%stat_selection]

sumSites=pandas.concat([pordf,medstatdf,manKPOR],axis=1)

sumSites['POR Start']=pandas.to_datetime(sumSites["POR Start"]).dt.strftime('%Y-%m-%d')
sumSites['POR End']=pandas.to_datetime(sumSites["POR End"]).dt.strftime('%Y-%m-%d')

#%%make selections
sites=data['site'].drop_duplicates()

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select = container.multiselect('Select one or more sites:', sites, sites)

else:
    multi_site_select = container.multiselect('Select one or more sites:', sites,default=sites.iloc[0])

    
def multisitefilter():
    return data[data['site'].isin(multi_site_select)]
    
data_sites=multisitefilter()

#%%start and end dates needed for initial data fetch
startY=1900
startM=10
startD=1
start_date = "%s-%s-0%s"%(startY,startM,startD) #if start day is single digit, add leading 0
end_dateRaw = arrow.now().format('YYYY-MM-DD')

#dates for st slider need to be in datetime format:
min_date = datetime.datetime(startY,startM,startD)
max_date = datetime.datetime.today() #today

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=int(end_dateRaw[:4]), value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY, max_value=int(end_dateRaw[:4]),value=2022)

def startDate():
    return "%s-0%s-0%s"%(int(startYear),1,1)

start_date=startDate()

def endDate():
    return "%s-%s-%s"%(int(endYear),12,31)

end_date=endDate()

#change dates to similar for comparison
start_date1=pandas.to_datetime(start_date)
end_date1=pandas.to_datetime(end_date) 
data_sites['date'] = pandas.to_datetime(data_sites['date'])


#%%FILTERED DATA
data_sites_years=data_sites[(data_sites['date']>start_date1)&(data_sites['date']<=end_date1)]


#%% calculate params for selected period

manKPORSelect=[]
medstatSelect=[]

siteSelect=data_sites_years['site'].drop_duplicates()

for site in siteSelect:
    dataBySite=data_sites_years[data_sites_years['site']==site]
    
    #get medians
    dataBySiteParam=dataBySite[stat_selection]
    tempstat=dataBySiteParam.median()
    medstatSelect.append(tempstat)
    
    #Man Kendall Test
    dataforMKSelect=dataBySite[[stat_selection,'CY']]
    tempPORMKMedian=dataforMKSelect.groupby(dataforMKSelect['CY']).median()
    tempPORManK=mk.original_test(tempPORMKMedian)
    if tempPORManK[0]=='no trend':
        manKPORSelect.append([site,-9999])
    else:
        manKPORSelect.append([site,tempPORManK[7].round(2)])       #slope value 

manKPORSelect=pandas.DataFrame(manKPORSelect)
manKPORSelect=manKPORSelect.set_index([0])
manKPORSelect.columns=(['ManKSelect'])

medstatSelectdf=pandas.DataFrame(medstatSelect)
medstatSelectdf=medstatSelectdf.set_index([siteSelect])

medstatSelectdf.columns=[stat_selection]

sumSites=pandas.concat([sumSites,medstatSelectdf,manKPORSelect],axis=1)      
sumSites=sumSites.drop("Site",axis=1)

sumSites1=sumSites[sumSites.index.isin(multi_site_select)]

# sumSites2=sumSites1.style\
#     .format({'POR %s'%stat_selection:"{:.1f}",'POR mint':"{:.1f}",'POR meant':"{:.1f}",'maxt':"{:.1f}",'mint':"{:.1f}",'meant':"{:.1f}"})\

st.header("Site Comparison, with Median")
sumSites1

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(sumSites1)

st.download_button(
     label="Download Summary Table as CSV",
     data=csv,
     file_name='Summary_Table.csv',
     mime='text/csv',
 )