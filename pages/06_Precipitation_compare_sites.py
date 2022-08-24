# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 05:31:28 2022
@author: msparacino
@editor: mpedrazas
"""

#%% Import Libraries
import pandas #for dataframe

import matplotlib.pyplot as plt #for plotting

from matplotlib import colors #for additional colors

import streamlit as st #for displaying on web app

import datetime #for date/time manipulation

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis
#%% Website display information
st.set_page_config(page_title="Precipitation Site Comparison", page_icon="🌦")

#%% Define data download as CSV function
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
#%% Read in raw weather data
data_raw=pandas.read_csv('DW_weather.csv.gz')

#%% Get site list
sites=data_raw['site'].drop_duplicates()

sumSites=pandas.DataFrame(sites)
sumSites=sumSites.set_index(['site']) #empty dataframe with sites as index

#%% add POR
data=data_raw
data=data_raw[['site','Month','pcpn','cumm_precip','WY']]
dates_new=pandas.to_datetime(data_raw.loc[:]['date'])
data=pandas.concat([data,dates_new],axis=1)
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


#filter by day count threshold

if len(month_select)==12:
    dayCountThres=330
    g=data.groupby(['site','WY'])
    data=g.filter(lambda x: len(x)>=dayCountThres)
else:
    dayCountThres=25
    g=data.groupby(['site','WY','Month'])
    data=g.filter(lambda x: len(x)>=dayCountThres)

#data.to_csv('temp.csv')
#%%select stat
#statistic

paramsDF=pandas.DataFrame({0:['pcpn'], 'long': ["Accumulated Precipitation (in)"]})
paramsSelect=paramsDF['long']

stat_select = "Accumulated Precipitation (in)"

#stat_select='Mean Temp (F)'
stat_selection=paramsDF.loc[paramsDF['long']==stat_select][0]

#%%calulcate params for POR
manKPOR=[]
por=[]
medstat=[]
for site in sites:
    dataBySite=data[data['site']==site]
    site_long=sites[sites.site==site].long.iloc[0]
    porS=dataBySite['date'].min()
    porE=dataBySite['date'].max()
    por.append([site_long,porS,porE])
    
    #get medians for POR of accumulated monthly pcpn
    dataBySiteParam=dataBySite['pcpn'] #accumulated precipitation by water year
    tempMonth_CY=dataBySite[['pcpn','Month','WY']]
    tempCY=tempMonth_CY.groupby(['WY']).sum()
    tempstat=tempCY['pcpn'].median()
    medstat.append(tempstat)
    

    #Man Kendall Test
    dataforMK=dataBySite[[stat_selection.iloc[0],'WY','Month']]
    tempPORMKMedian=dataforMK.groupby(['WY','Month']).sum().reset_index()[['WY','pcpn']]
    tempPORMKMedian=tempPORMKMedian.groupby(['WY']).sum()
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
sites=pandas.DataFrame(data['site'].drop_duplicates())
sites['long']=['Anterro (AN)','Cheesman (CM)','DIA (DI)','Dillon (DL)','DW Admin (DW)','Evergreen (EG)',
               'Eleven Mile (EM)','Gross (GR)','Kassler (KS)','Moffat HQ (MF)','Ralston (RS)','Central Park (SP)',
               'Strontia (ST)','Williams Fork (WF)']

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select_long = container.multiselect('Select one or more sites:', sites['long'], sites['long'])

else:
    multi_site_select_long = container.multiselect('Select one or more sites:', sites['long'],default=sites['long'].iloc[0])
 
multi_site_select=sites['site'][sites['long'].isin(multi_site_select_long)]

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
    return "%s-%s-%s"%(int(startYear-1),10,1)

start_date=startDate()

def endDate():
    return "%s-%s-%s"%(int(endYear),9,30)

end_date=endDate()

#change dates to similar for comparison
start_date1=pandas.to_datetime(start_date)
end_date1=pandas.to_datetime(end_date) 

#%%threshold filter
thresholdHigh = st.sidebar.number_input('Set Upper Precipitation threshold (in/day):',step=1,min_value=0, value=4)

thresholdLow = st.sidebar.number_input('Set Lower Precipitation threshold (in/day):',step=1,min_value=0, value=0)

#%%FILTERED DATA
data_sites_years=data_sites[(data_sites['date']>start_date1)&(data_sites['date']<=end_date1)]

#%% calculate params for selected period for Site Comparison Table

manKPORSelect=[]
medstatSelect=[]

siteSelect=data_sites_years['site'].drop_duplicates()

for site in sites['site']:
    dataBySite=data_sites_years[data_sites_years['site']==site]
    #filter by day count threshold
    
    dataBySite=dataBySite.groupby('WY').filter(lambda x : len(x)>=dayCountThres)
    
    #get medians
    dataBySiteParam=dataBySite[stat_selection]
    #get medians for POR of accumulated monthly pcpn
    tempMonth_CY=dataBySite[['pcpn','Month','WY']]
    tempCY=tempMonth_CY.groupby(['WY']).sum()
    tempstat=tempCY['pcpn'].median()
    medstatSelect.append(tempstat)
    
    dataforMK=dataBySite[['pcpn','WY','Month']]
    #Man Kendall Test
    try:
        tempPORMKMedian=dataforMK.groupby(['WY']).sum().reset_index()[['WY','pcpn']]
        tempPORMKMedian=tempPORMKMedian.groupby(['WY']).median()
        tempPORManK=mk.original_test(tempPORMKMedian)
    except:
        pass
    if tempPORManK[2]>0.1:
        manKPORSelect.append(float('nan'))
    else:
        manKPORSelect.append(tempPORManK[7])       #slope value 

manKPORSelect=pandas.DataFrame(manKPORSelect)
manKPORSelect=manKPORSelect.set_index([sites['site']])
manKPORSelect.columns=(['Select WY Trend'])
manKPORSelect=manKPORSelect[manKPORSelect.index.isin(siteSelect)]

medstatSelectdf=pandas.DataFrame(medstatSelect)
medstatSelectdf=medstatSelectdf.set_index([sites['site']])
medstatSelectdf.columns=(['Select WY Stat'])
medstatSelectdf=medstatSelectdf[medstatSelectdf.index.isin(siteSelect)]

sumSites=pandas.concat([sumSites,medstatSelectdf,manKPORSelect],axis=1)      
sumSites=sumSites.drop("Site",axis=1)

sumSites1=sumSites[sumSites.index.isin(multi_site_select)]

sumSitesDisplay=sumSites1.style\
    .format({'POR Stat':"{:.1f}",'POR Trend':"{:.2f}"
              ,'Select WY Stat':"{:.1f}",'Select WY Trend':"{:.2f}"})\
    .set_table_styles([dict(selector="th",props=[('max-width','3000px')])])

st.header("Site Comparison")
st.markdown("Compares the cumulative precipitation (in inches) and trends (Theil-Sen Slope in inches/year)")
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
sumSitesDisplay

#%% download Summary Table data

csv = convert_df(sumSites1)

st.download_button(
     label="Download Summary Table as CSV",
     data=csv,
     file_name='Summary_Table.csv',
     mime='text/csv',
 )

#%%Temp Current WY Median - WY Stat Median

compData=data_sites_years[['site',stat_selection.iloc[0],'WY','Month']]
selectCY=compData['WY'].drop_duplicates()
selectSite=compData['site'].drop_duplicates()

compList=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['WY']==CYrow]
    try:
        for siterow in selectSite:
            tempSiteData=tempCYdata[tempCYdata['site']==siterow]
            site_long=sites[sites.site==siterow].long.iloc[0]
            tempSiteCY_1=tempSiteData[['pcpn','WY']]
            tempSiteCY=tempSiteCY_1.groupby(['WY']).sum()
            # tempSiteCY=tempSiteCY_2[stat_selection.iloc[0]].median()
            
            #sum for year
            tempSiteCYSum=tempSiteCY[stat_selection.iloc[0]].sum()
            
            
            #median for all selected WYs stat
            tempPORmed=medstatSelectdf[medstatSelectdf.index==siterow]
            tempMedNorm=tempSiteCYSum-tempPORmed.iloc[0][0]
            
            #cumulative in WY / cumulative median at the site) (so answers will be in % rather than in) 
            precip_perc=(tempSiteCYSum/tempPORmed.iloc[0][0])*100
            
            compList.append([site_long,CYrow,tempMedNorm,tempSiteCY,tempSiteCYSum,precip_perc])
    except:
        compList.append([site_long,CYrow,None,None,None,None])
compListDF=pandas.DataFrame(compList)
compListDF.columns=['Site','WY','NormMed','WY Value','Total_Precip','Perc_Precip']

#%%transpose to get days as columns

list=compListDF['WY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    temp1=compListDF[compListDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[1]].copy()
    temp2.columns=[n]
    yearList[n]=temp2

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
    .format('{:,.1f}')

    #.background_gradient(cmap='Blues',low=0,high=1.02,axis=None, subset=select_col)\    
st.header("Update to Cumulative Precipitation in WY - Median Cumulative Precipitation in Selected WYs (in)")
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
yearList1

#%% download temp comparison data
csv = convert_df(yearList)

st.download_button(
     label="Download Precipitation Comparison as CSV",
     data=csv,
     file_name='pcpn_comp.csv',
     mime='text/csv',
 )

#%%percentage table

list=compListDF['WY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    temp1=compListDF[compListDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[4]].copy() #Percent change
    temp2.columns=[n]
    yearList[n]=temp2

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
    .format('{:,.1f}')

    #.background_gradient(cmap='Blues',low=0,high=1.02,axis=None, subset=select_col)\    
st.header("Update to Cumulative Precipitation in WY / Median Cumulative Precipitation in Selected WYs (%)")
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
yearList1

#%% download temp comparison data
csv = convert_df(yearList)

st.download_button(
     label="Download Percentage Precipitation Comparison as CSV",
     data=csv,
     file_name='pcpn_perc_comp.csv',
     mime='text/csv',
 )
#%%transpose to get days as columns

list=compListDF['WY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    temp1=compListDF[compListDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[3]].copy()
    temp2.columns=[n]
    yearList[n]=temp2

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
yearList2=yearList.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format('{:,.1f}')

    #.background_gradient(cmap='Blues',low=0,high=1.02,axis=None, subset=select_col)\    
st.header("Total %s in WY "%(stat_select))
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
yearList2

#%% download medians data

csv = convert_df(yearList)

st.download_button(
     label="Download Annual Totals as CSV",
     data=csv,
     file_name='Cumm_Pcpn_WY_value_comp.csv',
     mime='text/csv',
 )


#%%FOR THRESHOLD
#%%calc statistic for all months
compListCount=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['WY']==CYrow]
    # try:
    for siterow in selectSite:
        tempSiteData=tempCYdata[tempCYdata['site']==siterow]
        tempSiteData=tempSiteData[['WY','pcpn']].set_index('WY')
        site_long=sites[sites.site==siterow].long.iloc[0]
        # tempSiteCY_1=tempSiteData[['pcpn','WY']]
        # tempSiteCYSum=tempSiteCY_1.groupby(['WY']).sum()
        
        # #sum for year
        # tempSiteCYSum=tempSiteCY_2[stat_selection.iloc[0]].sum()
        
        count=tempSiteData[(tempSiteData < thresholdHigh)&(tempSiteData > thresholdLow)].count()[0]
        compListCount.append([site_long,CYrow,count])
# except:
    # compListCount.append([site_long,CYrow,None])
    
compListCountDF=pandas.DataFrame(compListCount)
compListCountDF.columns=['Site','WY','Count']

#%%transpose to get Months as columns
list=compListCountDF['WY'].drop_duplicates()
finalSites=compListCountDF['Site'].drop_duplicates()
list=list.sort_values()

countList=pandas.DataFrame(index=finalSites)
for n in list:
    #n=1979
    temp1=compListCountDF[compListCountDF['WY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[1]].copy()
    temp2.columns=[n]
    countList[n]=temp2
countList = countList.reindex(sorted(countList.columns,reverse=True), axis=1)

#%%colormap
def background_gradient(s, m=None, M=None, cmap='Blues',low=0.2, high=0):
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
st.header("Count of days with Precipitation between %s in and %s in"%(thresholdLow, thresholdHigh))
st.markdown("Date range for selected months: %s through %s"%(start_date, end_date))
countList1

#%% download temp count data

csv = convert_df(countList)

st.download_button(
     label="Download Precipitation Count Comparison as CSV",
     data=csv,
     file_name='Pcpn_count_comp.csv',
     mime='text/csv',
 )