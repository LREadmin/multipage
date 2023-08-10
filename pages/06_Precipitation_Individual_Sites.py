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
import numpy as np
from PIL import Image


#%% Website display information
st.set_page_config(page_title="Precipitation Individual Sites", page_icon="🌦")
st.header("Individual Precipitation Site Data Assessment")

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
sites = {
    'Antero (AN)': 'AN',
    'Cheesman (CM)': 'CM',
    'DIA (DI)': 'DI',
    'Dillon (DL)': 'DL',
    'DW Admin (DW)': 'DW',
    'Evergreen (EG)': 'EG',
    'Eleven Mile (EM)': 'EM',
    'Gross (GR)': 'GR',
    'Kassler (KS)': 'KS',
    'Moffat HQ (MF)': 'MF',
    'Ralston (RS)': 'RS',
    'Central Park (SP)': 'SP',
    'Strontia (ST)': 'ST',
    'Williams Fork (WF)': 'WF'}
# The long names are hard coded, so there's no reason to grab the abbreviations
# from the data frame. 
# As written, the long name the user selected DID NOT map to the correct site
# abbreviation. (i.e. "Antero (AN)" was mapping to "RS"). 
# sites=pandas.DataFrame(data_raw['site'].drop_duplicates())
# sites['long']=['Antero (AN)','Cheesman (CM)','DIA (DI)','Dillon (DL)','DW Admin (DW)','Evergreen (EG)',
#                'Eleven Mile (EM)','Gross (GR)','Kassler (KS)','Moffat HQ (MF)','Ralston (RS)','Central Park (SP)',
#                'Strontia (ST)','Williams Fork (WF)']

#%% filter first for parameters
params_select = "Accumulated Precipitation (in)"
param=paramsDF.loc[paramsDF['long']==params_select][0]
data_param=data_raw

#%%
data1=data_param[[param.iloc[0],'pcpn','Month','site','CY','WY']]

#%% filter second for site
# TODO: test whether this will work without converting keys from dict_keys type
site_select_long = st.sidebar.selectbox('Select One Site:', list(sites.keys()))
#site_select_long="Ralston (RS)"
site_select=sites[site_select_long]

def sitefilter():
    return data1.loc[data1['site'] == site_select]

data_param_site=sitefilter()

#%% filter third for date
endY=data_param_site['WY'].max()
startY=data_param_site['WY'].min()

startM=10
startD=1

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=endY,value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY, max_value=endY,value=endY)
def dateSelection():
    return data_param_site[(data_param_site['WY']>=startYear)&(data_param_site['WY']<=endYear)]

data_param_site_date=dateSelection()

tableStartDate=datetime.datetime(startYear-1,10,1).strftime("%Y-%m-%d")

tableEndDate=datetime.datetime(endYear,9,30).strftime("%Y-%m-%d")

#%%threshold filter
maxDaily=round(data_param_site_date['pcpn'].max(),2)
minDaily=round(data_param_site_date['pcpn'].min(),2)

thresholdHigh = st.sidebar.number_input('Set Upper Precipitation (in/day) Threshold (Inclusive):',step=0.1,min_value=minDaily, value=maxDaily)

thresholdLow = st.sidebar.number_input('Set Lower Precipitation (in/day) Threshold (Inclusive):',step=0.1,min_value=minDaily, value=minDaily)

#%%calc statistic for all months
yearList=data_param_site_date['WY'].drop_duplicates()
newParamData=[]
newParamData1=[]

for row in yearList:
    tempData=data_param_site_date[data_param_site_date['WY']==row]
    
    #filter by day count threshold
    dayCountThres=25
    yearCountThres=0
    
    if tempData['pcpn'].count().sum()>0:
       
        for row1 in monthList:
            try:    
                tempData2=tempData[tempData['Month']==row1]
                        
                tempData2=tempData2.drop(columns='site')
                if len(tempData2)==0:
                    count=[np.nan, np.nan, np.nan]
                    na_count = 0
                    # count[1]=np.nan 
                else:
                    count=tempData2[(tempData2 <= thresholdHigh)&(tempData2 >= thresholdLow)].count()
                    na_count=tempData2['pcpn'].isna().sum()
                    
                if len(tempData2)==0:
                    monthlyCumPrecip=np.nan
                else:
                    monthlyCumPrecip=tempData2.pcpn.sum() #calculate monthly total
                    
                newParamData.append([row,row1,monthlyCumPrecip,na_count])
                newParamData1.append([row,row1,count[1],na_count])
            except:
                pass
    else:
       newParamData.append([row,np.nan,np.nan,np.nan])
       newParamData1.append([row,np.nan,np.nan,np.nan]) 

paramDataMerge=pandas.DataFrame(newParamData,columns=['WY','Month',params_select,'count']) #sum pcpn
cols=paramDataMerge.columns
# paramDataMerge.loc[((paramDataMerge['count']>dayCountThres)),cols[2]]=np.nan

# Incorrect! The columns are: WY, Month, Result count, NA Count

# paramDataMerge1=pandas.DataFrame(newParamData1,columns=['WY','Month',params_select,'count']) #count
# You know what, I'm just going to change it. Screw the consequences
paramDataMerge1=pandas.DataFrame(newParamData1,columns=['WY','Month','data_count','na_count']) #count
na_inx = np.where(paramDataMerge1.data_count < dayCountThres)[0]
paramDataMerge.loc[na_inx, cols[2]] = np.nan

# cols=paramDataMerge1.columns
# paramDataMerge1.loc[((paramDataMerge1['count']>dayCountThres)),cols[2]]=np.nan

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
data4.dropna(axis=1, how='all',inplace=True)
data4.columns=monthNames
data4=data4[["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]]

medianData=pandas.DataFrame([["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"],data4.median()])

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
sumStats=sumStats[["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]]

#%%colormap
def background_gradient(s, m=None, M=None, cmap='Blues', low=0, high=0.8):
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
data4.index = data4.index.astype(str)
tableData=data4.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format(precision=2)
#%%display
st.subheader("Monthly %s for Selected Water Year(s)" %params_select)
st.markdown("""
Provides the monthly accumulated precipitation by month for the selected water year(s):  
            """)
            
st.markdown("Selected Water Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(tableData)
st.markdown("""
Table Notes:
- Months with fewer than 25 results are not shown.
- The user-defined precipitation threshold does not change this table.
            """)

#%% download table data
csv = convert_df(data4)

st.download_button(
     label="Download Monthly %s Data (as CSV)"%params_select,
     data=csv,
     file_name='Monthly_Data_%s_%s.csv'%(params_select,site_select),
     mime='text/csv',
 )

#%%
st.subheader("Monthly Summary Statistics for Selected Water Year(s)")
sumStats1=sumStats.style\
    .format('{:,.2f}',subset=(['Median'],slice(None)))\
    .format('{:,.3f}',subset=(['Trend'],slice(None)))\
    .set_properties(**{'width':'10000px'})\

st.markdown(
    """
Provides the monthly median and monthly trend for accumulated precipitation for the selected water year(s):
- Monthly median value, or midpoint, for the selected water years for accumulated precipitation (inches)
- Trend using the Theil-Sen Slope analysis  where Mann-Kendall trend test is significant for monthly accumulated precipitation (inches per year)
    - A negative trend indicates less accumulated precipitation in a given month and a positive trend indicates more accumulated precipitation in a given month    
    """)

st.markdown("Selected Water Year(s): %s through %s"%(tableStartDate, tableEndDate))   
sumStats1
st.markdown(
    """
Table Notes:
- If no trend, then result is presented as "None".
- The user-defined precipitation threshold does not change this table.
    """
    )

#%% download Summary table data
csv = convert_df(sumStats)

st.download_button(
     label="Download Summary Table Data as CSV",
     data=csv,
     file_name='Sum_Stats_Data_%s_%s.csv'%(params_select,site_select),
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
data5.dropna(axis=1, how='all',inplace=True)
data5.columns=monthNames
data5=data5[["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]]

#%%colormap
data5.index = data5.index.astype(str)
countTableData=data5.style\
    .format(precision=2)\
    .set_properties(**{'width':'10000px'})\
    .format(precision=0)\
    .apply(background_gradient, axis=None)

#%%display
pandas.set_option('display.width',100)
st.subheader("Count of %s Days Between %s and %s Inches"%(params_select,thresholdLow,thresholdHigh))
st.markdown(
"""For the selected site and selected water year(s), 
displays the number of days in each month within the user-defined upper and lower accumulated precipitation thresholds:   
""")

st.markdown("Selected Water Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(countTableData)
st.markdown("""
Table Note:
- The count includes days that are equal to the value of each threshold.
            """)

#%% download count data
csv = convert_df(data5)

st.download_button(
     label="Download Count Data as CSV",
     data=csv,
     file_name='Count_Data.csv',
     mime='text/csv',
 )
#%% Stations display information
st.subheader("Weather Station Locations")
image=Image.open("Maps/2_Weather_Stations.png")
st.image(image, width=500)