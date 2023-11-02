## Data Refresh
We have a cron job running on a machine to automatically refresh the data, so this should be taken care of automatically, but here are the steps:

- In the terminal, navigate to this repository.
- Run `git pull` to make sure the repo is up to date
- To download the SNOTEL data, run: 
    - `python Data_fetch.py -s -v`
    - This will update SNOTEL_data_raw.csv.gz. 
    - Add the updated file file to your staged changes:
    - `git add SNOTEL_data_raw.csv.gz`
- To download the temperature/precipitation data, run: 
    - `python Data_fetch.py -w -v`
    - This will update DW_weather.csv.gz
    - Add this file to your staged changes:
    - `git add DW_weather.csv.gz`
- Commit your changes: 
    - `git commit -m "<put a message here>"`
- Push your changes to github: 
    - `git push`

There is no need to update the soil moisture data, since it directly queries the API.

## Development 
[here is the dev environment](https://development-xax2apn4jgksccuchtxw7v.streamlit.app/)

You deploy to it by pushing from the "development" branch. Then, after you check that everything still works, you can merge the changes into main. 
    
### Incorporating updated data into app
1)	No app updates are needed so long as the updated data files from the scripts are uploaded into the GitHub repository; simply refresh the app and check that the year selection includes the updated data. 

Requirements.txt file is needed for streamlit to read required libraries. The "ulmo" library (necessary for SNOTEL data fetch) is not supported by streamlit, which is why I separated out the "Data_fetch.py" script. 
NOTE: This isn't true - it just needs to be a conda environment.yaml file. Look into automating this - TCS

When adding new pages, put scripts in "Pages" folder. 
