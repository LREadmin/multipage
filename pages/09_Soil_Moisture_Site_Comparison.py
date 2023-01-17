# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:53:06 2022

@author: msparacino and mpedrazas
"""
#%% import packages

import streamlit as st #for displaying on web app

import pandas as pd

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

import numpy as np
import matplotlib.pyplot as plt #for plotting
from matplotlib import colors #for additional colors

from PIL import Image


#%% Title page

st.set_page_config(page_title="Soil Moisture Site Comparison", page_icon="🌱")
st.header("Soil Moisture Site Comparison Data Assessment")


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

# remove sites without soil moisture data
AllsiteNames = AllsiteNames[AllsiteNames['0'].str.contains("Buffalo Park|Echo Lake|Fool Creek")==False]
#%% Load SMS data
data_raw=pd.read_csv('SNOTEL_SMS.csv.gz')

data=data_raw.iloc[: , [1,2,3,4,5,6]].copy()
dates_new=pd.to_datetime(data_raw.loc[:]['Date']).dt.strftime('%Y-%m-%d')
data=pd.concat([data,dates_new],axis=1)

#add WY column from date
data['year']=pd.DatetimeIndex(data['Date']).year
data['month']=pd.DatetimeIndex(data['Date']).month
data['WY']= data.apply(lambda x: convert_to_WY(x), axis=1)

#%% 01 select months
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
    month_select = container.multiselect('Select Month(s):',pd.concat([winterMonths,springMonths]), pd.concat([winterMonths,springMonths]))
elif winter and summer and (fall==False) and (spring==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([winterMonths,summerMonths]), pd.concat([winterMonths,summerMonths]))
elif winter and fall and (spring==False) and (summer==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([winterMonths,fallMonths]), pd.concat([winterMonths,fallMonths]))
elif winter and (fall==False) and (spring==False) and (summer==False):
    month_select = container.multiselect('Select Month(s):',winterMonths, winterMonths)
elif spring and (fall==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select Month(s):',springMonths, springMonths)
elif fall and spring and (winter==False) and (summer==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([springMonths,fallMonths]), pd.concat([springMonths,fallMonths]))
elif spring and summer and (winter==False) and (fall==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([springMonths,summerMonths]), pd.concat([springMonths,summerMonths]))
elif summer and fall and (winter==False) and (spring==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([summerMonths,fallMonths]), pd.concat([summerMonths,fallMonths]))
elif summer and (fall==False) and (winter==False) and (spring==False):
    month_select = container.multiselect('Select Month(s):',summerMonths, summerMonths)
elif fall and (spring==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select Month(s):',fallMonths, fallMonths)
elif fall and summer and spring and (winter==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([springMonths,summerMonths,fallMonths]), pd.concat([springMonths,summerMonths,fallMonths]))
elif fall and summer and winter and (spring==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([winterMonths,summerMonths,fallMonths]), pd.concat([winterMonths,summerMonths,fallMonths]))
elif spring and summer and winter and (fall==False):
    month_select = container.multiselect('Select Month(s):',pd.concat([winterMonths,springMonths,summerMonths]), pd.concat([winterMonths,springMonths,summerMonths]))
elif spring and fall and summer and winter:
    month_select = container.multiselect('Select Month(s):',pd.concat([springMonths,winterMonths,summerMonths,fallMonths]), pd.concat([springMonths,winterMonths,summerMonths,fallMonths]))

else:
    month_select = container.multiselect('Select Month(s):', monthSelect,default=monthSelect)

monthNum_select=pd.DataFrame(month_select)
monthNum_select=monthOptions.loc[monthOptions['Month'].isin(month_select)]['Num']

def monthfilter():
    return data[data['month'].isin(monthNum_select)]

data=monthfilter()

if len(month_select)==12:
    dayCountThres=330
    g=data.groupby(['site','WY'])
    data=g.filter(lambda x: len(x)>=dayCountThres)
else:
    dayCountThres=25
    g=data.groupby(['site','WY','month'])
    data=g.filter(lambda x: len(x)>=dayCountThres)

#%% 02 Select System
container=st.sidebar.container()
all=st.sidebar.checkbox("Select Both Collection Systems")

if all:
    system_selected = container.multiselect('Select Collection system(s):', AllsiteNames.iloc[:,2].drop_duplicates(), AllsiteNames.iloc[:,2].drop_duplicates())
else: 
    system_selected = container.multiselect('Select Collection system(s):', AllsiteNames.iloc[:,2].drop_duplicates(), default='North')

siteNames=AllsiteNames[AllsiteNames['2'].isin(system_selected)]

#%% 03 Select Site 

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all sites")

if all:
    site_selected = container.multiselect('Select Your Site(s):', siteNames.iloc[:,0], siteNames.iloc[:,0])
else: 
    site_selected = container.multiselect('Select Your Site(s):', siteNames.iloc[:,0], default=siteNames.iloc[0,0])

siteCodes=siteNames[siteNames['0'].isin(site_selected)].iloc[:,1]
siteNames=siteNames[siteNames['0'].isin(site_selected)].iloc[:,0] 

#%%Filter by sites selected
data_sites=data[data.site.isin(siteCodes)]
#data_sites=data_sites_og.copy()
emptyDepths=data_sites.columns[data_sites.isnull().all()].to_list()

#%% Data Availability Table
elementDF_og=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})

depths=elementDF_og[0]

pvTable_gen=pd.pivot_table(data_sites,values=['WY'],index='site', columns={'year'},aggfunc='count', margins=False, margins_name='Total')
pvTable_gen=pvTable_gen["WY"].head(len(pvTable_gen))

temp=AllsiteNames[AllsiteNames['1'].isin(pvTable_gen.index.to_list())]
temp.set_index('1',inplace=True)
temp.columns=['Site','System']
pvTable_gen=pd.concat([pvTable_gen,temp],axis=1)

pvTable_Availability=pvTable_gen[['Site','System']]

pvTable_Availability["POR Start"]=""
pvTable_Availability["POR End"]=""

pvTable_Availability["2 inch"]=""
pvTable_Availability["4 inch"]=""
pvTable_Availability["8 inch"]=""
pvTable_Availability["20 inch"]=""
pvTable_Availability["40 inch"]=""

depth_cols=pvTable_Availability.columns[4:]

for siteTemp in pvTable_Availability.index:
    print(siteTemp)
    pvTable_Availability["POR Start"].loc[siteTemp]=data_sites[data_sites.site==siteTemp].Date.min()
    pvTable_Availability["POR End"].loc[siteTemp]=data_sites[data_sites.site==siteTemp].Date.max()
    site=data_sites[data_sites.site==siteTemp]
    
    emptyDepths=site.columns[site.isnull().all()].to_list()
    sitetemp=site[['minus_2inch_pct','Date']].Date.min()
    
    for j in range(0,len(depth_cols)):
        print(j)
        if depths.iloc[j] in emptyDepths:
            pvTable_Availability[depth_cols[j]].loc[siteTemp]="X"
        else:
            temp=site[[elementDF_og.loc[j][0],'Date']]
            temp.dropna(inplace=True)
            if ((temp.Date.min()==pvTable_Availability['POR Start'].loc[siteTemp]) and (temp.Date.max()==pvTable_Availability['POR End'].loc[siteTemp])):
                pvTable_Availability[depth_cols[j]].loc[siteTemp]="✓"
            else:
                pvTable_Availability[depth_cols[j]].loc[siteTemp]="%s to %s"%(temp.Date.min(),temp.Date.max())#"✓"
  
#add site and system as indexcpvTable_por.index[0]pvTable_por.index[0]
pvTable_Availability=pvTable_Availability.set_index(["Site"],drop=True)

#%% 04 Select Depths

elementDF=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})
elementDF=elementDF[~elementDF[0].isin(emptyDepths)]

container=st.sidebar.container()
paramsSelect=elementDF['long']
element_select=container.multiselect('Select depth(s):',paramsSelect,default=elementDF['long'])
element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]
elementStr= ','.join(element_select)

#%%05 Select Water Year
endY=data_sites['WY'].max()
startY=data_sites['WY'].min()

start_date = "%s-%s-0%s"%(startY,10,1) 
end_date = "%s-%s-0%s"%(endY,9,30) 

min_date = datetime.datetime(startY,10,1) #dates for st slider need to be in datetime format:
max_date = datetime.datetime(endY,9,30)

startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=endY, value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:', min_value=startY, max_value=endY,value=endY)

#%% Filter raw data by sites, depths and dates

#Filter by depths selected
columns_selected=element_select.to_list()
columns_selected.append('Date')
columns_selected.append('WY')
columns_selected.append('month')
columns_selected.append('site')
data_sites=data_sites[columns_selected]

#calculate averageSoilMoisture making nan for missing data on ANY of the depths 
data_sites['averageSoilMoisture']=(data_sites[element_select.to_list()]).mean(axis=1,skipna=False)
data_sites_nonans = data_sites.dropna(subset=['averageSoilMoisture'])

if len(month_select)==12:
    g=data_sites_nonans.groupby(['site','WY'])
    data_sites_nonans=g.filter(lambda x: len(x)>=dayCountThres)
else:
    g=data_sites_nonans.groupby(['site','WY','month'])
    data_sites_nonans=g.filter(lambda x: len(x)>=dayCountThres)
  
#filter by WY
data_wy=data_sites_nonans[(data_sites_nonans['WY']>=startYear)&(data_sites_nonans['WY']<=endYear)]
nameTemp=AllsiteNames.copy()
nameTemp.columns=['Name','site','system']
data_wy=pd.merge(data_wy,nameTemp,on=['site'])

data_wy.set_index('Date')

#%% POR Statistics Table

pvTable_por=pd.pivot_table(data_sites_nonans, values=['averageSoilMoisture'],index='site', columns={'WY'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
pvTable_por=pvTable_por["averageSoilMoisture"].head(len(pvTable_por))

pvTable_wy=pd.pivot_table(data_wy, values=['averageSoilMoisture'],index='site', columns={'WY'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
pvTable_wy=pvTable_wy["averageSoilMoisture"].head(len(pvTable_wy))

pvTable_por["POR Start"]=""
pvTable_por["POR End"]=""
pvTable_por["POR Median"]=np.nan
pvTable_por["POR Trend"]=np.nan
pvTable_por["Select WY Median"]=np.nan
pvTable_por["Select WY Trend"]=np.nan

#add por start and por end
for siteTemp2 in pvTable_por.index:
    print(siteTemp2)
    pvTable_por["POR Start"].loc[siteTemp2]=data_sites_nonans[data_sites_nonans.site==siteTemp2].Date.min()
    pvTable_por["POR End"].loc[siteTemp2]=data_sites_nonans[data_sites_nonans.site==siteTemp2].Date.max()
    
    # get select WY start and end
    tableStartY=data_wy[data_wy.site==siteTemp2].Date.min()
    tableEndY=data_wy[data_wy.site==siteTemp2].Date.max()
    
    trend_data_por=pvTable_por.loc[siteTemp2][:-6]
    trend_data_wy=pvTable_wy.loc[siteTemp2][:]
    pvTable_por["POR Median"].loc[siteTemp2]=trend_data_por.median()
    pvTable_por["Select WY Median"].loc[siteTemp2]=trend_data_wy.median()
    try:
        tempMK=mk.original_test(trend_data_por)
        if tempMK[2]<0.1:
            pvTable_por["POR Trend"].loc[siteTemp2]=(tempMK[7])  
        else:
            pvTable_por["POR Trend"].loc[siteTemp2]=np.nan
    except:
        pvTable_por["POR Trend"].loc[siteTemp2]=np.nan
    try:
        tempMK_WY=mk.original_test(trend_data_wy)
        if tempMK_WY[2]<0.1:
            pvTable_por["Select WY Trend"].loc[siteTemp2]=(tempMK_WY[7])  
        else:
            pvTable_por["Select WY Trend"].loc[siteTemp2]=np.nan
    except:
        pvTable_por["Select WY Trend"].loc[siteTemp2]=np.nan

#add site and system as indexcpvTable_por.index[0]pvTable_por.index[0]
pvTable_por['Site']=""
pvTable_por['System']=""
for i in range(0,len(pvTable_por)):
    pvTable_por["Site"].iloc[i]=AllsiteNames[AllsiteNames['1']== pvTable_por.index[i]]['0'].iloc[0]
    pvTable_por["System"].iloc[i]=AllsiteNames[AllsiteNames['1']== pvTable_por.index[i]]['2'].iloc[0]


pvTable_por=pvTable_por[["Site","System","POR Start","POR End","POR Median", "POR Trend","Select WY Median","Select WY Trend"]]
pvTable_por=pvTable_por.set_index(["Site"],drop=True)

displayTableDataPOR=pvTable_por.style\
    .set_properties(**{'width':'10000px'})\
    .format({'POR Median':"{:.2f}",'POR Trend':"{:.3f}"
              ,'Select WY Median':"{:.2f}",'Select WY Trend':"{:.3f}"})\

#%% Create pivot table WY Soil moisture / Median SM for select water years range

pvTable_division=pvTable_wy.copy()
pvTable_division.sort_index(axis='columns',level='WY',ascending=False,inplace=True)
pvTable_wy.sort_index(axis='columns',level='WY',ascending=False,inplace=True)

for i in range(0,len(pvTable_division)):
    pvTable_division.iloc[i]=pvTable_wy.iloc[i]/pvTable_por["Select WY Median"].iloc[i]

pvTable_division["Site"]=""
pvTable_division['System']=""
for i in range(0,len(pvTable_division)):
    pvTable_division["Site"].iloc[i]=AllsiteNames[AllsiteNames['1']==pvTable_division.index[i]]['0'].iloc[0]
    pvTable_division["System"].iloc[i]=AllsiteNames[AllsiteNames['1']== pvTable_division.index[i]]['2'].iloc[0]

pvTable_division=pvTable_division.set_index(["Site", "System"],drop=True)

#display pivot table 
tableDataDiv=pvTable_division.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format("{:,.0%}")


#%% Create pivot table using average soil moisture and show medians by WY

pvTable_wy["Site"]=""
pvTable_wy['System']=""
for i in range(0,len(pvTable_wy)):
    pvTable_wy["Site"].iloc[i]=AllsiteNames[AllsiteNames['1']==pvTable_wy.index[i]]['0'].iloc[0]
    pvTable_wy["System"].iloc[i]=AllsiteNames[AllsiteNames['1']== pvTable_wy.index[i]]['2'].iloc[0]

pvTable_wy=pvTable_wy.set_index(["Site","System"],drop=True)
#pvTable_wy=pvTable_wy/100

#display pivot table 
tableDataMedian=pvTable_wy.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format(precision=2)

#%% DIsplay
#%% Available Data Summary
st.subheader("Available Data Summary ")
st.markdown("""
Provides the following information for the selected site:
- **System:** Location of the site within the Collection System (North or South System)
- **POR Start:** Earliest date of available data for the site
- **POR End:** Latest date of available data for site
- **Available Data from Sample Depths** (2, 4, 8, 20, and 40-inch depths):
    - **✓** = Data available for entire POR
    - **X** = No data available for that depth
    - **Date Range** = Data available for some of the POR
                """)

#display pivot table 
AvData=pvTable_Availability.style\
    .set_properties(**{'width':'10000px'})

st.dataframe(AvData)

csv = convert_df(data_wy)
st.download_button(
     label="Download Daily Soil Moisture Data (as CSV)",
     data=csv,
     file_name='SMS_data.csv',
     mime='text/csv',
 )   
#%% Median

st.subheader("Depth Averaged Monthly Median Soil Moisture (%) by Water Year(s)")
st.markdown(
"""
Provides the depth-averaged median soil moisture (percent) for the selected water years and selected month(s)/season(s):  
- Only depths with available soil moisture data are available for selection in the depth filter.  
- If multiple depths are selected, the monthly median is assessed using the daily soil moisture percentage, averaged across selected depths.
- If multiple depths are selected, the monthly median results will only be provided for months and water years with data for all selected depths.  
"""
)
##note the following: If fall months (September, October, November) are selected for all depths and the full POR for Berthoud Summit, the column for water year 2018 in the following table will display the depth averaged median soil moisture percentage for 9/1/2018 thorugh 9/30/2018. The column for water year 2019 in the following table will display the depth averaged median soil moisture percentage for 10/1/2018 thorugh 11/30/2018 combined with 9/1/2019 through 9/30/2019. 

    
tableDepths=list(element_select)
tableDepths2=elementDF.loc[elementDF[0].isin(tableDepths)]['long']
tableDepths2Str= ', '.join(tableDepths2)

st.markdown(
    """
    Based on average for %s for user-selected month(s)/season(s) in selected water year(s): %s through %s    
    """%(tableDepths2Str, tableStartY, tableEndY)
    )

st.dataframe(tableDataMedian)
st.markdown(
    """
Table Notes:
- Excludes user-selected sites if no data exists for one of the user-selected depths ("X" in Available Data Summary Table). 
- If full year (12 months) is selected, years with fewer than 330 results are excluded and the result is presented as “nan.”
- If less than 12 months are selected, months with fewer than 25 results are excluded and presented as “nan.""
    """)
#download pivot table
csv = convert_df(pvTable_wy)
st.download_button(
     label="Download Depth Averaged Monthly Median Soil Moisture % (as CSV)",
     data=csv,
     file_name='Median_SoilMoisture_byWY_CompareSites.csv',
     mime='text/csv',
)
#%% Summary Statistics Table
st.subheader("Summary Statistics for the Selected Sites, Water Year(s) and Month(s)/Season(s)")
st.markdown(
    """
Provides the following information for the selected site:
- **System:** Location of the site within the Collection System (North or South System)
- **POR Start:** Earliest date of available data for the site
- **POR End:** Latest date of available data for site
- **POR Median:** Median soil moisture (percent) for the month(s)/season(s) for the entire period of record, regardless of selected water year(s).
- **POR Trend:** Soil moisture trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for entire period of record:
    - **Soil Moisture** (increasing or decreasing percent per year)
- **Selected WY Median:** Soil moisture median for the Months/Seasons of the selected Water Year(s).
- **Selected WY Trend:** Soil moisture trend (percent per year) using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for the month(s)/season(s) of the selected water year(s).
"""
    )
    
st.markdown(
    """
    POR and selected water year(s) depths based on average for %s and user-selected month(s)/season(s). Selected water year(s): %s through %s   
    """%(tableDepths2Str, tableStartY, tableEndY)
    )

st.dataframe(displayTableDataPOR)
st.markdown(
    """
Table Notes:
- Excludes user-selected sites if no data exists for one of the user-selected depths ("X" in Avaiable Data Summary Table). 
- If no trend, then result is presented as “nan.” 
    """)


#download pivot table
csv = convert_df(pvTable_por)
st.download_button(
      label="Download Summary Soil Moisture Table (as CSV)",
      data=csv,
      file_name='StatisticsTableSoilMoistureCompareSites.csv',
      mime='text/csv',
  )

#%% % difference
st.subheader("Percent of Monthly Median Soil Moisture Compared to the Monthly Median Soil Moisture for Selected Water Year Range")
st.markdown(
    """
The percent is calculated by dividing the depth-averaged soil moisture median in selected month(s)/season(s) in a selected water year by the median soil moisture for the selected water year range for the selected month(s)/season(s) and multiplying by 100. 
- For example, the depth-averaged soil moisture median for Fall (September, October, and November) 2017 at Middle Fork Camp (3.1%) is divided by the median for the selected Water Year range of 2002 – 2022 for the same months (4.4%) and multiplied by 100.  The result shows that soil moisture for fall 2017 at Middle Fork Camp was 71% of the median for the selected water years of 2002 – 2022. 
    """)

st.markdown(
    """
    Based on average for %s for user-selected month(s)/season(s) in water year(s): %s through %s   
    """%(tableDepths2Str, tableStartY, tableEndY)
    )

st.dataframe(tableDataDiv)
st.markdown(
    """
Table Notes:
- Excludes user-selected sites if no data exists for one of the user-selected depths ("X" in Available Data Summary Table). 
- If full year (12 months) is selected, years with fewer than 330 results are excluded and the result is presented as “nan.”
- If less than 12 months are selected, months with fewer than 25 results are excluded and presented as “nan.""
    """)
#download pivot table
csv = convert_df(pvTable_division)
st.download_button(
     label="Download % Comparison (as CSV)",
     data=csv,
     file_name='SMS_percent_comp.csv',
     mime='text/csv',
 )
#%% Stations display information
st.subheader("Soil Moisture Station Locations ")
image=Image.open("Maps/3_Soil_Moisture.png")
st.image(image, width=500)