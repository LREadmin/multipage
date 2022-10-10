# -*- coding: utf-8 -*-
"""
@author: msparacino
"""
#%% Import Libraries
import pandas #for dataframe

import numpy #for math

import matplotlib.pyplot as plt #for plotting

import streamlit as st #for displaying on web app

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

#%% Website display information
st.set_page_config(page_title="SNOTEL Individual Sites", page_icon="📈")
#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

#%% Select year type
yearType="WY" #CY = calendar year, WY = water year

#%% Read in raw data and isolate site names
data_raw=pandas.read_csv('SNOTEL_data_raw.csv.gz')

#convert date to datetime
pandas.to_datetime(data_raw['Date'])

# get site list
with open("siteNamesList.txt") as f:
    siteNamesList=f.read().split(", ")

# clean up data to isolate site names
siteNamesList = [s.replace("[", "") for s in siteNamesList]
siteNamesList = [s.replace("]", "") for s in siteNamesList]
siteNamesList = [s.replace("'", "") for s in siteNamesList]
siteNames=pandas.DataFrame(siteNamesList)

#%% Definte start and end dates
startY=1950
startM=10
startD=1
start_date = "%s-%s-0%s"%(startY,startM,startD) #if start day is single digit, add leading 0
end_dateRaw = arrow.now().format('YYYY-MM-DD')

#%% Define and use Site Filter

site_selected = st.sidebar.selectbox('Select your site:', siteNames)

def filterdata():
    return data_raw.loc[data_raw['Site']==site_selected]

data=filterdata()

# rearrange columns
cols=data.columns.tolist()
cols=cols[-1:] + cols[:-1]
data=data[cols]
data1=data
data1=data1.set_index('Site')
data1['Date']=data1['Date'].str[:-15]

# sort with current year at top
data1=data1.sort_values(by="Date", ascending=False)

# toggle check box to display data table
if st.checkbox('show SNOTEL data for full POR'):    
    st.dataframe(data1)
    
#%% download snotel data  as CSV
csv = convert_df(data1)

st.download_button(
     label="Download POR SNOTEL data as CSV",
     data=csv,
     file_name='%s_data.csv'%site_selected,
     mime='text/csv',
 )

#%% date filter

#dates for st slider need to be in datetime format:
min_date = datetime.datetime(startY,startM,startD)
max_date = datetime.datetime.today() #today

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=startY, max_value=int(end_dateRaw[:4]))
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=startY+1, max_value=int(end_dateRaw[:4]),value=2022)

# startYear=2013
# endYear=2013

def startDate():
    return "%s-%s-0%s"%(int(startYear-1),10,1)

start_date=startDate()

def endDate():
    return "%s-0%s-%s"%(int(endYear),9,30)

end_date=endDate()

st.header("Date range: %s through %s"%(start_date, end_date))

#change dates to similar for comparison
start_date=pandas.to_datetime(start_date,utc=True) 
end_date=pandas.to_datetime(end_date,utc=True) 
data['Date'] = pandas.to_datetime(data['Date'])

data=data[(data['Date']>=start_date)&(data['Date']<=end_date)]

#%% redefine years as needed for remaining analyses
start=start_date
end=end_date
startYear=start_date.year
endYear=end_date.year

#%%date time manipulation
data['Date']=pandas.to_datetime(data['Date'])
data['CY']=pandas.DatetimeIndex(data['Date']).year
data['CalDay']=data['Date'].dt.dayofyear
data['Month']=data['Date'].dt.month
data['MonthDay']=data['Date'].dt.day

#drop date
data2=data.iloc[:,[2,3,4]].copy()

#%%add WY col
##In leap years, December 31 is the 366th day. Therefore, WY 2021 (for example) 
##  will show up on the raster hydrograph with 366 days because it includes days from a leap year (2020). 
data2['WY']=numpy.where(data2['CalDay']>=274,data2['CY']+1,data2['CY'])

#check for full WY and keep if current WY
fullWYcheck=data2.groupby(data2['WY']).count()
fullWYcheck.drop(fullWYcheck [ (fullWYcheck['SWE_in'] <365) & (fullWYcheck.index < int(end_dateRaw[:4])) ].index,inplace=True)

#%%drop incomplete WYs
data2= data2 [data2['WY'].isin(fullWYcheck.index)]

#create year list
years=[]
years.extend(range(startYear+1,endYear+1))

#%%create day list for cal year or water year
daysCY=[]
daysCY.extend(range(1,367))

daysWY=[]
daysWY.extend(range(274,367))
daysWY.extend(range(1,274))

if yearType=="WY":
    dataDay=daysWY
else:
    dataDay=daysCY

#%%transpose to get days as columns
list=years
yearList=[]
for n in list:
    if yearType=="WY":
        temp=data2.loc[data2['WY']==n]
    else:
        temp=data2.loc[data2['CY']==n]
    temp2=temp.iloc[:,[0,2]].copy()
    temp2=temp2.sort_values(by="CalDay")
    temp3=temp2.T
    temp3.columns=temp3.iloc[1]
    temp3=temp3.drop('CalDay')
    yearList.append(temp3)

data4=pandas.concat(yearList)
data4['Years']=years
data4=data4.set_index('Years')

data4=data4.reindex(columns=dataDay)
data4.drop(data4.columns[274:],axis=1,inplace=True)

#%% Peak SWE days
data2['PeakSWE']=data2.groupby('WY')['SWE_in'].transform('max')
data2['PeakCalDay']=data2['SWE_in']==data2['PeakSWE']
PeakSWE=data2.loc[data2['PeakCalDay']==True]
PeakSWE = PeakSWE.drop_duplicates('WY',keep='last')

#%% snow free days
list=range(startYear,endYear+1)
yearList2=[]
for i in range(len(PeakSWE)):
    tempDay=PeakSWE.iloc[i][2]
    tempWY=PeakSWE.iloc[i][3]
    tempZeroSWE=data2[(data2['WY']==tempWY)&(data2['SWE_in']==0)&(data2['CalDay']>tempDay)]
    yearList2.append(tempZeroSWE)
zeroSWE=pandas.concat(yearList2)
zeroSWE=zeroSWE.sort_values(by=['CalDay','WY'])
zeroSWE=zeroSWE.drop_duplicates('WY',keep='first')

#%% summary table
summary=PeakSWE[['PeakSWE','WY','CalDay']].copy()
merge=summary.merge(zeroSWE,how='inner',on='WY')
merge=merge.drop(['SWE_in','PeakCalDay','PeakSWE_y','CY'],axis=1)
merge.rename({'PeakSWE_x': 'Peak SWE (in)', 'WY': 'WY', 'CalDay_x':'Peak SWE Day','CalDay_y': 'First Zero SWE Day'}, axis=1, inplace=True)
merge['Melt Day Count']=merge['First Zero SWE Day']-merge['Peak SWE Day']


#%%Mann kendall
merge=merge.set_index('WY')
params=merge.columns
median=pandas.DataFrame(merge.median()).T

if len(merge)==1:
    merge1=median
    merge1=merge1.rename(index={0: 'Median'})
else:
    trendraw=[]
    ManKraw=[]
    for row in params:
        try:
            tempManK=mk.original_test(merge[row])
            ManKraw.append(tempManK)
            if tempManK[2]>0.1:
                trendraw.append(float('nan'))
            else:
                trendraw.append(tempManK[7])  
        except:
            ManKraw.append(float('nan'))
            trendraw.append(float('nan'))
    ManK=pandas.DataFrame(ManKraw)
    trend=pandas.DataFrame(trendraw)
    ManK['params']=params
    ManK['slope1']=trend
    
    ManK=ManK[['trend','slope1','params']].T
    ManK.columns=ManK.iloc[2]
    ManK=ManK.drop(['params','trend'])
    
    merge1=pandas.concat([median, ManK],ignore_index=True)
    merge1=merge1.rename(index={0: 'Median',1:'Trend'})

#%%accumulated SWE to array
array=data4.to_numpy()
array2=array[::-1]

#%%peak SWE array
data5=pandas.DataFrame(numpy.where(data4.T == data4.T.max(),data4.T.max(),0),index=data4.columns).T

array3=data5.to_numpy()

array4=numpy.ma.masked_where(array3 ==0,array3)
array5=array4[::-1]

#%% plot array
years.reverse()
fig, ax1=plt.subplots(figsize=(8,10.5),constrained_layout=True)
base=ax1.imshow(array2, aspect = 'auto',interpolation='none',cmap="Blues")
peak=ax1.imshow(array5, aspect = 'auto',interpolation='none',cmap="Reds")

ax2=ax1.twiny()

ax1.set_yticks(numpy.arange(0,len(years),step=1))
ax1.set_yticklabels(years,fontsize=11)

if yearType=="WY":
    ax1.set_xticks([-1,31,61,92,123,151,182,212,243,274])#,304,335,365])
    ax2.set_xticks([0,31,61,92,123,151,182,212,243,273])#,304,335,365])
    ax1.set_ylabel("Water Year")
    ax1.set_xlabel("Day of Water Year")
else:
    ax1.set_xticks([0,31,59,90,120,151,181,212,243,273,304,334,365])
    ax2.set_xticks([0,31,59,90,120,151,181,212,243,273,304,334,365])
    ax1.set_ylabel("Cal. Year")
    ax1.set_xlabel("Day of Cal. Year")

ax2.set_xlim(ax2.get_xlim())

if yearType=="WY":
    ax2.set_xticklabels(["Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul"])#,"Aug","Sep"])
    ax1.set_xticklabels(["273","304","334","0","31","59","90","120","151","181"])#,"212","243"])
else:
    ax2.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    ax1.set_xticklabels(["0","31","59","90","120","151","181","212","243","273","304","334"])

plotTitle=site_selected
plt.title(plotTitle)
plt.xticks(rotation=90)

#add color bar to blues
cbaxes=fig.add_axes([1.02,0.1,0.03,0.3])
cbar=fig.colorbar(base,cax=cbaxes, shrink=.25)
cbar.set_label("SWE (inches)")

#add colar bar to reds
cb2axes=fig.add_axes([1.02,0.5,0.03,0.3])
cbar1=fig.colorbar(peak,cax=cb2axes,shrink=.25)
cbar1.set_label("Peak SWE (inches)")
st.pyplot(plt)

#%% display summary stats tables

st.header("Summary Statistic Table")
sumDisplay=merge1.style\
    .format({"Peak SWE (in)":"{:.1f}","Peak SWE Day":"{:.1f}","First Zero SWE Day":"{:.1f}","Melt Day Count":"{:.1f}"})\
    .set_properties(**{'width':'10000px'})

st.markdown("Trend (Theil-Sen Slope (inches/year or days/year) if Mann-Kendall trend test is significant (p-value <0.1); otherwise nan)")
sumDisplay

#%% download sum stats data
csv = convert_df(merge1)

st.download_button(
     label="Download summary stats CSV",
     data=csv,
     file_name='%s_sum_stats.csv'%site_selected,
     mime='text/csv',
 )

#%% display yearly data table
merge=merge.sort_values(by="WY", ascending=False)
merge2=merge.style\
    .format({"Peak SWE (in)":"{:.1f}","Peak SWE Day":"{:.0f}","First Zero SWE Day":"{:.0f}","Melt Day Count":"{:.0f}"})\
    .set_properties(**{'width':'10000px'})

st.header("Yearly Data Table")
merge2

#%% download yearly data table
csv = convert_df(merge)

st.download_button(
     label="Download yearly data as CSV",
     data=csv,
     file_name='%s_yearly_data.csv'%site_selected,
     mime='text/csv',
 )
