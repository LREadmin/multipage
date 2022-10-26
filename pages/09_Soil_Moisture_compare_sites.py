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

st.set_page_config(page_title="Soil Moisture Site Comparison", page_icon="🌱")

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
startY=1950
startM=10
startD=1

#%% Site data
siteNamesRaw = pd.read_csv("siteNamesListCode.csv", dtype=str)

AllsiteNames = siteNamesRaw.replace('SNOTEL:','', regex=True)
AllsiteNames = AllsiteNames.replace("_", ":",regex=True)

#%% Load SMS data
data_raw=pd.read_csv('SNOTEL_SMS.csv.gz')

#%% Left Filters

#%% 01 Select System
container=st.sidebar.container()

all=st.sidebar.checkbox("Select both systems")

if all:
    system_selected = container.multiselect('Select your system(s):', AllsiteNames.iloc[:,2].drop_duplicates(), AllsiteNames.iloc[:,2].drop_duplicates())
else: 
    system_selected = container.multiselect('Select your system(s):', AllsiteNames.iloc[:,2].drop_duplicates(), default='North')

siteNames=AllsiteNames[AllsiteNames['2'].isin(system_selected)]

#%% 02 Select Site 
all_sites=st.sidebar.checkbox("Select all sites")
if all:
    site_selected = container.multiselect('Select your site:', siteNames.iloc[:,0], siteNames.iloc[:,0])
else: 
    site_selected = container.multiselect('Select your site:', siteNames.iloc[:,0], default=siteNames.iloc[0,0])

siteCodes=siteNames[siteNames['0'].isin(site_selected)].iloc[:,1]
siteNames=siteNames[siteNames['0'].isin(site_selected)].iloc[:,0]

#%% 03 select months
monthOptions=pd.DataFrame({'Month':['Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug'],
                               'Season':['Fall','Fall','Fall','Winter','Winter','Winter','Spring','Spring','Spring','Summer','Summer','Summer',],
                               'Num':[9,10,11,12,1,2,3,4,5,6,7,8]})
monthSelect=monthOptions['Month']


fallMonths=monthOptions.loc[monthOptions['Season']=='Fall']['Month']
winterMonths=monthOptions.loc[monthOptions['Season']=='Winter']['Month']
springMonths=monthOptions.loc[monthOptions['Season']=='Spring']['Month']
summerMonths=monthOptions.loc[monthOptions['Season']=='Summer']['Month']

container=st.sidebar.container()

fall=st.sidebar.checkbox("Fall")
summer=st.sidebar.checkbox("Summer")
spring=st.sidebar.checkbox("Spring")
winter=st.sidebar.checkbox("Winter")

#multiseasons
if winter and spring and (fall==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',pd.concat([winterMonths,springMonths]), pd.concat([winterMonths,springMonths]))
elif winter and summer and (fall==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',pd.concat([winterMonths,summerMonths]), pd.concat([winterMonths,summerMonths]))
elif winter and fall and (spring==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',pd.concat([winterMonths,fallMonths]), pd.concat([winterMonths,fallMonths]))
elif winter and (fall==False) and (spring==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',winterMonths, winterMonths)
elif spring and (fall==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',springMonths, springMonths)
elif fall and spring and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',pd.concat([springMonths,fallMonths]), pd.concat([springMonths,fallMonths]))
elif spring and summer and (winter==False) and (fall==False):
    month_select = container.multiselect('Select month(s):',pd.concat([springMonths,summerMonths]), pd.concat([springMonths,summerMonths]))
elif summer and fall and (winter==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',pd.concat([summerMonths,fallMonths]), pd.concat([summerMonths,fallMonths]))
elif summer and (fall==False) and (winter==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',summerMonths, summerMonths)
elif fall and (spring==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',fallMonths, fallMonths)
elif fall and summer and spring and (winter==False):
    month_select = container.multiselect('Select month(s):',pd.concat([springMonths,summerMonths,fallMonths]), pd.concat([springMonths,summerMonths,fallMonths]))
elif fall and summer and winter and (spring==False):
    month_select = container.multiselect('Select month(s):',pd.concat([winterMonths,summerMonths,fallMonths]), pd.concat([winterMonths,summerMonths,fallMonths]))
elif spring and summer and winter and (fall==False):
    month_select = container.multiselect('Select month(s):',pd.concat([winterMonths,springMonths,summerMonths]), pd.concat([winterMonths,springMonths,summerMonths]))
elif spring and fall and summer and winter:
    month_select = container.multiselect('Select month(s):',pd.concat([springMonths,winterMonths,summerMonths,fallMonths]), pd.concat([springMonths,winterMonths,summerMonths,fallMonths]))

else:
    month_select = container.multiselect('Select month(s):', monthSelect,default=monthSelect)

monthNum_select=pd.DataFrame(month_select)
monthNum_select=monthOptions.loc[monthOptions['Month'].isin(month_select)]['Num']
    


#%%Filter by sites selected
data_sites_og=data_raw[data_raw.site.isin(siteCodes)]
data_sites=data_sites_og.copy()
emptyDepths=data_sites.columns[data_sites.isnull().all()].to_list()

#%% 04 Select Depths

elementDF=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})
elementDF=elementDF[~elementDF[0].isin(emptyDepths)]

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



#%% Filter raw data by sites, depths and dates

#Filter by depths selected
columns_selected=element_select.to_list()
columns_selected.append('Date')
columns_selected.append('site')
data_sites=data_sites[columns_selected]

#add WY column from date
data_sites['year']=pd.DatetimeIndex(data_sites['Date']).year
data_sites['month']=pd.DatetimeIndex(data_sites['Date']).month
data_sites['WY']= data_sites.apply(lambda x: convert_to_WY(x), axis=1)


#calculate averageSoilMoisture making nan for missing data on ANY of the depths 
data_sites['averageSoilMoisture']=(data_sites[element_select.to_list()]).mean(axis=1,skipna=False)
data_sites_nonans = data_sites.dropna(subset=['averageSoilMoisture'])

#filter by month
data_sites_nonans=data_sites_nonans[data_sites_nonans['month'].isin(monthNum_select)]

#filter by months with days > 25 that have average soil moisture data 
#filter years by days > 330 days
if len(month_select)==12:
    dayCountThres=330
    data_sites_nonans=data_sites_nonans.groupby(['WY']).filter(lambda x : len(x)>=dayCountThres)
else:
    dayCountThres=25
    data_sites_nonans=data_sites_nonans.groupby(['month','WY']).filter(lambda x : len(x)>=dayCountThres)

#filter by WY
data_wy=data_sites_nonans[(data_sites_nonans['WY']>=startYear)&(data_sites_nonans['WY']<=endYear)]

st.header("Soil Moisture Percent (%) Start of Day Values")

data_wy.set_index('Date')

csv = convert_df(data_wy)
st.download_button(
     label="Download Daily Soil Moisture Data",
     data=csv,
     file_name='SMS_data.csv',
     mime='text/csv',
 )

#%% Data Availability Table
elementDF_og=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})

depths=elementDF_og[0]

data_sites_og['year']=pd.DatetimeIndex(data_sites_og['Date']).year

pvTable_gen=pd.pivot_table(data_sites_og, values=['minus_2inch_pct'],index='site', columns={'year'},aggfunc='count', margins=False, margins_name='Total')
pvTable_gen=pvTable_gen["minus_2inch_pct"].head(len(pvTable_gen))

pvTable_gen["Site"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_gen.index.to_list())].iloc[:,0].to_list()
pvTable_gen["System"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_gen.index.to_list())].iloc[:,2].to_list()

pvTable_Availability=pvTable_gen[['Site','System']]

pvTable_Availability["POR Start"]=""
pvTable_Availability["POR End"]=""

pvTable_Availability["2 inch"]=""
pvTable_Availability["4 inch"]=""
pvTable_Availability["8 inch"]=""
pvTable_Availability["20 inch"]=""
pvTable_Availability["40 inch"]=""

depth_cols=pvTable_Availability.columns[4:]

for i in range(0,len(pvTable_Availability)):
    pvTable_Availability["POR Start"].iloc[i]=data_sites_og[data_sites_og.site==pvTable_Availability.index[i]].Date.min()
    pvTable_Availability["POR End"].iloc[i]=data_sites_og[data_sites_og.site==pvTable_Availability.index[i]].Date.max()
    site=data_sites_og[data_sites_og.site==siteCodes.iloc[i]]
    emptyDepths=site.columns[site.isnull().all()].to_list()
    for j in range(0,len(depth_cols)):
        if depths.iloc[j] in emptyDepths:
            pvTable_Availability[depth_cols[j]].iloc[i]="X"
        else:
            pvTable_Availability[depth_cols[j]].iloc[i]="✓"
  
#add site and system as indexcpvTable_por.index[0]pvTable_por.index[0]
pvTable_Availability=pvTable_Availability.set_index(["Site"],drop=True)


st.header("Data Availability Table")
#display pivot table 
AvData=pvTable_Availability.style\
    .set_properties(**{'width':'10000px'})
    
st.dataframe(AvData)
#%% POR Statistics Table

pvTable_por=pd.pivot_table(data_sites_nonans, values=['averageSoilMoisture'],index='site', columns={'WY'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
pvTable_por=pvTable_por["averageSoilMoisture"].head(len(pvTable_por))

pvTable_wy=pd.pivot_table(data_wy, values=['averageSoilMoisture'],index='site', columns={'WY'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
pvTable_wy=pvTable_wy["averageSoilMoisture"].head(len(pvTable_wy))


pvTable_por["POR Start"]=""
pvTable_por["POR End"]=""
pvTable_por["POR Stat"]=np.nan
pvTable_por["POR Trend"]=np.nan
pvTable_por["Select WY Stat"]=np.nan
pvTable_por["Select WY Trend"]=np.nan

#add por start and por end
for i in range(0,len(pvTable_por)):
    pvTable_por["POR Start"].iloc[i]=data_sites_nonans[data_sites_nonans.site==pvTable_por.index[i]].Date.min()
    pvTable_por["POR End"].iloc[i]=data_sites_nonans[data_sites_nonans.site==pvTable_por.index[i]].Date.max()
    trend_data_por=pvTable_por.iloc[i,:-6]
    trend_data_wy=pvTable_wy.iloc[i,:]
    pvTable_por["POR Stat"].iloc[i]=trend_data_por.median()
    pvTable_por["Select WY Stat"].iloc[i]=trend_data_wy.median()
    try:
        tempMK=mk.original_test(trend_data_por)
        if tempMK[2]<0.1:
            pvTable_por["POR Trend"].iloc[i]=(tempMK[7])  
        else:
            pvTable_por["POR Trend"].iloc[i]=np.nan
    except:
        pvTable_por["POR Trend"].iloc[i]=np.nan
    try:
        tempMK_WY=mk.original_test(trend_data_wy)
        if tempMK_WY[2]<0.1:
            pvTable_por["Select WY Trend"].iloc[i]=(tempMK_WY[7])  
        else:
            pvTable_por["Select WY Trend"].iloc[i]=np.nan
    except:
        pvTable_por["Select WY Trend"].iloc[i]=np.nan

#add site and system as indexcpvTable_por.index[0]pvTable_por.index[0]
pvTable_por["Site"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_por.index.to_list())].iloc[:,0].to_list()
pvTable_por["System"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_por.index.to_list())].iloc[:,2].to_list()

pvTable_por=pvTable_por[["Site","System","POR Start","POR End","POR Stat", "POR Trend","Select WY Stat","Select WY Trend"]]
pvTable_por=pvTable_por.set_index(["Site"],drop=True)


st.header("Soil Moisture % Statistics ")

#display pivot table 
st.markdown("Trend (Theil-Sen Slope (inches/year) if Mann-Kendall trend test is significant (p-value <0.1); otherwise nan). Months with less than 25 days of data are not included in the analysis.")

displayTableDataPOR=pvTable_por.style\
    .set_properties(**{'width':'10000px'})\
    .format(precision=2)

st.dataframe(displayTableDataPOR)

#download pivot table
csv = convert_df(pvTable_por)
st.download_button(
      label="Download Statistics Table Data as CSV",
      data=csv,
      file_name='StatisticsTableSoilMoistureCompareSites.csv',
      mime='text/csv',
  )

#%% Create pivot table WY Soil moisture / Median SM for select water years range


pvTable_division=pvTable_wy.copy()
for i in range(0,len(pvTable_por)):
    pvTable_division.iloc[i]=pvTable_wy.iloc[i]/pvTable_por["Select WY Stat"].iloc[i]

pvTable_division["Site"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_division.index.to_list())].iloc[:,0].to_list()
# pvTable_division["System"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_division.index.to_list())].iloc[:,2].to_list()
pvTable_division=pvTable_division.set_index(["Site"],drop=True)


# pvTable=pvTable.rename(columns = months)

st.header("WY Soil Moisture / Median Soil Moisture for Select Water Years")

#display pivot table 
tableDataDiv=pvTable_division.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format("{:,.0%}")

st.dataframe(tableDataDiv)

#download pivot table
csv = convert_df(pvTable_division)
st.download_button(
     label="Download WY Soil Moisture/ Median Soil Moisture Data as CSV",
     data=csv,
     file_name='WY_SoilMoisture_byMedianSoilMoistureWY_CompareSites.csv',
     mime='text/csv',
 )




#%% Create pivot table using average soil moisture and show medians by WY


pvTable_wy["Site"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_wy.index.to_list())].iloc[:,0].to_list()
# pvTable_wy["System"]=AllsiteNames[AllsiteNames['1'].isin(pvTable_wy.index.to_list())].iloc[:,2].to_list()
pvTable_wy=pvTable_wy.set_index(["Site"],drop=True)


# pvTable=pvTable.rename(columns = months)

st.header("Soil Moisture % WY Median ")

#display pivot table 
tableData=pvTable_wy.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format(precision=1)

st.dataframe(tableData)

#download pivot table
csv = convert_df(pvTable_wy)
st.download_button(
     label="Download Table Data as CSV",
     data=csv,
     file_name='Median_SoilMoisture_byWY_CompareSites.csv',
     mime='text/csv',
 )


