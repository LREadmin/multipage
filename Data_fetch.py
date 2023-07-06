# -*- coding: utf-8 -*-
"""
Get data for DW tools
"""
# Package for public hydrology/climate data ulmo.readthedocs.io/en/latest/
# the Ulmo package has weird dependency issues with the "suds-jurko" package and 
# cannot be included in a deployed app via streamlit
# ^ This is incorrect. It will work fine if it's installed with conda.
# Include an environment.yml file instead of a requirements.txt file to tell
# streamlit to use conda. I suggest using `channel: conda-forge`, but I'm not
# the code police - follow your bliss.
# https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/app-dependencies#add-python-dependencies
import os
import argparse
from datetime import datetime
import ulmo  
import pandas as pd
import numpy as np

WSDLURL='https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL'
VARIABLE_CODE='SNOTEL:WTEQ_D'
SITE_CODES = [
        'SNOTEL:335_CO_SNTL',
        'SNOTEL:938_CO_SNTL',
        'SNOTEL:913_CO_SNTL',
        'SNOTEL:415_CO_SNTL',
        'SNOTEL:936_CO_SNTL',
        'SNOTEL:1186_CO_SNTL',
        'SNOTEL:485_CO_SNTL',
        'SNOTEL:505_CO_SNTL',
        'SNOTEL:1187_CO_SNTL',
        'SNOTEL:531_CO_SNTL',
        'SNOTEL:935_CO_SNTL',
        'SNOTEL:970_CO_SNTL',
        'SNOTEL:937_CO_SNTL',
        'SNOTEL:1014_CO_SNTL',
        'SNOTEL:939_CO_SNTL']


def snotel_fetch(site_code: str, 
                 start_date: str, 
                 end_date: str,
                 verbose: bool=False):
    """ Input:
            site_code:
            start_date:
            end_date:
            verbose:
        Output:
            values_df:
    """
    if verbose:
        print(site_code, VARIABLE_CODE, start_date, end_date)
    # I'm 99% sure this is unnecessary
    # values_df = None
    try:
        # can pull data out of this dict
        #Request data from the server
        site_values = ulmo.cuahsi.wof.get_values(WSDLURL, 
                                                 site_code, 
                                                 VARIABLE_CODE, 
                                                 start=start_date, 
                                                 end=end_date)
        #Convert to a Pandas DataFrame   
        values_df = pd.DataFrame.from_dict(site_values['values'])
        #Parse the datetime values to Pandas Timestamp objects
        values_df['datetime'] = pd.to_datetime(values_df['datetime'], 
                                                   utc=True)
        #Convert values to float and replace -9999 nodata values with NaN
        values_df['value'] = pd.to_numeric(values_df['value']).replace(-9999, np.nan)
        #Remove any records flagged with lower quality
        values_df = values_df[values_df['quality_control_level_code'] == '1']
    # Try/Excepts that don't specify what kind of error they're expecting cause
    # me physical pain
    except:
        print("Unable to fetch %s" % VARIABLE_CODE)
    # As written this function can return None
    return values_df


def get_snotel_data(start_date: str,
                    end_date: str, 
                    verbose: bool=False):
    """ Input:
            start_date:
            end_date:
            verbose: bool -
        Output:

    """
    data_raw=pd.DataFrame()
    siteNamesList=[]
    siteNamesListCode=[]
    sites = ulmo.cuahsi.wof.get_sites(WSDLURL)
    sites_df = pd.DataFrame.from_dict(sites, orient='index').dropna()
    sites_df=sites_df.reset_index()

    for row in SITE_CODES:
        if verbose:
            print(row)
        values_df = snotel_fetch(row, VARIABLE_CODE, start_date, end_date)
        temp=values_df[['datetime','value']].copy()
        name=sites_df['name'][sites_df['index']==row].iloc[0]
        temp['Site']=name
        
        data_raw=pd.concat([data_raw,temp])
        siteNamesList.append(name)
        siteNamesListCode.append([name,row])
            
    data_raw.rename({'datetime': 'Date', 'value': 'SWE_in', 'name':'Site'}, axis=1, inplace=True)

    with open ("siteNamesList.txt","w") as output:
        output.write(str(siteNamesList))

    siteNamesListCode=pd.DataFrame(siteNamesListCode)
    siteNamesListCode.to_csv('siteNamesListCode.csv',index=False)

    data_raw.to_csv("SNOTEL_data_raw.csv.gz",index=False)

def convert_weather_data(verbose: bool=False):
    """ Input:
            verbose: bool - whether we should print to stdout 
        Output:

    """
    wd=os.getcwd()
    path=os.path.join(wd,"Weather_Data") #put all DW files in one directory with nothing else
    weather_files = os.listdir(path)

    weather=pd.DataFrame()
    for file_name in weather_files:
        file=pd.read_excel(os.path.join(path, file_name))
        # This might break - add test later
        file['site']=file_name[:2]
        weather=pd.concat([weather,file])
        
    weather.to_csv("DW_weather.csv.gz",index=False)

def main(args: argparse.Namespace):
    """ Input:
            args: populated namespace from Argument.Parser.parse_args()
        Output:    
    """
    # If you're going to specify these like this, why not just use a string?
    startY=1950
    startM=10
    startD=1
    start_date = "%s-%s-0%s"%(startY,startM,startD) #if start day is single digit, add leading 0
    end_date = datetime.now().strftime('%Y-%m-%d')

    verbose = args.verbose
    if args.snotel:
        get_snotel_data(start_date, end_date, verbose)
    if args.weather:
        convert_weather_data(verbose)

    #import and store site data for ALL Snotel Sites



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', 
                        '--snotel', 
                        action='store_true',
                        help='download the SNOTEL data')
    parser.add_arguments('-w', 
                        '--weather', 
                        action='store_true',
                        help='read the weather data from excel docs stored in dropbox.')
    parser.add_arguments('-v', 
                        '--verbose', 
                        action='store_true',
                        help='print a bunch of stuff to stdout - useful for debugging')
    args = parser.parse_args()
    main(args)
