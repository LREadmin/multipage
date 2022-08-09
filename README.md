To update SNOTEL or temperature data: run "Data_fetch.py"

-SNOTEL site info gets all SNOTEL site info from NRCS, this is used for joining data in the SNOTEL_compare_sites page.

-SNOTEL data is used to get SWE data from selected SNOTEL sites; make sure "sitecode" list is updated with sites of interest. 

-TEMPERATURE data merges all temp data from DW processed files, using "Weather_Data" folder.

-outputs from "Data_fetch.py" are:

--SNOTEL_sites.csv

--siteNamesList.txt

--SNOTEL_data_raw.csv

--DW_weather.csv

Requirements.txt file is needed for streamlit to read required libraries. The "ulmo" library (necessary for SNOTEL data fetch) is not supported by streamlit, which is why I separated out the "Data_fetch.py" script. 

SiteNamesListNS.txt joins the sites in siteNamesList.txt with DW collection system (North or South)
