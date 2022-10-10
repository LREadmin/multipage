import streamlit as st


st.set_page_config(
    page_title="Denver Water Climate APP",
    page_icon="👋",
)


st.write("# Welcome to Denver Water's Climate App! 👋")

st.header("Static Elevation Map of the Assesment Basin and Station Locations")
#add map here when DW provides it

st.header("Temperature and Precipitation Data Information")
"""
*Months with less than 25 days are excluded from analysis

*For site comparison:
    
    *If all months are selected, years with less than 330 days are excluded

    *If less than full year is selected, months with less than 25 days are excluded
"""

st.header("Seasonal Information")
"""
*For site comparison:
    
*According to the meteorological definition, in the Northern Hemisphere, the months included in each season are the following:
    
    *Fall  = September, October and November

    *Winter = December, January and Februrary
    
    *Spring = March, April and May
    
    *Summer = June, July and August
"""

