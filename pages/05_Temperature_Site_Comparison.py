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

import arrow #another library for date/time manipulation

import pymannkendall as mk #for trend anlaysis

from PIL import Image #for map

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

#%% Website display information
st.set_page_config(page_title="Temperature Site Comparison", page_icon="📈")
st.header("Temperature Site Comparison Data Assessment")

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
data=data_raw[['site','Month','maxt','mint','meant']]
dates_new=pandas.to_datetime(data_raw.loc[:]['date'])
data=pandas.concat([data,dates_new],axis=1)
data['CY']=data['date'].dt.year

#%%select stat
#statistic

paramsDF=pandas.DataFrame({0:['maxt','mint','meant'], 'long': ['Max Temp (F)', 'Min Temp (F)', 'Mean Temp (F)']})
paramsSelect=paramsDF['long']

stat_select= st.sidebar.selectbox(
     'Select One Statistic:', paramsSelect)

#stat_select='Mean Temp (F)'
stat_selection=paramsDF.loc[paramsDF['long']==stat_select][0]


#%%make selections
sites=pandas.DataFrame(data['site'].drop_duplicates())
sites['long']=['Antero (AN)','Cheesman (CM)','DIA (DI)','Dillon (DL)','DW Admin (DW)','Evergreen (EG)',
               'Eleven Mile (EM)','Gross (GR)','Kassler (KS)','Moffat HQ (MF)','Ralston (RS)','Central Park (SP)',
               'Strontia (ST)','Williams Fork (WF)']

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select_long = container.multiselect('Select One or More Sites:', sites['long'], sites['long'])

else:
    multi_site_select_long = container.multiselect('Select One or More Sites:', sites['long'],default=sites['long'].iloc[0])
 
multi_site_select=sites['site'][sites['long'].isin(multi_site_select_long)]

def multisitefilter():
    return data[data['site'].isin(multi_site_select)]

#%% Filter data by sites   
data_sites=multisitefilter()

#%%start and end dates needed for initial data fetch
selectStartYear=data_sites['CY'].min()
selectEndYear=data_sites['CY'].max()
startM=1
startD=1

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Calendar Year:', min_value=selectStartYear, max_value=selectEndYear, value=selectStartYear)
endYear = st.sidebar.number_input('Enter Ending Calendar Year:',min_value=selectStartYear, max_value=selectEndYear,value=selectEndYear)

def startDate():
    return "%s-0%s-0%s"%(int(startYear),1,1)

start_date=startDate()

def endDate():
    return "%s-%s-%s"%(int(endYear),12,31)

end_date=endDate()

#change dates to similar for comparison
start_date1=pandas.to_datetime(start_date)
end_date1=pandas.to_datetime(end_date) 

tableStartDate=datetime.datetime(startYear,1,1).strftime("%Y-%m-%d")

tableEndDate=datetime.datetime(endYear,12,31).strftime("%Y-%m-%d")

#%%Filter site data by year
data_sites_years=data_sites[(data_sites['date']>start_date1)&(data_sites['date']<=end_date1)]

#%%select months

monthOptions=pandas.DataFrame({'Month':['Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug',],
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
    month_select = container.multiselect('Select month(s):',pandas.concat([winterMonths,springMonths]), pandas.concat([winterMonths,springMonths]))
elif winter and summer and (fall==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([winterMonths,summerMonths]), pandas.concat([winterMonths,summerMonths]))
elif winter and fall and (spring==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([winterMonths,fallMonths]), pandas.concat([winterMonths,fallMonths]))
elif winter and (fall==False) and (spring==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',winterMonths, winterMonths)
elif spring and (fall==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',springMonths, springMonths)
elif fall and spring and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([springMonths,fallMonths]), pandas.concat([springMonths,fallMonths]))
elif spring and summer and (winter==False) and (fall==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([springMonths,summerMonths]), pandas.concat([springMonths,summerMonths]))
elif summer and fall and (winter==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([summerMonths,fallMonths]), pandas.concat([summerMonths,fallMonths]))
elif summer and (fall==False) and (winter==False) and (spring==False):
    month_select = container.multiselect('Select month(s):',summerMonths, summerMonths)
elif fall and (spring==False) and (winter==False) and (summer==False):
    month_select = container.multiselect('Select month(s):',fallMonths, fallMonths)
elif fall and summer and spring and (winter==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([springMonths,summerMonths,fallMonths]), pandas.concat([springMonths,summerMonths,fallMonths]))
elif fall and summer and winter and (spring==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([winterMonths,summerMonths,fallMonths]), pandas.concat([winterMonths,summerMonths,fallMonths]))
elif spring and summer and winter and (fall==False):
    month_select = container.multiselect('Select month(s):',pandas.concat([winterMonths,springMonths,summerMonths]), pandas.concat([winterMonths,springMonths,summerMonths]))
elif spring and fall and summer and winter:
    month_select = container.multiselect('Select month(s):',pandas.concat([springMonths,winterMonths,summerMonths,fallMonths]), pandas.concat([springMonths,winterMonths,summerMonths,fallMonths]))

else:
    month_select = container.multiselect('Select month(s):', monthSelect,default=monthSelect)

monthNum_select=pandas.DataFrame(month_select)
monthNum_select=monthOptions.loc[monthOptions['Month'].isin(month_select)]['Num']
    
def monthfilter():
    return data_sites_years[data_sites_years['Month'].isin(monthNum_select)]

def monthfilterPOR():
    return data[data['Month'].isin(monthNum_select)]

data_sites_years_months=monthfilter()
data_months=monthfilterPOR()

#filter by day count threshold

if len(month_select)==12:
    dayCountThres=330
    g=data_sites_years_months.groupby(['site','CY'])
    data_sites_years_months=g.filter(lambda x: x['%s'%stat_selection.iloc[0]].count().sum()>=dayCountThres)
    
    g=data_months.groupby(['site','CY'])
    data_months=g.filter(lambda x: x['%s'%stat_selection.iloc[0]].count().sum()>=dayCountThres)
    
else:
    dayCountThres=25
    g=data_sites_years_months.groupby(['site','CY','Month'])
    data_sites_years_months=g.filter(lambda x: x['%s'%stat_selection.iloc[0]].count().sum()>=dayCountThres)
    
    g=data_months.groupby(['site','CY','Month'])
    data_months=g.filter(lambda x: x['%s'%stat_selection.iloc[0]].count().sum()>=dayCountThres)

#%%calulcate params for POR
manKPOR=[]
por=[]
medstat=[]
for site in sites['site']:
    dataBySite=data_months[data_months['site']==site]
    
    porS=dataBySite['date'].min()
    porE=dataBySite['date'].max()
    por.append([site,porS,porE])
    
    #get medians
    dataBySiteParam=dataBySite[stat_selection.iloc[0]]
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
manKPOR=manKPOR.set_index([sites['site']])
manKPOR.columns=(['Site','POR Trend for %s'%stat_select])
    
pordf=pandas.DataFrame(por)
pordf=pordf.set_index([0])
pordf.columns=["POR Start","POR End"]

medstatdf=pandas.DataFrame(medstat)
medstatdf=medstatdf.set_index([sites['site']])
medstatdf.columns=['POR Median of %s'%stat_select]

sumSites=pandas.concat([pordf,medstatdf,manKPOR],axis=1)

sumSites['POR Start']=pandas.to_datetime(sumSites["POR Start"]).dt.strftime('%Y-%m-%d')
sumSites['POR End']=pandas.to_datetime(sumSites["POR End"]).dt.strftime('%Y-%m-%d')

#%%threshold filter
maxDaily=int(np.ceil(data_sites_years_months['%s'%stat_selection.iloc[0]].max())) #rounds up to max num in dataset
minDaily=int(np.floor(data_sites_years_months['%s'%stat_selection.iloc[0]].min())) #rounds down to max num in dataset

thresholdHigh = st.sidebar.number_input('Set Upper %s Threshold (Inclusive):'%stat_select,step=1, min_value=minDaily, value=maxDaily)

thresholdLow = st.sidebar.number_input('Set Lower %s Threshold (Inclusive):'%stat_select,step=1, min_value=minDaily, value=minDaily)

#%% calculate params for selected period

manKPORSelect=[]
medstatSelect=[]

siteSelect=data_sites_years_months['site'].drop_duplicates()

for site in sites['site']:
    dataBySite=data_sites_years_months[data_sites_years_months['site']==site]
    #filter by day count threshold

    dataBySite=dataBySite.groupby('CY').filter(lambda x : len(x)>=dayCountThres)

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
manKPORSelect=manKPORSelect.set_index([sites['site']])
manKPORSelect.columns=(['Select CY Trend for %s'%stat_select])
manKPORSelect=manKPORSelect[manKPORSelect.index.isin(siteSelect)]

medstatSelectdf=pandas.DataFrame(medstatSelect)
medstatSelectdf=medstatSelectdf.set_index([sites['site']])
medstatSelectdf.columns=(['Select CY Median of %s'%stat_select])
medstatSelectdf=medstatSelectdf[medstatSelectdf.index.isin(siteSelect)]

sumSites=pandas.concat([sumSites,medstatSelectdf,manKPORSelect],axis=1)      
sumSites=sumSites.drop("Site",axis=1)

sumSites1=sumSites[sumSites.index.isin(multi_site_select)]
sumSites1['long']=""

for i in range(0,len(sumSites1)):
    idx=sumSites1.index[i]
    site_long=sites[sites.site==idx].long.iloc[0]
    sumSites1.long.iloc[i]=site_long
    
sumSites1=sumSites1.set_index('long')
sumSitesDisplay=sumSites1.style\
    .format({'POR Median of %s'%stat_select:"{:.1f}",'POR Trend for %s'%stat_select:"{:.2f}"
              ,'Select CY Median of %s'%stat_select:"{:.1f}",'Select CY Trend for %s'%stat_select:"{:.2f}"})\
    .set_table_styles([dict(selector="th",props=[('max-width','3000px')])])

#%%Temp CY Median / Temp POR Median

compData=data_sites_years_months[['site',stat_selection.iloc[0],'CY']]
selectCY=compData['CY'].drop_duplicates()
selectSite=compData['site'].drop_duplicates()

compList=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['CY']==CYrow]
    try:
        for siterow in selectSite:
            site_long=sites[sites.site==siterow].long.iloc[0]
            tempSiteData=tempCYdata[tempCYdata['site']==siterow]
            tempSiteCY=tempSiteData[stat_selection.iloc[0]].median()
            
            #median for selected POR
            tempPORmed=medstatSelectdf[medstatSelectdf.index==siterow]
            tempMedNorm=tempSiteCY-tempPORmed.iloc[0][0]
            
            compList.append([site_long,CYrow,tempMedNorm,tempSiteCY])
    except:
        compList.append([site_long,CYrow,None,None])
compListDF=pandas.DataFrame(compList)
compListDF.columns=['Site','CY','NormMed','CY Value']

#%%transpose to get days as columns

list=compListDF['CY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    temp1=compListDF[compListDF['CY']==n]
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
    norm = colors.CenteredNorm(vcenter=0, halfrange=15)
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

#%%transpose to get days as columns

list=compListDF['CY'].drop_duplicates()
finalSites=compListDF['Site'].drop_duplicates()
list=list.sort_values()
yearList=pandas.DataFrame(index=finalSites)
for n in list:
    temp1=compListDF[compListDF['CY']==n]
    temp1=temp1.set_index('Site')
    temp2=temp1.iloc[:,[2]].copy()
    temp2.columns=[n]
    yearList[n]=temp2

#%%colormap
def background_gradient(s, m=None, M=None, cmap='bwr',low=0.2, high=0):
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

#%%FOR THRESHOLD
#%%calc statistic for all months
compListCount=[]
for CYrow in selectCY:
    tempCYdata=compData[compData['CY']==CYrow]
    try:
        for siterow in selectSite:
            site_long=sites[sites.site==siterow].long.iloc[0]
            tempSiteData=tempCYdata[tempCYdata['site']==siterow]
            tempSiteData=tempSiteData.drop(columns=['site','CY'])
            count=tempSiteData[(tempSiteData <= thresholdHigh)&(tempSiteData >= thresholdLow)].count()[0]
            if (len(tempSiteData)==0):
                compListCount.append([site_long,CYrow,None])
            else:
                compListCount.append([site_long,CYrow,count])
    except:
        compListCount.append([site_long,CYrow,None])
        
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

countList1=countList.style\
    .set_properties(**{'width':'10000px'})\
    .format('{:,.0f}')\
    .apply(background_gradient, axis=None)\

#%% Page DISPLAY
#%% MEDIAN 
st.subheader("Median of %s for Selected Site(s) and Month(s)/Season(s) by Calendar Year(s)"%(stat_select))
st.markdown(
    """
Provides the median of the selected summary statistic for each selected site for the selected month(s)/season(s) and calendar year(s):
- **Max Temp (F):** The recorded daily maximum temperature 
- **Min Temp (F):** The recorded daily minimum temperature 
- **Mean Temp (F):** Calculated daily mean using the recorded maximum and minimum temperature
Notes for all tables:
- If full year (12 months) is selected, years with fewer than 330 results are excluded and the result is presented as “nan.”
- If less than 12 months are selected, months with fewer than 25 results are excluded and presented as “nan.”
"""
)
st.markdown("User-Selected Month(s)/Season(s) in Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))
yearList2
st.markdown(
    """
Table Note
- The user-defined temperature threshold does not change this table.
"""
)
#%% download medians data
 
csv = convert_df(yearList)
 
st.download_button(
     label="Download Median of %s Table (as CSV)"%stat_select,
     data=csv,
     file_name='Median_Site_Table.csv',
     mime='text/csv',
 ) 
#%%Summary Statistics for Selected Sites, Calendar Years and Months/Seasons:  
st.subheader("Summary %s for Selected Sites, Calendar Year(s) and Month(s)/Season(s)"%stat_select)
st.markdown(
    """
For the selected summary statistic (Max Temp, Min Temp, or Mean Temp), provides period of record dates and both period of record and calendar year median statistics and trends for each selected site for the selected month(s)/season(s) and calendar year(s). 
- **POR Start:** Earliest date of available data for the site 
- **POR End:** Latest date of available data for site 
- **POR Median:** Median of the selected summary statistic (Max Temp, Min Temp, or Mean Temp) and month(s)/season(s) for the entire period of record, regardless of selected calendar year(s)
- **POR Trend:** Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for entire period of record of the selected summary statistic:
    - **Max Temp:** (increasing or decreasing degrees Fahrenheit per year)
    - **Min Temp:** (increasing or decreasing degrees Fahrenheit per year)
    - **Median Temp:** (increasing or decreasing degrees Fahrenheit per year)
- **Selected CY Median:** Median of the selected summary statistic (Max Temp, Min Temp, or Mean Temp) for the selected month(s)/season(s) and calendar year(s).
- **Selected CY Trend:** Trend for the Selected summary statistic (Max Temp, Min Temp, or Mean Temp) using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for the selected month(s)/season(s) and calendar year(s). 
    """        
    )
    
st.markdown("User-Selected Month(s)/Season(s) in Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))
sumSitesDisplay
st.markdown(
    """
Table Note:
- The user-defined temperature threshold does not change this table.
    """)

#%% download Summary Table data
csv = convert_df(sumSites1)

st.download_button(
     label="Download Summary %s Table (as CSV)"%stat_select,
     data=csv,
     file_name='Summary_Table.csv',
     mime='text/csv',
 )

#%%
st.subheader("Net Difference Between Select CY Median of %s and POR Median of %s"%(stat_select,stat_select))
st.markdown(
    """
For example, the median maximum temperature at Antero in 2012 was 58 degrees F and the median for the full period of record was 54 degrees F, so the net difference presented for Antero in 2012 is +4 degrees F. 
    """
    )

st.markdown("User-Selected Month(s)/Season(s) in Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))
yearList1
st.markdown(
    """
Table Note:
- The user-defined temperature threshold does not change this table.
    """)

#%% download temp comparison data
csv = convert_df(yearList)

st.download_button(
     label="Download Net Difference Table (as CSV)",
     data=csv,
     file_name='Net_Diff.csv',
     mime='text/csv',
 )

#%%

st.subheader("Count of %s Days Within %s\N{DEGREE SIGN}F and %s\N{DEGREE SIGN}F"%(stat_select,thresholdLow,thresholdHigh))
st.markdown(
"""For each selected site, %s, month(s)/season(s) and selected calendar year(s), 
displays the number of days in each month within the user-defined upper and lower thresholds.
"""%stat_select)
st.markdown("User-Selected Month(s)/Season(s) in Calendar Year(s): %s through %s"%(tableStartDate, tableEndDate))
countList1
st.markdown("""
Table Note:
- The count includes days that are equal to the value of each threshold.
            """)

#%% download temp count data

csv = convert_df(countList)

st.download_button(
     label="Download Temperature Count Comparison (as CSV)",
     data=csv,
     file_name='Temp_count_comp.csv',
     mime='text/csv',
 )
#%% Stations display information
st.subheader("Weather Station Locations ")
image=Image.open("Maps/2_Weather_Stations.png")
st.image(image, width=500)
