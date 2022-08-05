import streamlit as st


st.set_page_config(
    page_title="Denver Water Climate APP",
    page_icon="👋",
)

st.write("# Welcome to Denver Water's Climate App! 👋")

st.header("SNOTEL Data")
"""
*WY = Water Year; October 1 through September 30; e.g. WY 2021 begins October 1, 2020 and ends September 30, 2021

*Peak SWE Day = Calendar Day (January 1 = Day 1) of last occurence of Peak SWE value

*POR = Period of Record
"""

st.sidebar.success("Select a demo above.")

