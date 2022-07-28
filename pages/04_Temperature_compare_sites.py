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
data=data_raw[['site','date','Month','maxt','mint','meant']]
data['date']=pandas.to_datetime(data['date'])
data['CY']=data['date'].dt.year

#%%select months

monthOptions=pandas.DataFrame({'Month':['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                               'Season':['Winter','Winter','Winter','Spring','Spring','Spring','Summer','Summer','Summer','Fall','Fall','Fall'],
                               'Num':[1,2,3,4,5,6,7,8,9,10,11,12]})
monthSelect=monthOptions['Month']

winterMonths=monthOptions.loc[monthOptions['Season']=='Winter']['Month']
springMonths=monthOptions.loc[monthOptions['Season']=='Spring']['Month']
summerMonths=monthOptions.loc[monthOptions['Season']=='Summer']['Month']
fallMonths=monthOptions.loc[monthOptions['Season']=='Fall']['Month']

container=st.sidebar.container()
winter=st.sidebar.checkbox("Winter")
spring=st.sidebar.checkbox("Spring")
summer=st.sidebar.checkbox("Summer")
fall=st.sidebar.checkbox("Fall")

if winter:
    month_select = container.multiselect('Select month(s):',winterMonths, winterMonths)
    
elif spring:
    month_select = container.multiselect('Select month(s):',springMonths, springMonths)
    
elif summer:
    month_select = container.multiselect('Select month(s):',summerMonths, summerMonths)
        
elif fall:
    month_select = container.multiselect('Select month(s):',fallMonths, fallMonths)
else:
    month_select = container.multiselect('Select month(s):', monthSelect,default=monthSelect)

monthNum_select=pandas.DataFrame(month_select)
monthNum_select=monthOptions.loc[monthOptions['Month'].isin(month_select)]['Num']
    
def monthfilter():
    return data[data['Month'].isin(monthNum_select)]

data=monthfilter()

#%%select stat
#statistic

paramsDF=pandas.DataFrame({0:['maxt','mint','meant'], 'long': ['Max Temp (F)', 'Min Temp (F)', 'Mean Temp (F)']})
paramsSelect=paramsDF['long']

stat_select= st.sidebar.selectbox(
     'Select one statistic:', paramsSelect)

stat_selection=paramsDF.loc[paramsDF['long']==stat_select][0]


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
    dataforMK=dataBySite[[stat_selection.iloc[0],'CY']]
    tempPORMKMedian=dataforMK.groupby(dataforMK['CY']).median()
    tempPORManK=mk.original_test(tempPORMKMedian)
    if tempPORManK[2]>0.1:
        manKPOR.append([site,None])
    else:
        manKPOR.append([site,tempPORManK[7]])       #slope value 

manKPOR=pandas.DataFrame(manKPOR)
manKPOR=manKPOR.set_index([sites])
manKPOR.columns=(['Site','POR Trend'])
    
pordf=pandas.DataFrame(por)
pordf=pordf.set_index([0])
pordf.columns=["POR Start","POR End"]

medstatdf=pandas.DataFrame(medstat)
medstatdf=medstatdf.set_index([sites])
medstatdf.columns=['POR Stat']

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


#%%threshold filter
thresholdHigh = st.sidebar.number_input('Set Upper %s threshold:'%stat_select,step=1)

thresholdLow = st.sidebar.number_input('Set Lower %s threshold:'%stat_select,step=1)

#%%FILTERED DATA
data_sites_years=data_sites[(data_sites['date']>start_date1)&(data_sites['date']<=end_date1)]


#%% calculate params for selected period

manKPORSelect=[]
medstatSelect=[]

siteSelect=data_sites_years['site'].drop_duplicates()

for site in sites:
    dataBySite=data_sites_years[data_sites_years['site']==site]
    
    #get medians
    dataBySiteParam=dataBySite[stat_selection]
    tempstat=dataBySiteParam.median()
    medstatSelect.append(tempstat[0])
    
    #Man Kendall Test
    try:
        dataforMKSelect=dataBySite[[stat_selection.iloc[0],'CY']]
        tempPORMKMedian=dataforMKSelect.groupby(dataforMKSelect['CY']).median()
        tempPORManK=mk.original_test(tempPORMKMedian)
    except:
        pass
    if tempPORManK[2]>0.1:
        manKPORSelect.append(float('nan'))
    else:
        manKPORSelect.append(tempPORManK[7])       #slope value 

manKPORSelect=pandas.DataFrame(manKPORSelect)
manKPORSelect=manKPORSelect.set_index([sites])
manKPORSelect.columns=(['Select CY Trend'])
manKPORSelect=manKPORSelect[manKPORSelect.index.isin(siteSelect)]

medstatSelectdf=pandas.DataFrame(medstatSelect)
medstatSelectdf=medstatSelectdf.set_index([sites])
medstatSelectdf.columns=(['Select CY Stat'])
medstatSelectdf=medstatSelectdf[medstatSelectdf.index.isin(siteSelect)]

sumSites=pandas.concat([sumSites,medstatSelectdf,manKPORSelect],axis=1)      
sumSites=sumSites.drop("Site",axis=1)

sumSites1=sumSites[sumSites.index.isin(multi_site_select)]

sumSitesDisplay=sumSites1.style\
    .format({'POR Stat':"{:.1f}",'POR Trend':"{:.2f}"
              ,'Select CY Stat':"{:.1f}",'Select CY Trend':"{:.2f}"})\
    .set_table_styles([dict(selector="th",props=[('max-width','3000px')])])

st.header("Site Comparison")
st.markdown("Compares SWE Statistic (median, inches) and trend (Theil-Sen Slope (inches/year) if Mann-Kendall trend test is significant; otherwise nan)")
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
sumSitesDisplay

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

#%%Temp CY Median / Temp POR Median

compData=data_sites_years[['site',stat_selection.iloc[0],'CY']]
selectCY=compData['CY'].drop_duplicates()
selectSite=compData['site'].drop_duplicates()

compList=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['CY']==CYrow]
    try:
        for siterow in selectSite:
            tempSiteData=tempCYdata[tempCYdata['site']==siterow]
            tempSiteCYPeak=tempSiteData[stat_selection.iloc[0]].median()
            tempPORmed=sumSites[sumSites.index==siterow]['POR Stat'][0]
            tempMedNorm=tempSiteCYPeak/tempPORmed
            compList.append([siterow,CYrow,tempMedNorm])
    except:
        compList.append([siterow,CYrow,None])
compListDF=pandas.DataFrame(compList)
compListDF.columns=['Site','CY','NormMed']

#%%transpose to get days as columns
#compListDF=pandas.read_csv("temp.csv")

list=compListDF['CY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    #n=1979
    temp1=compListDF[compListDF['CY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[1]].copy()
    temp2.columns=[n]
    yearList[n]=temp2
#yearList=yearList.fillna("NaN")

#%%colormap
def background_gradient(s, m=None, M=None, cmap='bwr',low=0, high=0):
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

#select_col=yearList.columns[:]
yearList1=yearList.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format('{:,.0%}')

    #.background_gradient(cmap='Blues',low=0,high=1.02,axis=None, subset=select_col)\    
st.header("%s CY Median / %s POR Median"%(stat_select,stat_select))
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
yearList1

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(yearList)

st.download_button(
     label="Download Temperature Comparison as CSV",
     data=csv,
     file_name='Temp_comp.csv',
     mime='text/csv',
 )
#%%FOR THRESHOLD
#%%calc statistic for all months
compListCount=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['CY']==CYrow]
    try:
        for siterow in selectSite:
            tempSiteData=tempCYdata[tempCYdata['site']==siterow]
            tempSiteData=tempSiteData.drop(columns=['site','CY'])
            count=tempSiteData[(tempSiteData < thresholdHigh)&(tempSiteData > thresholdLow)].count()[0]
            compListCount.append([siterow,CYrow,count])
    except:
        compListCount.append([siterow,CYrow,None])
        
compListCountDF=pandas.DataFrame(compListCount)
compListCountDF.columns=['Site','CY','Count']

#%%transpose to get Months as columns

countList=pandas.DataFrame(index=finalSites)
for n in list:
    #n=1979
    temp1=compListCountDF[compListCountDF['CY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[1]].copy()
    temp2.columns=[n]
    countList[n]=temp2
countList = countList.reindex(sorted(countList.columns,reverse=True), axis=1)

#%%colormap
def background_gradient(s, m=None, M=None, cmap='OrRd',low=0, high=0):
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

#select_col=yearList.columns[:]
countList1=countList.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\

    #.background_gradient(cmap='Blues',low=0,high=1.02,axis=None, subset=select_col)\    
st.header("Count of days with %s between %s and %s %s"%(stat_select,thresholdLow, thresholdHigh, stat_select))
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
countList1

# download data
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(countList)

st.download_button(
     label="Download Temperature Count Comparison as CSV",
     data=csv,
     file_name='Temp_count_comp.csv',
     mime='text/csv',
 )