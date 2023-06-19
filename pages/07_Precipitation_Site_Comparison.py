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

from PIL import Image

#%% Website display information
st.set_page_config(page_title="Precipitation Site Comparison", page_icon="🌦")
st.header("Precipitation Site Comparison Data Assessment")

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

#%%select stat
#statistic

paramsDF=pandas.DataFrame({0:['pcpn'], 'long': ["Accumulated Precipitation (in)"]})
paramsSelect=paramsDF['long']

stat_select = "Accumulated Precipitation (in)"

stat_selection=paramsDF.loc[paramsDF['long']==stat_select][0]

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

rev_sites = {
    'AN': 'Antero (AN)',
    'CM': 'Cheesman (CM)',
    'DI': 'DIA (DI)',
    'DL': 'Dillon (DL)',
    'DW': 'DW Admin (DW)',
    'EG': 'Evergreen (EG)',
    'EM': 'Eleven Mile (EM)',
    'GR': 'Gross (GR)',
    'KS': 'Kassler (KS)',
    'MF': 'Moffat HQ (MF)',
    'RS': 'Ralston (RS)',
    'SP': 'Central Park (SP)',
    'ST': 'Strontia (ST)',
    'WF': 'Williams Fork (WF)'}

long_site_names = list(sites.keys())

container=st.sidebar.container()
all=st.sidebar.checkbox("Select all")

if all:
    multi_site_select_long = container.multiselect('Select One or More Sites:', long_site_names, long_site_names)

else:
    multi_site_select_long = container.multiselect('Select One or More Sites:', sites.keys(), default=long_site_names[0])

#multi_site_select_long=["Antero (AN)" ]   

multi_site_select=[sites[i] for i in long_site_names]

def multisitefilter():
    return data[data['site'].isin(multi_site_select)]
    
#%%FILTERED DATA by site
data_sites=multisitefilter()

#%%start and end dates needed for initial data fetch
selectStartYear=data_sites['WY'].min()
selectEndYear=data_sites['WY'].max()
startM=10
startD=1
start_date = "%s-%s-0%s"%(selectStartYear,startM,startD) #if start day is single digit, add leading 0
end_date = "%s-09-30"%(selectEndYear)

# with st.sidebar: 
startYear = st.sidebar.number_input('Enter Beginning Water Year:', min_value=selectStartYear, max_value=selectEndYear, value=selectStartYear)
endYear = st.sidebar.number_input('Enter Ending Water Year:',min_value=selectStartYear, max_value=selectEndYear,value=selectEndYear)

def startDate():
    return "%s-%s-%s"%(int(startYear-1),10,1)

start_date=startDate()

def endDate():
    return "%s-%s-%s"%(int(endYear),9,30)

end_date=endDate()

#change dates to similar for comparison
start_date1=pandas.to_datetime(start_date)
end_date1=pandas.to_datetime(end_date) 

#%% Filter data by years
data_sites_years=data_sites[(data_sites['date']>=start_date1)&(data_sites['date']<=end_date1)]

maxDaily=data_sites_years['pcpn'].max()
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

#month_select=['Sep','Oct','Nov']
monthNum_select=pandas.DataFrame(month_select)
monthNum_select=monthOptions.loc[monthOptions['Month'].isin(month_select)]['Num']
    
def monthfilter():
    return data_sites_years[data_sites_years['Month'].isin(monthNum_select)]

def monthfilterPOR():
    return data[data['Month'].isin(monthNum_select)]

data_sites_years_monthsRaw=monthfilter()
data_monthsRaw=monthfilterPOR()

#filter by day count threshold

if len(month_select)==12:
    dayCountThres=330
    g=data_sites_years_monthsRaw.groupby(['site','WY'])
    data_sites_years_months=g.filter(lambda x: x['pcpn'].count().sum()>=dayCountThres)
    
    g=data_monthsRaw.groupby(['site','WY'])
    data_months=g.filter(lambda x: x['pcpn'].count().sum()>=dayCountThres)
    
else:
    dayCountThres=25
    g=data_sites_years_monthsRaw.groupby(['site','WY','Month'])
    data_sites_years_months=g.filter(lambda x: x['pcpn'].count().sum()>=dayCountThres)
    
    g=data_monthsRaw.groupby(['site','WY','Month'])
    data_months=g.filter(lambda x: x['pcpn'].count().sum()>=dayCountThres)

#%% get correct year range based on filtered data
selectStartYearTable=data_sites_years_months['WY'].min()
selectEndYearTable=data_sites_years_months['WY'].max()    
tableStartDate=datetime.datetime(selectStartYearTable-1,10,1).strftime("%Y-%m-%d")

tableEndDate=datetime.datetime(selectEndYearTable,9,30).strftime("%Y-%m-%d")

#%%calulcate params for POR
manKPOR=[]
por=[]
medstat=[]
for site in sites.values():
    dataBySite=data_months[data_months['site']==site]

    porS=dataBySite['date'].min()
    porE=dataBySite['date'].max()
    por.append([site,porS,porE])
    
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
        manKPOR.append([site,float('nan')])
    else:
        manKPOR.append([site,tempPORManK[7]])       #slope value 

manKPOR=pandas.DataFrame(manKPOR)
manKPOR.columns=(['Site','POR Trend for %s'%stat_select])
manKPOR = manKPOR.set_index('Site')
    
pordf=pandas.DataFrame(por)
pordf=pordf.set_index([0])
pordf.columns=["POR Start","POR End"]

medstatdf=pandas.DataFrame(medstat, index=sites.values())
medstatdf.columns=['POR Median of %s'%stat_select]

sumSites=pandas.concat([pordf,medstatdf,manKPOR],axis=1)

sumSites['POR Start']=pandas.to_datetime(sumSites["POR Start"]).dt.strftime('%Y-%m-%d')
sumSites['POR End']=pandas.to_datetime(sumSites["POR End"]).dt.strftime('%Y-%m-%d')

#%%threshold filter
maxDaily=round(data_sites_years_months['pcpn'].max(),2)
minDaily=round(data_sites_years_months['pcpn'].min(),2)

thresholdHigh = st.sidebar.number_input('Set Upper Precipitation (in/day) Threshold (Inclusive):',step=0.1,min_value=minDaily, value=maxDaily)

thresholdLow = st.sidebar.number_input('Set Lower Precipitation (in/day) Threshold (Inclusive):',step=0.1,min_value=minDaily, value=minDaily)

#%% calculate params for selected period for Site Comparison Table

manKPORSelect=[]
medstatSelect=[]

siteSelect=data_sites_years_months['site'].drop_duplicates()

for site in sites.values():
    dataBySite=data_sites_years_months[data_sites_years_months['site']==site]
   
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

manKPORSelect=pandas.DataFrame(manKPORSelect, index=sites.values())
# manKPORSelect=manKPORSelect.set_index([sites['site']])
manKPORSelect.columns=(['Select WY Trend for %s'%stat_select])
manKPORSelect=manKPORSelect[manKPORSelect.index.isin(siteSelect)]

medstatSelectdf=pandas.DataFrame(medstatSelect, index=sites.values())
# medstatSelectdf=medstatSelectdf.set_index([sites['site']])
medstatSelectdf.columns=(['Select WY Median of %s'%stat_select])
medstatSelectdf=medstatSelectdf[medstatSelectdf.index.isin(siteSelect)]

sumSites=pandas.concat([sumSites,medstatSelectdf,manKPORSelect],axis=1)      
sumSites=sumSites.drop("Site",axis=1)

sumSites1=sumSites[sumSites.index.isin(multi_site_select)]

sumSites1['long']=""

for i in range(0,len(sumSites1)):
    idx=sumSites1.index[i]
    site_long=rev_sites[idx]
    sumSites1.long.iloc[i]=site_long
    
sumSites1=sumSites1.set_index('long')
sumSitesDisplay=sumSites1.style\
    .format({'POR Median of %s'%stat_select:"{:.2f}",'POR Trend for %s'%stat_select:"{:.3f}"
              ,'Select WY Median of %s'%stat_select:"{:.2f}",'Select WY Trend for %s'%stat_select:"{:.3f}"})\
    .set_table_styles([dict(selector="th",props=[('max-width','3000px')])])

#%%Temp Current WY Median - WY Stat Median

compData=data_sites_years_months[['site',stat_selection.iloc[0],'WY','Month']]
selectWY=data_sites_years_monthsRaw['WY'].drop_duplicates()
selectSite=compData['site'].drop_duplicates()

compList=[]
for WYrow in selectWY:
    tempWYdata=compData[compData['WY']==WYrow]
    try:
        for siterow in selectSite:
            site_long=rev_sites[siterow]
            tempSiteData=tempWYdata[tempWYdata['site']==siterow]
            if len(tempSiteData)==0:
                compList.append([site_long,WYrow,None,None,None,None])
            else:
                
                tempSiteWY_1=tempSiteData[['pcpn','WY']]
                tempSiteWY=tempSiteWY_1.groupby(['WY']).sum()
                
                #sum for year
                tempSiteWYSum=tempSiteWY[stat_selection.iloc[0]].sum()
                
                #median for all selected WYs stat
                tempPORmed=medstatSelectdf[medstatSelectdf.index==siterow]
                tempMedNorm=tempSiteWYSum-tempPORmed.iloc[0][0]
                
                #cumulative in WY / cumulative median at the site) (so answers will be in % rather than in) 
                precip_perc=(tempSiteWYSum/tempPORmed.iloc[0][0])
        
                compList.append([site_long,WYrow,tempMedNorm,tempSiteWY,tempSiteWYSum,precip_perc])
            
    except:
        compList.append([site_long,WYrow,None,None,None,None])
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
def background_gradient(s, m=None, M=None, cmap='bwr_r',low=0., high=0.8):
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

yearListAbs = yearList.reindex(sorted(yearList.columns,reverse=True), axis=1)

#select_col=yearList.columns[:]
yearListAbs1=yearListAbs.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format('{:,.2f}')

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
def background_gradient(s, m=None, M=None, cmap='bwr_r',low=0., high=0.8):
    #print(s.shape)
    if m is None:
        m = s.min().min()
    if M is None:
        M = s.max().max()
    rng = M - m
    norm = colors.CenteredNorm(vcenter=1, halfrange=1.5)
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
    .format("{:,.0%}")

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

#select_col=yearList.columns[:]
yearList2=yearList.style\
    .set_properties(**{'width':'10000px'})\
    .apply(background_gradient, axis=None)\
    .format('{:,.2f}')

#%%FOR THRESHOLD
#%%calc statistic for all months
compListCount=[]
for WYrow in selectWY:
    tempWYdata=compData[compData['WY']==WYrow]
    try:
        for siterow in selectSite:
            tempSiteData=tempWYdata[tempWYdata['site']==siterow]
            tempSiteData=tempSiteData[['WY','pcpn']].set_index('WY')
            site_long=rev_sites[siterow]
            
            count=tempSiteData[(tempSiteData <= thresholdHigh)&(tempSiteData >= thresholdLow)].count()[0]
            if (len(tempSiteData)==0):
                compListCount.append([site_long,WYrow,None])
            else:
                compListCount.append([site_long,WYrow,count])
    except:
        compListCount.append([site_long,WYrow,None])
    
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

countList1=countList.style\
    .set_properties(**{'width':'10000px'})\
    .format('{:,.0f}')\
    .apply(background_gradient, axis=None)\

#%% Page DISPLAY
#%% Accumulated Precip
st.subheader("Monthly %s for Selected Site(s) and Month(s)/Season(s) by Water Year(s)" %stat_select)
st.markdown("""
Provides the total accumulated precipitation (in inches) for each selected site for the selected month(s)/season(s) and water year(s):  
Notes for all tables:
- If full year (12 months) is selected, years with fewer than 330 results are excluded and the result is presented as “nan.”
- If less than 12 months are selected, months with fewer than 25 results are excluded and presented as “nan.”          
    """)
            
st.markdown("Selected Water Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(yearList2)
st.markdown("""
Table Note:
- The user-defined precipitation threshold does not change this table.
            """)
            
#%% download accumulated Precip
csv = convert_df(yearList)

st.download_button(
 label="Download Annual Totals (as CSV)",
 data=csv,
 file_name='Cumm_Pcpn_WY_value_comp.csv',
 mime='text/csv',
 )

#%%Summary Statistics for Selected Sites, Calendar Years and Months/Seasons:  
st.subheader("Summary of %s for Selected Sites, Water Year(s) and Month(s)/Season(s)"%stat_select)
st.markdown(
    """
Provides period of record dates and accumulated precipitation medians and trends for each selected site for the selected month(s)/season(s) and water year(s): 
- **POR Start:** Earliest date of available data for the site 
- **POR End:** Latest date of available data for site 
- **POR Median:** Median of accumulated precipitation and month(s)/season(s) for the entire period of record, regardless of selected water year(s)
- **POR Trend:** Trend using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for entire period of record of the selected summary statistic:
    - **Accumulated Precipitation** (increasing or decreasing inches per year)
- **Selected WY Median:** Median of accumulated precipitation for the selected month(s)/season(s) and water year(s).
- **Selected WY Trend:** Trend for accumulated precipitation (inches per year) using the Theil-Sen Slope analysis where Mann-Kendall trend test is significant for the selected month(s)/season(s) and water year(s).  
"""        
    )
    
st.markdown("User-Selected Month(s)/Season(s) in Water Year(s): %s through %s"%(tableStartDate, tableEndDate))
sumSitesDisplay
st.markdown(
    """
Table Notes:
- If no trend, then result is presented as “nan.” 
- The user-defined precipitation threshold does not change this table.
    """)
    
#%% download Summary Table data

csv = convert_df(sumSites1)

st.download_button(
     label="Download Summary %s Table (as CSV)"%stat_select,
     data=csv,
     file_name='Summary_Table.csv',
     mime='text/csv',
 )

#%% Net Difference Absolute
st.subheader("Net Difference Between Select WY Median of %s and POR Median of %s"%(stat_select,stat_select))
st.markdown(
    """
For example, the total accumulated precipitation for 2015 at Antero was 14.87 inches and the median for the full period of record was 10.37 in, so the net difference presented for Antero in 2015 with is +4.50 inches. This shows that 2015 had higher than average precipitation.
"""
    )

st.markdown("User-Selected Month(s)/Season(s) in Water Year(s): %s through %s"%(tableStartDate, tableEndDate))
yearListAbs1
st.markdown(
    """
Table Note:
- The user-defined precipitation threshold does not change this table.
    """)
    
#%% download temp comparison data
csv = convert_df(yearListAbs)

st.download_button(
     label="Download Net Difference Table (as CSV)",
     data=csv,
     file_name='Net_diff.csv',
     mime='text/csv',
 )
#%% Net Difference Percent
st.subheader("Percent of %s for Individual Water Year Compared to the Median of %s for Selected Water Year Range"%(stat_select,stat_select))
st.markdown(
    """
The percent is calculated by dividing the accumulated precipitation for selected months/seasons in a selected water year by the accumulated precipitation for the selected water year range for the selected month(s)/season(s) and multiplying by 100. 
- For example, the total accumulated precipitation for 2015 at Antero (14.87 inches) is divided by the median for the full period of record (10.37 in) and multiplied by 100. The result shows that precipitation for 2015 at Antero was 143% of the median for the full period of record.
"""
    )

st.markdown("User-Selected Month(s)/Season(s) in Water Year(s): %s through %s"%(tableStartDate, tableEndDate))
yearList1
st.markdown(
    """
Table Notes:
- If no trend, then result is presented as “nan.” 
- The user-defined precipitation threshold does not change this table.
    """)
#%% download temp comparison data
csv = convert_df(yearList)

st.download_button(
     label="Download % Comparison (as CSV)",
     data=csv,
     file_name='Percent_comp.csv',
     mime='text/csv',
 )    

#%%display
pandas.set_option('display.width',100)
st.subheader("Count of %s Days Between %s and %s Inches"%(stat_select,thresholdLow,thresholdHigh))
st.markdown(
"""For each selected site for the selected month(s)/season(s) and water year(s), displays the number of days in each month within the user-defined upper and lower accumulated precipitation thresholds.    
""")

st.markdown("Selected Water Year(s): %s through %s"%(tableStartDate, tableEndDate))   
st.dataframe(countList1)
st.markdown("""
Table Note:
- The count includes days that are equal to the value of each threshold.
            """)

#%% download temp count data

csv = convert_df(countList)

st.download_button(
     label="Download Precipitation Count Comparison (as CSV)",
     data=csv,
     file_name='Pcpn_count_comp.csv',
     mime='text/csv',
 )
#%% Stations display information
st.subheader("Weather Station Locations")
image=Image.open("Maps/2_Weather_Stations.png")
st.image(image, width=500)