SNOTEL Data
1)	Download/run “Data_fetch.py” lines through 105:

    a. 	This SNOTEL block of code is needed because The "ulmo" library (necessary for SNOTEL data fetch) is not supported by Streamlit. 

    b.	Verify that the sitecode list in lines 36 through 51 is representative of the SNOTEL sites you would like to include in the analysis. 

    c.	Line 58 sets the period of record end date to the day the code is rerun
2)	A new file, “SNOTEL_data_raw.csv.gz,” will be saved to your local working directory. 
3)	A new file, “SiteNamesList.txt,” will be written to your local working directory.

    a.	This file is read by “02_SNOTEL_Individual_Sites.py”
4)	If you modified the sites in step 3, manually update SiteNamesListNS.txt as well

    a.	This file is read by “03_SNOTEL_Site_Comparison.py”
5)	A new file, “siteNamesListCode.csv,” will be written to your local working directory.

    a.	This file is read by “SMS_data_fetch_all.py,” “08_Soil_Moisture_Individual_Sites.py” and “09_Soil_Moisture_Site_Comparison.py”
6)	Copy the new files generated in steps 4-6 to the GitHub multipage parent directory. 
Temperature/Precipitation Data
1)	Copy DW weather station data into a folder titled “Weather_Data” in your local working directory
2)	Download/run “Data_fetch.py” lines 108 -118
3)	A new file, “DW_weather.csv.gz” will be saved to your local working directory. 

    a.  This file concatenates individual weather station files
4)	Copy the new file generated in steps 4 to the GitHub multipage parent directory. 
Soil Moisture Data
1)	Create a folder titled “SMS_Data” in your local working directory.
2)	Download/run “SMS_data_fetch_all.py”
3)	New files, one for each SNOTEL site, will be saved to the “SMS_Data” folder in your local working directory. 
4)	 The last block of code, lines 61-71, concatenates individual soil moisture files and creates a new file “SNOTEL_SMS.csv.gz”
    
    a.  This file is read by “09_Soil_Moisture_Site_Comparison.py”

Requirements.txt file is needed for streamlit to read required libraries. The "ulmo" library (necessary for SNOTEL data fetch) is not supported by streamlit, which is why I separated out the "Data_fetch.py" script. 

When adding new pages, put scripts in "Pages" folder. 
