# -*- coding: utf-8 -*-
"""
@author: msparacino
"""

#%% Import Libraries
import pandas #for dataframe
import matplotlib.pyplot as plt #for plotting
from matplotlib import colors #for additional colors
import streamlit as st #for displaying on web app
import datetime #for date/time manipulation
import pymannkendall as mk #for trend anlaysis
import numpy as np
from PIL import Image #for map
#%% Website display information
st.set_page_config(page_title="Temperature Individual Sites", page_icon="📈")
st.header("Individual Temperature Site Data Assessment")

#%% Define data download as CSV function
@st.cache_data
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
# params=data_raw.columns
# params=params[params.isin(["maxt","mint","meant"])==True]

# paramsDF=pandas.DataFrame(params)
# paramsDF['long']=['Max Temp (F)', 'Min Temp (F)', 'Mean Temp (F)']
# paramsSelect=paramsDF['long']

# The "long" values are already hardcoded in, so there's no reason not to use
# a dict. It simplifies things a lot, an it speeds things up by a factor of 
# around 5000
params_dict =  {
    'Max Temp (F)': 'maxt',
    'MinTemp(F)': 'mint',
    'Mean Temp (F)': 'meant'}

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

#%% filter first for parameters
params_select = st.sidebar.selectbox('Select One Statistic:', params_dict.keys())
param=params_dict[params_select]
data_param=data_raw
data1=data_param[[param,'Month','site','CY']]

#%% filter second for site
site_select_long = st.sidebar.selectbox('Select One Site:', sites.keys())

site_select=sites[site_select_long]

def sitefilter():
    return data1.loc[data1['site'] == site_select]

data_param_site=sitefilter()

#%% filter third for date
startY=data_param_site['CY'].min()
endY=data_param_site['CY'].max()
startM=1
startD=1

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Calendar Year:', min_value=startY, max_value=endY,value=startY)
endYear = st.sidebar.number_input('Enter Ending Calendar Year:',min_value=startY, max_value=endY,value=endY)

def dateSelection():
    return data_param_site[(data_param_site['CY']>=startYear)&(data_param_site['CY']<=endYear)]

data_param_site_date=dateSelection()

#%%threshold filter
maxDaily=int(np.ceil(data_param_site_date.iloc[:,0].max())) #rounds up to max num in dataset
minDaily=int(np.floor(data_param_site_date.iloc[:,0].min())) #rounds down to max num in dataset

thresholdHigh = st.sidebar.number_input('Set Upper %s Threshold (Inclusive):'%params_select,step=1, min_value=minDaily, value=maxDaily)

thresholdLow = st.sidebar.number_input('Set Lower %s Threshold (Inclusive):'%params_select,step=1, min_value=minDaily, value=minDaily)

#%%calc statistic for all months
yearList=data_param_site_date['CY'].drop_duplicates()
newParamData=[]
newParamData1=[]

for row in yearList:
    tempData=data_param_site_date[data_param_site_date['CY']==row]

    #filter by day count threshold
    dayCountThres=25
    tempData=tempData.groupby('Month').filter(lambda x : x['%s'%param].count().sum()>=dayCountThres)
    
    for row1 in monthList:
        tempData2=tempData[tempData['Month']==row1]
        tempData2=tempData2.drop(columns='site')
        if len(tempData2)==0:
            count=[np.nan, np.nan, np.nan]
            count[0]=np.nan
        else:
            tempData2=tempData2.dropna()
            count=tempData2[(tempData2 <= thresholdHigh)&(tempData2 >= thresholdLow)].count()
        median=tempData2.median()
        
        newParamData.append([row,row1,median[0]])
        newParamData1.append([row,row1,count[0]])
        
paramDataMerge=pandas.DataFrame(newParamData,columns=['CY','Month',params_select])
paramDataMerge1=pandas.DataFrame(newParamData1,columns=['CY','Month',params_select])

selectStartYear=paramDataMerge1['CY'].min()
selectEndYear=paramDataMerge1['CY'].max()

tableStartDate=datetime.datetime(selectStartYear,1,1).strftime("%Y-%m-%d")

tableEndDate=datetime.datetime(selectEndYear,12,31).strftime("%Y-%m-%d")
#%%transpose to get months as columns
years=paramDataMerge['CY'].drop_duplicates()
years=years.sort_values(ascending=False)
yearList=[]
for n in years:
    temp1=paramDataMerge[paramDataMerge['CY']==n]
    temp2=temp1.iloc[:,[1,2]].copy()
    temp2=temp2.sort_values(by="Month")
    temp3=temp2.T
    temp3.columns=temp3.iloc[0]
    temp3=temp3.drop('Month')
    yearList.append(temp3)

data4=pandas.concat(yearList)
years=years.values.tolist()
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
def background_gradient(s, m=None, M=None, cmap='OrRd', low=0, high=0):
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

data4.index = data4.index.astype(str)
tableData=data4.style\
    .format(precision=1)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
#pandas.set_option('display.width',100)
st.subheader("Monthly Median of %s Values by Year" %params_select)
st.markdown(
    """
For the summary statistic, site and selected calendar year(s), the following information is available:
- **Max Temp (F):** The recorded daily maximum temperature 
- **Min Temp (F):** The recorded daily minimum temperature 
- **Mean Temp (F):** Calculated daily mean using the recorded maximum and minimum temperature
    """
    )

st.markdown("Selected Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(tableData)

st.markdown(
    """Table Notes:
- Months with fewer than 25 results are not shown.
- The user-defined temperature threshold does not change this table.  
    """
    )
#%% download table data
csv = convert_df(data4)

st.download_button(
     label="Download Monthly Median of %s Data (as CSV)"%params_select,
     data=csv,
     file_name='Monthly_Median_Data_%s_%s.csv'%(params_select,site_select),
     mime='text/csv',
 )

sumStats1=sumStats.style\
    .format('{:,.1f}',subset=(['Median'],slice(None)))\
    .format('{:,.2f}',subset=(['Trend'],slice(None)))\
    .set_properties(**{'width':'10000px'})

st.subheader("Monthly %s for Selected Calendar Year(s)"%params_select)
st.markdown(
"""
Provides the monthly median and monthly trend for %s for the selected water year(s):

- Monthly median value, or midpoint, for the selected water years for %s
- Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for monthly %s (degrees Fahrenheit per year)
    - A negative trend indicates decreasing %s in a given month and a positive trend indicates increasing %s in in a given month
"""%(params_select, params_select, params_select, params_select, params_select)
)
st.markdown("Selected Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))   
sumStats1
st.markdown("""Table Notes:
- If no trend, then result is presented as "None".
- The user-defined temperature threshold does not change this table.
"""
)
#%% download Summary table data
csv = convert_df(sumStats)

st.download_button(
     label="Download Monthly %s Table (as CSV)"%params_select,
     data=csv,
     file_name='Sum_Stats_Data_%s_%s.csv'%(params_select,site_select),
     mime='text/csv',
 )

#%%FOR THRESHOLD
#%%transpose to get Months as columns
yearList=[]
for n in years:
    temp1=paramDataMerge1[paramDataMerge1['CY']==n]
    temp2=temp1.iloc[:,[1,2]].copy()
    temp2=temp2.sort_values(by="Month")
    temp3=temp2.T
    temp3.columns=temp3.iloc[0]
    temp3=temp3.drop('Month')
    yearList.append(temp3)

data5=pandas.concat(yearList)
# years=med_list.values.tolist()
data5['Years']=years
data5=data5.set_index('Years')
data5.index = data5.index.astype(str)
data5.columns=monthNames
   
countTableData=data5.style\
    .format(precision=0)\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)

#%%display
pandas.set_option('display.width',100)
st.subheader("Count of %s Days Within %s\N{DEGREE SIGN}F and %s\N{DEGREE SIGN}F"%(params_select,thresholdLow,thresholdHigh))
st.markdown(
"""For the selected site, %s, and selected calendar year(s), 
displays the number of days in each month within the user-defined upper and lower thresholds.    
"""%params_select)

st.markdown("Selected Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(countTableData)
st.markdown("""
Table Note:
- The count includes days that are equal to the value of each threshold.
            """)

#%% download count data
csv = convert_df(data5)

st.download_button(
     label="Download %s Count Data (as CSV)"%params_select,
     data=csv,
     file_name='Count_Data.csv',
     mime='text/csv',
 )
#%% Stations display information
st.subheader("Weather Station Locations ")
image=Image.open("Maps/2_Weather_Stations.png")
st.image(image, width=500)
