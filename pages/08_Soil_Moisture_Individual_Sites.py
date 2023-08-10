# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:53:06 2022

@author: msparacino and mpedrazas
"""
#%% import packages

import streamlit as st #for displaying on web app
import pandas as pd
import requests
import datetime #for date/time manipulation
import pymannkendall as mk #for trend anlaysis
import numpy as np
import matplotlib.pyplot as plt #for plotting
from matplotlib import colors #for additional colors
from PIL import Image

st.set_page_config(page_title="Soil Moisture Individual Site", page_icon="🌱")
st.header("Individual Soil Moisture Site Data Assessment")

#%% Define data download as CSV function
#functions
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def convert_to_WY(row):
    if row.month>=10:
        return(datetime.date(row.year+1,1,1).year)
    else:
        return(datetime.date(row.year,1,1).year)
    
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

#%% Site data
siteNames = pd.read_csv("siteNamesListCode.csv")
siteNames = siteNames[siteNames['0'].str.contains("Buffalo Park|Echo Lake|Fool Creek")==False]

#%% Left Filters

#01 Select Site 
site_selected = st.sidebar.selectbox('Select your site:', siteNames.iloc[:,0])
siteCode=siteNames[siteNames.iloc[:,0]==site_selected].iloc[0][1]
#siteCode='SNOTEL:485_CO_SNTL'

#%% SOIL MOISTURE DATA filtered by site, parameter and date
#Selections
sitecodeSMS=siteCode.replace("SNOTEL:", "" )
sitecodeSMS=sitecodeSMS.replace("_", ":" )

elementDF=pd.DataFrame({0:["SMS:-2:value","SMS:-4:value", "SMS:-8:value","SMS:-20:value","SMS:-40:value"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})

element_select=elementDF['long']
element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]
elementStr= ','.join(element_select)

if len(element_select)==0:
    st.sidebar.error("Select at least one depth")

headerAdj=pd.DataFrame({'ElementCount':[0,1,2,3,4,5],"HeaderRowCount":[57,58,59,60,61,62]})
headerCount=headerAdj['HeaderRowCount'][headerAdj['ElementCount']==len(element_select)]

base="https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
part1="customMultiTimeSeriesGroupByStationReport/daily/start_of_period/"
site=sitecodeSMS
por="%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/"#  "%7Cid=%22%22%7Cname/" + str(startYear-1) + "-10-01," + str(endYear) + "-09-30/"
element=elementStr
part2="?fitToScreen=false"
url=base+part1+site+por+element+part2

s=requests.get(url).text

urlDataRaw=pd.read_csv(url,header=headerCount.iloc[0],delimiter=',')#headerCount.iloc[0]

#filter out data >100%
datecol=urlDataRaw['Date']
cols=urlDataRaw.columns[1:]
urlData=urlDataRaw[cols].applymap(lambda x: np.nan if x > 100 else x)
urlData['Date']=datecol
cols2=urlData.columns.tolist()
cols2 = [cols2[-1]]+cols2[:-1] 
urlData=urlData.reindex(columns=cols2)

urlData.columns=['Date','minus_2inch_pct','minus_4inch_pct','minus_8inch_pct','minus_20inch_pct','minus_40inch_pct']

#add WY column from date
urlData['year']=urlData['Date'].str[0:4].astype(int)
urlData['month']=urlData['Date'].str[5:7].astype(int)
urlData['WY']= urlData.apply(lambda x: convert_to_WY(x), axis=1)

#  THIS DOES NOT FILTER OUT YEARS WITH FEWER THAN 330 OBSERVATIONS, 
#  IT ONLY FILTERS OUT YEARS WITH FEWER THAN 330 RECORDS - i.e., it only
#  filters out the most recent water year (which is undesireable )
# dayCountThres=330
# g=urlData.groupby(['WY'])
# data=g.filter(lambda x: len(x)>=dayCountThres)

dayCountThres=25
g=urlData.groupby(['WY','month'])
data=g.filter(lambda x: len(x)>=dayCountThres)

urlData=data
PORData=urlData

#%% Figure out which depths dont have any data and don't include
emptyDepths=PORData.columns[PORData.isnull().all()].to_list()

depth_dict={"minus_2inch_pct":"2 inch depth",
            "minus_4inch_pct":"4 inch depth",
            "minus_8inch_pct":"8 inch depth",
            "minus_20inch_pct":"20 inch depth",
            "minus_40inch_pct":"40 inch depth"}

emptyDepths_items=[depth_dict.get(k) for k in emptyDepths]  

#%%02 Select Depths

elementDF=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                           'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})
elementDF=elementDF[~elementDF[0].isin(emptyDepths)]

container=st.sidebar.container()
paramsSelect=elementDF['long']
element_select=container.multiselect('Select depth(s):',paramsSelect,default=elementDF['long'])
element_select=elementDF.loc[elementDF['long'].isin(element_select)][0]
elementStr= ','.join(element_select)
    
#element_select=element_select[:-1]
if len(element_select)==0:
    st.sidebar.error("Select at least one depth")

#%%Filter by depths selected
columns_selected=element_select.to_list()
columns_selected.append('Date')
columns_selected.append('WY')
columns_selected.append('month')
dateFiltered=urlData[columns_selected]

#%%03 Select Water Year
endY=dateFiltered['WY'].max()
startY=dateFiltered['WY'].min()

start_date = "%s-%s-0%s"%(startY,10,1) 
end_date = "%s-%s-0%s"%(endY,9,30) 

min_date = datetime.datetime(startY,10,1) #dates for st slider need to be in datetime format:
max_date = datetime.datetime(endY,9,30)

startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=endY, value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:', min_value=startY, max_value=endY,value=endY)

#%%filter by water year
dateFiltered=dateFiltered[(dateFiltered['WY']>=startYear)&(dateFiltered['WY']<=endYear)]
         
if len(urlData)==0:
    "no data for this depth"
else:
    #%% Data Availability Table
    elementDF_og=pd.DataFrame({0:["minus_2inch_pct","minus_4inch_pct", "minus_8inch_pct","minus_20inch_pct","minus_40inch_pct"], 
                                'long': ['2 inch depth', '4 inch depth','8 inch depth', '20 inch depth','40 inch depth']})
    depths=elementDF_og['long']
    
    site_dateFiltered=PORData.copy()
    site_dateFiltered['site']=site_selected
    
    pvTable_gen=pd.pivot_table(site_dateFiltered,values=['WY'],index='site', columns={'year'},aggfunc='count', margins=False, margins_name='Total')
    pvTable_gen=pvTable_gen["WY"].head(len(pvTable_gen))

    temp=siteNames[siteNames['0'].isin(pvTable_gen.index.to_list())]
    temp.set_index('0',inplace=True)
    temp.columns=['Code','System']
    temp['Site']=temp.index
    pvTable_gen=pd.concat([pvTable_gen,temp],axis=1)
    
    pvTable_Availability=pvTable_gen[['Site','System']]

    pvTable_Availability["POR Start"]=""
    pvTable_Availability["POR End"]=""

    pvTable_Availability["2 inch"]=""
    pvTable_Availability["4 inch"]=""
    pvTable_Availability["8 inch"]=""
    pvTable_Availability["20 inch"]=""
    pvTable_Availability["40 inch"]=""

    depth_cols=pvTable_Availability.columns[-5:]

    for siteTemp in pvTable_Availability.index:
        print(siteTemp)
        pvTable_Availability["POR Start"].loc[siteTemp]=site_dateFiltered[site_dateFiltered.site==siteTemp].Date.min()
        pvTable_Availability["POR End"].loc[siteTemp]=site_dateFiltered[site_dateFiltered.site==siteTemp].Date.max()
        site=site_dateFiltered
               
        for j in range(0,len(depth_cols)):
            print(j)
            if depths.iloc[j] in emptyDepths_items:
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
    
    #%% download data
    csv = convert_df(PORData)
    st.download_button(
         label="Download Daily Soil Moisture Data (as CSV)",
         data=csv,
         file_name='SMS_data.csv',
         mime='text/csv',
     )
    #%% Create pivot table using average soil moisture and show medians by WY
    st.subheader("Depth Averaged Monthly Median Soil Moisture (%) by Water Year(s)")
    st.markdown(
"""
Provides the depth averaged median soil moisture (percent) for each month within the selected water years: 
- Only depths with available soil moisture data are available for selection in the depth filter.  
- If multiple depths are selected, the monthly median is assessed using the daily soil moisture percentage, averaged across selected depths.
- If multiple depths are selected, the monthly median results will only be provided for months and water years with data for all selected depths.  
    - For example, Berthoud Summit has full POR data (2003 – 2022) for 2, 8, and 20-inch depths. The 4-inch depth data is limited to 2018 – 2022. If all four depths are selected and if the beginning and ending water years are 2003 – 2022, only data from 2018 – 2022 will be presented.
"""
)

    dateFiltered['averageSoilMoisture']=(dateFiltered[element_select.to_list()]).mean(axis=1,skipna=False)
    dateFiltered_nonans = dateFiltered.dropna(subset=['averageSoilMoisture'])
        
    #filter by months with days > 25 that have average soil moisture data 
    smData=dateFiltered_nonans.groupby(['month','WY']).filter(lambda x : len(x)>=dayCountThres)
  
    if len(smData)==0:
        "no data for selected depths"
    else:
        pvTable=pd.pivot_table(smData, values=['averageSoilMoisture'],index='WY', columns={'month'},aggfunc=np.nanmedian, margins=False, margins_name='Total')
        pvTable=pvTable["averageSoilMoisture"].head(len(pvTable))
        pvTable=pvTable.rename(columns = months)
        pvTable=pvTable[["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]]
        pvTable.sort_index(axis='rows',level='WY',ascending=False,inplace=True)
        pvTable.index = pvTable.index.astype(str)
        #display pivot table 
        tableData=pvTable.style\
            .set_properties(**{'width':'10000px'})\
            .apply(background_gradient, axis=None)\
            .format(precision=2)
        
        tableStartY=smData['WY'].min()-1
        tableEndY=smData['WY'].max()
        
        tableDepths=list(element_select)
        tableDepths2=elementDF.loc[elementDF[0].isin(tableDepths)]['long']
        tableDepths2Str= ', '.join(tableDepths2)
        
        st.markdown(
            """
            Based on average for %s for selected water year(s): %s-10-01 through %s-9-30   
            """%(tableDepths2Str, tableStartY, tableEndY)
            )
        
        st.dataframe(tableData)
        st.markdown(
    """
Table Notes:
- Months with fewer than 25 results are not shown.
- NRCS raw data occasionally includes soil moisture percentages that exceed 100%; these values are excluded from the calculations presented in this table.  
    """)
        
        #download pivot table
        csv = convert_df(pvTable)
        st.download_button(
             label="Download Depth Averaged Monthly Median Soil Moisture % (as CSV)",
             data=csv,
             file_name='Median_SoilMoisture.csv',
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
        st.subheader("Monthly Summary Statistics for Selected Water Year(s) with Available Data")
        st.markdown(
            """
Provides the monthly median and monthly trend for soil moisture for the selected depth(s) and selected water year(s):
- Monthly median value, or midpoint, for the selected water year(s) for soil moisture (percent). If multiple depths are selected, the median will only be provided for the months and years with data for all depths. 
- Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for monthly median soil moisture (percent per year) where all selected depths have available data. 
    - A negative trend indicates lower soil moisture in a given month and a positive trend indicates higher soil moisture in a given month.
"""
            )
        displayTableData=medianTableData.style\
            .set_properties(**{'width':'10000px'})\
            .format('{:,.2f}',subset=(['Median'],slice(None)))\
            .format('{:,.3f}',subset=(['Trend'],slice(None)))\
            
        st.markdown(
            """
            Based on average for %s for selected water year(s): %s-10-01 through %s-9-30  
            """%(tableDepths2Str, tableStartY, tableEndY)
            )
        
        st.dataframe(displayTableData)
        st.markdown(
    """
Table Note:        
- If no trend, then result is presented as "None". 
 """
    )        
        #download pivot table
        csv = convert_df(medianTableData)
        st.download_button(
              label="Download Monthly Statistics Table (as CSV)",
              data=csv,
              file_name='StatisticsTablebyMonth.csv',
              mime='text/csv',
          )
#%% Stations display information
st.subheader("Soil Moisture Station Locations ")
image=Image.open("Maps/3_Soil_Moisture.png")
st.image(image, width=500)