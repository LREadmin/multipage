import streamlit as st


st.set_page_config(
    page_title="Denver Water Climate APP",
    page_icon="👋",
)


st.write("# Welcome to Denver Water's Climate App! 👋")

st.header("SNOTEL Data Information")
"""
*WY = Water Year; October 1 through September 30; e.g. WY 2021 begins October 1, 2020 and ends September 30, 2021

*Peak SWE Day = Calendar Day (January 1 = Day 1) of last occurence of Peak SWE value

*POR = Period of Record
"""

st.header("Temperature Data Information")
"""

*For site comparison:
    
    *If all months are selected, years with less than 330 days are excluded

    *If less than full year is selected, months with less than 25 days are excluded
"""

st.sidebar.success("Select a demo above.")

