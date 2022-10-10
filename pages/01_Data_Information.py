# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 12:11:30 2022

@author: mpedrazas
"""

import streamlit as st


st.set_page_config(
    page_title="Data Information",
    page_icon="👋",
)


st.write("# Welcome to Denver Water's Climate App! 👋")

st.header("SNOTEL Data Information")
"""
*WY = Water Year; October 1 through September 30; e.g. WY 2021 begins October 1, 2020 and ends September 30, 2021

*First Zero SWE Day = Calendar Day (January 1 = Day 1) of first day of fully melted snowpack

*Peak SWE Day = Calendar Day (January 1 = Day 1) of last occurence of Peak SWE value

*POR = Period of Record
"""

st.header("Temperature and Precipitation Data Information")
"""
*Months with less than 25 days are excluded from analysis

*For site comparison:
    
    *If all months are selected, years with less than 330 days are excluded

    *If less than full year is selected, months with less than 25 days are excluded
"""

st.header("Seasons Information")
"""
*According to the meteorological definition, in the Northern Hemisphere, the months included in each season are the following:
    
    *Fall  = September, October and November

    *Winter = December, January and Februrary
    
    *Spring = March, April and May
    
    *Summer=June, July and August
"""

st.sidebar.success("Select a demo above.")
