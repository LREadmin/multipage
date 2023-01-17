# -*- coding: utf-8 -*-
"""
@author: msparacino
"""
#%% Import Libraries
import pandas #for dataframe

import numpy #for math

import matplotlib.pyplot as plt #for plotting

from matplotlib import colors #for additional colors

import streamlit as st #for displaying on web app

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

from PIL import Image

#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

st.set_page_config(page_title="SNOTEL Site Comparison Data Assessment", page_icon="📈")

st.header("SNOTEL Site Comparison Data Assessment")

#%% Read in raw data
data_raw=pandas.read_csv('SNOTEL_data_raw.csv.gz')

# get raw end date
end_dateRaw = arrow.now().format('YYYY-MM-DD')

#%% read site data
sites_df=pandas.read_csv('SNOTEL_sites.csv.gz') #needed for code info

#needed for site/system info
with open("siteNamesListNS.txt") as f:
    siteNamesList=f.read().split(", ")
siteNamesList = [s.replace("[", "") for s in siteNamesList]
siteNamesList = [s.replace("]", "") for s in siteNamesList]
siteNamesList = [s.replace("'", "") for s in siteNamesList]
siteNames=pandas.DataFrame([sub.split(",") for sub in siteNamesList])
siteNames.columns=['Site','System']

siteKey=sites_df[['index','name']]
siteKey.columns=['code','Site']

#%% merged df
combo_data=pandas.merge(data_raw,siteKey,on="Site",how='inner')
combo_data1=pandas.merge(combo_data,siteNames,on="Site",how='inner')
combo_data2=combo_data1
combo_data2=combo_data2.set_index('Site')

#get WY
combo_data2['Date']=pandas.to_datetime(combo_data2['Date'])
combo_data2['CalDay']=combo_data2['Date'].dt.dayofyear
combo_data2['CY']=pandas.DatetimeIndex(combo_data2['Date']).year
combo_data2['Month']=combo_data2['Date'].dt.month
combo_data2['MonthDay']=combo_data2['Date'].dt.day
combo_data2['WY']=numpy.where(combo_data2['Month']>=10,combo_data2['CY']+1,combo_data2['CY'])

#check for full WY and keep if current WY
fullWYcheck=combo_data2.groupby([combo_data2.index,combo_data2['WY']]).count().reset_index()
fullWYcheck.drop(fullWYcheck [ (fullWYcheck['Date'] <365) & (fullWYcheck['WY'] < int(end_dateRaw[:4])) ].index,inplace=True)
fullWYcheck=fullWYcheck.set_index('Site')


#%% filter for parameter
#get parameter list
paramsDF=pandas.DataFrame(['Peak SWE (in)','Peak SWE Day','First Zero SWE Day','Melt Day Count'])
paramsDF['long']=['Peak SWE (in)','Peak SWE Day','First Zero SWE Day','Melt Day Count']
paramsDF['title']=["Peak SWE",
                   "Peak SWE Day",
                   "First Zero SWE Day",
                   "Melt Day Count"]
paramsDF['format']=["{:.1f}","{:.0f}","{:.0f}","{:.0f}"]
paramsSelect=paramsDF['long']

params_select = st.sidebar.selectbox('Select One Summary Statistic:', paramsSelect)
param=paramsDF.loc[paramsDF['long']==params_select][0]
title=paramsDF['title'][paramsDF['long']==params_select]
format_Dec=paramsDF['format'][paramsDF['long']==params_select]



#%%System Selection
system=combo_data2['System'].drop_duplicates()

container=st.sidebar.container()
all=st.sidebar.checkbox("Select Both Systems")

if all:
    system_select = container.multiselect('Select Collection System(s):', system, system)
    
else: 
    system_select = container.multiselect('Select Collection System(s):', system, default=system.iloc[0])
    
def systemfilter():
    return combo_data2[combo_data2['System'].isin(system_select)]

system_data=systemfilter()

#%% multi site selection
tempSD=system_data.reset_index()
sites=tempSD['Site'].drop_duplicates()

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select = container.multiselect('Select One or More Sites:', sites, sites)

else:
    multi_site_select = container.multiselect('Select One or More Sites:', sites,default=sites.iloc[0])

def multisitefilter():
    return system_data[system_data.index.isin(multi_site_select)]
    
system_site_data=multisitefilter()

#%%start and end dates needed for initial data fetch
startY=system_site_data['WY'].min()
endY=system_site_data['WY'].max()
startM=10
startD=1

# with st.sidebar: 
st.sidebar.header("Define Select WY Range")
    
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=endY,value=startY)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY, max_value=endY,value=endY)

def startDate():
    return "%s-%s-0%s"%(int(startYear-1),10,1)

start_date=startDate()

def endDate():
    return "%s-0%s-%s"%(int(endYear),9,30)

end_date=endDate()

#change dates to similar for comparison
start_date1=pandas.to_datetime(start_date,utc=True) 
end_date1=pandas.to_datetime(end_date,utc=True) 

final_data=system_site_data[(system_site_data['Date']>start_date1)&(system_site_data['Date']<=end_date1)]


#%% get POR start, end, stat and trend
manKPOR=[]
median=[]
por_record=[]
siteSelect=final_data.index.drop_duplicates()

for row in siteSelect:
    temp=combo_data2[combo_data2.index==row] #full dataset
    tempfullWYcheck=fullWYcheck[fullWYcheck.index==row]
    temp=temp[temp['WY'].isin(tempfullWYcheck['WY'])]

    # get POR start and end
    por_start=str(temp['Date'].min())
    por_end=str(temp['Date'].max())
    por_record.append([row,por_start,por_end])
    
    # get median of parameter
    #median annual SWE Peak
    tempMedian=temp[['WY','SWE_in']]
    
    
    #peak SWE
    tempSiteWYPeak=tempMedian.groupby(tempMedian['WY']).max()
    tempSiteWYPeak['PeakSWEDay']=numpy.nan
    tempSiteWYPeak['FirstZeroSWEDay']=numpy.nan
    tempSiteWYPeak['MeltDays']=numpy.nan
    for i in range(tempMedian.WY.min(),tempMedian.WY.max()+1):
         #peak SWE day
         tempWY=temp[temp.WY==i]
         tempSiteWYPeak.PeakSWEDay.loc[i]=tempWY.loc[tempWY['SWE_in']==tempSiteWYPeak.loc[i][0]].CalDay[0]
         tempZeroDay=tempWY[(tempWY['SWE_in']==0)&(tempWY['CalDay']>tempSiteWYPeak.loc[i][0])].sort_values(by=['CalDay'])
         tempSiteWYPeak.FirstZeroSWEDay.loc[i]=tempZeroDay.iloc[0].CalDay
         tempSiteWYPeak.MeltDays.loc[i]=tempSiteWYPeak.FirstZeroSWEDay.loc[i]-tempSiteWYPeak.PeakSWEDay.loc[i]

    cols={'Peak SWE (in)':'SWE_in','Peak SWE Day':'PeakSWEDay','First Zero SWE Day':'FirstZeroSWEDay',
          'Melt Day Count':'MeltDays'}

    temp_median=tempSiteWYPeak[cols[params_select]].median()
    median.append([row,temp_median])
             
    temp1=tempSiteWYPeak.reset_index()
    #Man Kendall Test
    tempPOR=temp1[['WY',cols[params_select]]]
    tempPORMKMedian=tempPOR.groupby(tempPOR['WY']).median()
    tempPORManK=mk.original_test(tempPORMKMedian)
    if tempPORManK[2]>0.1:
        manKPOR.append([row,float('nan')])
    else:
        manKPOR.append([row,tempPORManK[7]])       #slope value 
        
medianPOR=pandas.DataFrame(median)
medianPOR.columns=(['Site','MedianPOR'])
medianPOR=medianPOR.set_index('Site')

por_record=pandas.DataFrame(por_record)
por_record=por_record.set_index([0])
por_record.columns=(['por_start','por_end'])

manKPOR=pandas.DataFrame(manKPOR)
manKPOR.columns=(['Site','ManKPOR'])
manKPOR=manKPOR.set_index('Site')

#%%for selected period get WY Stat
summary=pandas.DataFrame()
siteSelect=final_data.index.drop_duplicates()

tempManK=[]
manK=[]
median=[]
for row in siteSelect:
    temp=final_data[final_data.index==row]
    tempMedian=temp[['WY','SWE_in']]
    
    #peak SWE
    tempSiteWYPeak=tempMedian.groupby(tempMedian['WY']).max()
    tempSiteWYPeak['PeakSWEDay']=numpy.nan
    tempSiteWYPeak['FirstZeroSWEDay']=numpy.nan
    tempSiteWYPeak['MeltDays']=numpy.nan
    
    for i in range(temp.WY.min(),temp.WY.max()+1):
         #peak SWE day
         tempWY=temp[temp.WY==i]
         tempSiteWYPeak.PeakSWEDay.loc[i]=tempWY.loc[tempWY['SWE_in']==tempSiteWYPeak.loc[i][0]].CalDay[0]
         tempZeroDay=tempWY[(tempWY['SWE_in']==0)&(tempWY['CalDay']>tempSiteWYPeak.loc[i][0])].sort_values(by=['CalDay'])
         tempSiteWYPeak.FirstZeroSWEDay.loc[i]=tempZeroDay.iloc[0].CalDay
         tempSiteWYPeak.MeltDays.loc[i]=tempSiteWYPeak.FirstZeroSWEDay.loc[i]-tempSiteWYPeak.PeakSWEDay.loc[i]

    cols={'Peak SWE (in)':'SWE_in','Peak SWE Day':'PeakSWEDay','First Zero SWE Day':'FirstZeroSWEDay',
          'Melt Day Count':'MeltDays'}

    temp_median=tempSiteWYPeak[cols[params_select]].median()
    median.append(temp_median)
             
    temp_1=tempSiteWYPeak.reset_index()
    #Man Kendall Test
    tempMK=temp_1[['WY',cols[params_select]]]
    tempMKMedian=tempPOR.groupby(tempPOR['WY']).median()
    tempManK=mk.original_test(tempPORMKMedian)
   
    if tempManK[2]>0.1:
        manK.append(float('nan'))
    else:
        manK.append(tempManK[7])  
    
    temp1=temp['System']
    temp1=temp1.drop_duplicates()
    summary=pandas.concat([summary,temp1],ignore_index=True)

summary=summary.set_index(siteSelect)

  
median=pandas.DataFrame(median)
median=median.set_index(siteSelect)
median.columns=(['Select WY Stat'])
median=median[median.index.isin(siteSelect)]

manK=pandas.DataFrame(manK)
manK=manK.set_index(siteSelect)
manK.columns=(['Select WY Trend'])
manK=manK[manK.index.isin(siteSelect)]

#%%combine POR with Selected stats
por_record=por_record[por_record.index.isin(siteSelect)]
manKPOR=manKPOR[manKPOR.index.isin(siteSelect)]
medianPOR=medianPOR[medianPOR.index.isin(siteSelect)]

summary=pandas.concat([summary,por_record,manKPOR,medianPOR,manK,median],axis=1)
summary=summary[[0,'por_start','por_end','MedianPOR','ManKPOR','Select WY Stat','Select WY Trend']]

summary.columns=['System','POR Start','POR End','POR Median of %s'%params_select,'POR Trend for %s'%params_select,'Select WY Median of %s'%params_select,'Select WY Trend for %s'%params_select]
summary["POR Start"] = pandas.to_datetime(summary["POR Start"]).dt.strftime('%Y-%m-%d')
summary["POR End"] = pandas.to_datetime(summary["POR End"]).dt.strftime('%Y-%m-%d')

summary1=summary.style\
.format({'POR Median of %s'%params_select:"{:.1f}",'POR Trend for %s'%params_select:"{:.2f}"
          ,'Select WY Median of %s'%params_select:"{:.1f}",'Select WY Trend for %s'%params_select:"{:.2f}"})

#%% full comparison
final_data['CalDay']=final_data['Date'].dt.dayofyear
final_data['CY']=pandas.DatetimeIndex(final_data['Date']).year
final_data['WY']=numpy.where(final_data['CalDay']>=274,final_data['CY']+1,final_data['CY'])

compData=final_data[['SWE_in','CalDay','WY']]
selectWY=compData['WY'].drop_duplicates()
selectSite=compData.index.drop_duplicates()

compList=[]
for WYrow in selectWY:
    tempWYdata=compData[compData['WY']==WYrow]
    for siterow in selectSite:
        try:
            tempSiteData=tempWYdata[tempWYdata.index==siterow]
            tempfullWYcheck=fullWYcheck[fullWYcheck.index==siterow]
            tempSiteData=tempSiteData[tempSiteData['WY'].isin(tempfullWYcheck['WY'])]    
            
            #peak SWE
            tempSiteWYPeak=tempSiteData['SWE_in'].max()
                     
            #POR Median Peak SWE
            tempPORmed=median[median.index==siterow]
            tempMedNorm=tempPORmed.iloc[0][0]
            
            #peak SWE day
            tempSiteWYPeakDay=tempSiteData.loc[tempSiteData['SWE_in']==tempSiteWYPeak].iloc[-1][1]
            
            # #first Zero SWE day
            tempZeroAll=tempSiteData[(tempSiteData['SWE_in']==0)&(tempSiteData['CalDay']>tempSiteWYPeakDay)]
            tempZeroAll=tempZeroAll.sort_values(by=['CalDay'])
            tempZeroDay=tempZeroAll['CalDay'].iloc[0]
            
            #melt day count
            compList.append([siterow,WYrow,tempSiteWYPeak,tempMedNorm,tempSiteWYPeakDay,tempZeroDay, tempZeroDay-tempSiteWYPeakDay])
        except:
            compList.append([siterow,WYrow,None,None,None,None,None])
compListDF=pandas.DataFrame(compList)
compListDF.columns=['Site','WY','Peak SWE (in)','NormMed','Peak SWE Day','First Zero SWE Day','Melt Day Count']
# compListDF['Melt Day Count']=compListDF['First Zero SWE Day']-compListDF['Peak SWE Day']


#%%transpose to get days as columns and prent % peak of median
list=compListDF['WY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    #n=1979
    temp1=compListDF[compListDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.loc[:,[param.iloc[0]]].copy()
    temp2['Med']=numpy.nan
    temp2['NormMed']=numpy.nan
    temp2.Med=temp1.loc[:,['NormMed']].copy()
    temp2['NormMed']=temp2[param.iloc[0]]/temp2.Med
    temp2=temp2[['NormMed']]
    temp2.columns=[n]
    yearList[n]=temp2

#%%colormap
def background_gradient(s, m=None, M=None, cmap='Blues',low=0, high=0.8):
    #print(s.shape)
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

yearList = yearList.reindex(sorted(yearList.columns,reverse=True), axis=1)

yearList.insert(0,'System',summary["System"])

select_col=yearList.columns[1:]
yearList1=yearList.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None,subset=select_col)\
    .format("{:,.0%}",subset=select_col)
   
#%%transpose to get days as columns and present actual SWE value
yearListPeak=pandas.DataFrame(index=finalSites)
for n in list:
    #n=1979
    temp1=compListDF[compListDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.loc[:,[param.iloc[0]]].copy()
    temp2.columns=[n]
    yearListPeak[n]=temp2

#%%colormap
def background_gradient(s, m=None, M=None, cmap='Blues',low=0, high=0.8):
    #print(s.shape)
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

yearListPeak = yearListPeak.reindex(sorted(yearListPeak.columns,reverse=True), axis=1)

yearListPeak.insert(0,'System',summary["System"])

yearListPeak1=yearListPeak.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None,subset=select_col)\
    .format(paramsDF[paramsDF.long==param.iloc[0]].format.iloc[0],subset=select_col)


#%%Page Display
#Annual table
st.subheader("Annual %s for Selected Site(s) and Water Year(s)"%params_select)
st.markdown(
    """
Annual selected summary statistic results (Peak SWE, Peak SWE Day, First Zero SWE Day, or Melt Day Count) for each selected site by water year: 

- **Peak SWE:** The highest daily SWE (in inches) for each water year 
- **Peak SWE Day:** The day(s) of peak SWE (in inches) occurrence prior to snowmelt and SWE decline. Presented in calendar day where January 1 = Day 1. Calendar day 100 = April 10 or April 9 in a leap year. Calendar day 150 = May 30 or May 29 in a leap year. 
- **First Zero SWE Day:** The first day SWE equals zero and the snowpack has melted (Calendar Day) 
- **Melt Day Count:** Number of days between the Peak SWE Day and First Zero SWE Day (Days) 
"""
    )
yearListPeak1

#%% download SNOTEL comparison data
csv = convert_df(yearListPeak)

st.download_button(
     label="Download Annual Statistic Table (as CSV)",
     data=csv,
     file_name='SNOTEL_Annual_Stats.csv',
     mime='text/csv',
 )

#%%Summary statistics
st.subheader("Summary %s Table for Selected Site(s) and Water Year(s)"%params_select) 
st.markdown(
    """
For the selected summary statistic (Peak SWE, Peak SWE Day, First Zero SWE Day, or Melt Day Count), provides period of record dates and both period of record and water year median statistics and trends for each selected site. 
- **POR Start:** Earliest date of available data for the site 
- **POR End:** Latest date of available data for site 
- **POR Median:** Median of the selected summary tatistic (Peak SWE, Peak SWE Day, First Zero SWE Day, or Melt Day Count) for the entire period of record, regardless of selected water year(s) 
- **POR Trend:** Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for entire period of record of the selected summary statistic: 
    - **Peak SWE:** (increasing or decreasing inches per year) 
    - **Peak SWE Day:** (earlier or later calendar day per year) 
    - **First Zero SWE Day:** (earlier or later calendar day per year) 
    - **Melt Day Count:** (increasing or decreasing days per year) 
- **Selected WY Median:** Median of the selected summary statistic (Peak SWE, Peak SWE Day, First Zero SWE Day, or Melt Day Count) for the selected water year(s) 
- **Selected WY Trend:** Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for the selected water years of the selected summary statistic. If no trend, then result is “nan.” 
"""
)
st.markdown("Selected Water Year(s): %s through %s"%(start_date, end_date))    
summary1
st.markdown(
    """
Table Note:
- If no trend, then result is presented as “nan.” 
    """)

#%% download SNOTEL comparison Summary data

csv = convert_df(summary)

st.download_button(
     label="Download Summary Statistic/Trend Table (as CSV)",
     data=csv,
     file_name='SNOTEL_Summary_Statistic_Trend.csv',
     mime='text/csv',
 )

#%%Percent of Median Summary Statistis
st.subheader("Annual Percent of Median %s for Selected Site(s) and Water Year(s)"%params_select)
st.markdown(
    """
Annual selected summary statistic percent of median results for each selected Site by WY. A 100% result for a given WY indicates that the value is exactly the median of the Selected WY summary statistic result.  A 50% result indicates that WY result is half of the selected WY median. 
- **Peak SWE:** (% of median, where less then 100% indicates a lower SWE in inches) 
- **Peak SWE Day:** (% of median, where less then 100% indicates an earlier Peak SWE day in calendar days) 
- **First Zero SWE Day:** (% of median, where less then 100% indicates an earlier First Zero SWE day in calendar days) 
- **Melt Day Count:** (% of median, where less then 100% indicates fewer days between the Peak SWE Day and First Zero SWE Day) 
"""
)
st.markdown("Selected Water Year(s): %s through %s"%(start_date, end_date))    
yearList1

#%% download SNOTEL comparison data

csv = convert_df(yearList)

st.download_button(
     label="Download Annual Percent of Median Statistic Table (as CSV)",
     data=csv,
     file_name='SNOTEL_comp.csv',
     mime='text/csv',
 )


#%% Stations display information
st.subheader("SNOTEL Locations ")
image=Image.open("Maps/1_Snotel.png")
st.image(image, width=500)

