# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 14:48:58 2023

@author: msparacino
"""

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Denver Water Climate Dashboard",
    page_icon="👋",
)


st.write("# Welcome to Denver Water's Climate Dashboard! 👋")

url1="https://climate.colostate.edu/data_access.html"
url2="https://www.nrcs.usda.gov/wps/portal/wcc/home/quicklinks/imap"

#%%
st.header("Introduction")
st.markdown(
    """
This Dashboard provides access to climate data within and surrounding Denver Water’s Collection and Distribution Systems.  Data are from the following three sources: 

- Denver Water weather stations (temperature and precipitation) 
    """
    )

st.markdown("- Other weather stations available through the [Colorado Climate Center](%s): (temperature and precipitation)" %url1)

st.markdown("- National Resource Conservation Service (NRCS) [Snow Telemetry (SNOTEL)](%s) sites (snow water equivalent (SWE) and soil moisture)"%url2)

st.markdown(
    """
This Dashboard includes data from the early 1900s through the current month, depending  on the period of record (POR) for each site. The analysis options target a long-term view of SWE, temperature, precipitation, and soil moisture over time and space using summary statistics and trends. Monthly updates and analysis are available through Climate Tracker reports available from the Climate Adaptation & Water Resource Planning Team.     

    """
    )

#%%
st.header("SNOTEL and Weather Station Locations ")
image=Image.open("Maps/4_All_Sites.png")
st.image(image)

#%%
st.header("Data Availability and Assessment Notes")
st.markdown(
    """
    _Minimum monthly and annual data points:_
    
    - **Monthly Statistics:** Months with fewer than 25 days of data are excluded from the analysis 
    - **Annual Statistics:**  Years with fewer than 330 days of data are excluded from the analysis 
    - Months and/or years that do not meet the minimum data point requirement will display as black cells with “nan.”  
        
    _Soil Moisture Depth Averaging:_   
    - Median statistic and trend represent depth averaged soil moisture across the depths selected by the user. If you would like to see, for example, "median soil moisture at depth of 2-inches," select only the 2-inch depth.
    - Not all SNOTEL sites have soil moisture probes at all possible depths. On the Soil Moisture Comparison Sites page, inter-site comparisons are calculated only for sites that have soil moisture sensors at all depths selected by the user. 
    """
    )
#%%
st.header("Acronyms & Definitions")
st.markdown(
    """  
    **F:** Degrees Fahrenheit  
    
    **In:** Inches
    
    **Median:** Value in the middle of the selected data set 
    
    **POR:** Period of Record: the timeframe for which a monitoring value (e.g., temperature) was collected and is included in the dashboard for a specific site 
    
    **Seasons:**  Filter selections for Temperature, Precipitation & Soil Moisture are defined for the purposes of this dashboard as follows: 
    - **Fall:** September, October and November 
    - **Winter:** December, January and February 
    - **Spring:** March, April, May 
    - **Summer:** June, July, August 
    
    **SWE:** Snow Water Equivalent: the amount of liquid water in snow  
    
    **CY:** Calendar Year: January 1 through December 31st; used for temperature analysis  
    
    **WY:** Water Year: October 1 through September 30 (e.g. WY 2021 begins October 1, 2020 and ends September 30, 2021); used for SWE, precipitation, and soil moisture analysis
    
    **Selected CY or WY:** Year range selected using the Beginning and End year filters on the left side of the dashboard 

    """
    )
#%%
st.header("Trend Statistics")
st.markdown(
    """
    **Theil-Sen Slope:** a non-parametric, unbiased estimator method for linear regression. The Theil-Sen slope fits a line based on the median of slopes of all lines through pairs of points. Because it is non-parametric, it is insensitive to outliers (unlike least squares-based simple linear regression). 

    **Mann-Kendall Trend Test:** a non-parametric statistical test used to assess whether a set of data values is increasing over time or decreasing over time, and whether the trend in either direction is statistically significant.

    **Mann-Kendall Trend Test p-Value:** represents a probability of the error of the Trend test. The lower the p-value, the greater the statistical significance.

    **Trends:** Theil-Sen Slope trend values (e.g., "inches per year") are only reported as significant in instances where the Mann-Kendall Trend test p-value is <0.1, otherwise, “nan” is shown for statistics for which there is no statistically significant linear trend.
    """)