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


