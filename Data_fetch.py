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
import time
import argparse
from datetime import datetime
import json
import ulmo
import pandas as pd
import numpy as np

### Global Variables ###
# not necessarily good practice, but these might be updated in the future, and 
# I'd rather have them be highly visible than buried in the code.
WSDLURL='https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL'
VARIABLE_CODE='SNOTEL:WTEQ_D'
START_DATE='1950-10-01'
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
                 end_date: str,
                 verbose: bool=False) -> pd.DataFrame:
    """ Input:
            site_code: str - the site code we want to pull data for
            end_date: str - the latest date we want to pull data for
            verbose: bool - whether we should print information to stdout 
        Output:
            values_df: pd.DataFrame - the 
    """
    if verbose:
        print(site_code, VARIABLE_CODE, START_DATE, end_date)
    try:
        # Request data from the server
        site_values = ulmo.cuahsi.wof.get_values(WSDLURL,
                                                 site_code,
                                                 VARIABLE_CODE,
                                                 start=START_DATE,
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
        # As written this function can return None
        return values_df
    # Try/Excepts that don't specify what kind of error they're expecting cause
    # me physical pain
    except Exception as e:
        print(f"Unable to fetch site_code: {site_code}")
        raise e

def get_snotel_data(end_date: str, 
                    verbose: bool=False):
    """ Input:
            end_date: str - the latest date we want to pull data for
            verbose: bool - whether we should print information to stdout 
        Output:
            Writes data_raw to a compressed csv file. The columns are the date
            of the observation, the SWE in inches, and the name of the site. 
    """
    data_raw=pd.DataFrame()
    sites = ulmo.cuahsi.wof.get_sites(WSDLURL)
    sites_df = pd.DataFrame.from_dict(sites, orient='index').dropna()
    sites_df=sites_df.reset_index()

    for site_code in SITE_CODES:
        if verbose:
            print(site_code)
        values_df = snotel_fetch(site_code, end_date)
        temp=values_df[['datetime','value']].copy()
        name=sites_df['name'][sites_df['index']==site_code].iloc[0]
        temp['Site']=name
        data_raw=pd.concat([data_raw,temp])
        time.sleep(1)
    data_raw.rename({'datetime': 'Date', 'value': 'SWE_in', 'name':'Site'}, axis=1, inplace=True)

    data_raw.to_csv("SNOTEL_data_raw.csv.gz",index=False)

def get_weather_data(verbose: bool=False):
    """ Input:
            verbose: bool - whether we should print to stdout 
        Output:
            writes DW_weather to a compressed csv file. The columns mirror those
            in the excel files, but they are concatenated into one csv and 
            the site name (2 letter abbreviation) is added as a column named 
            "site"
    """
    # Fail loudly and informatively if file is missing
    try:
        with open('dropbox_url_list.json','r', encoding='utf-8') as f:
            url_dict = json.load(f)
    except FileNotFoundError as e:
        print('The file "dropbox_url_list.json" is missing!')
        raise e
    # Proceed if file is present
    if verbose:
        print(f'Preparing to download {len(url_dict)} files from dropbox...')

    # Download each excel in dropbox_url_list, concatenate them, and save as
    # compressed csv
    weather = pd.DataFrame()
    for site_id, url in url_dict.items():
        if verbose:
            print(f'site_id: {site_id}, url: {url}')
        # df = pd.read_excel(url)
        df = pd.read_csv(url)
        df['site'] = site_id
        weather=pd.concat([weather, df])
        time.sleep(.5)
    weather.to_csv("DW_weather.csv.gz",index=False)

def get_soil_moisture_data():
    """ Retrieves the soil moisture data for the sites.
    """
    print('Retrieving soil moisture data...')
    site_names = pd.read_csv("siteNamesListCode.csv")
    site_names = site_names[
        ~site_names['0'].str.contains("Buffalo Park|Echo Lake|Fool Creek")]
    site_codes = site_names.iloc[:,1]
    site_codes = site_codes.str.replace('SNOTEL:','')
    site_codes = site_codes.str.replace('_',':')
    # This was a gross thing that had a lot of moving parts earlier.
    # It was a data frame, then some other junk - gross.
    # The values were hardcoded, they were just pretending to be dynamic
    # before, so we're going to just add a hardcoded list and replace the
    # extra complexity.
    param_list = [
        'SMS:-2:value',
        'SMS:-4:value',
        'SMS:-8:value',
        'SMS:-20:value',
        'SMS:-40:value'
    ]
    param_str = ','.join(param_list)

    df_list = []
    for site_code in site_codes:
        print(f'Beginning site: {site_code}')
        df_list.append(get_soil_moisture_for_site(site_code, param_str))
        time.sleep(1)
    df = pd.concat(df_list)
    df.to_csv("SNOTEL_SMS.csv.gz",index=False)
    return df

def get_soil_moisture_for_site(site_code, param_str):
    """ Input:
            site_code: str - something like "1014:CO:SNTL"
            param_str: str - a comma separated list of the values we want
                to request from the API
        Output:
            returns a dataframe with columns for Date, soil moisture percent
            at various depths, and the site code.
    """
    url = '/'.join(
        [
            'https://wcc.sc.egov.usda.gov',
            'reportGenerator',
            'view_csv',
            'customMultiTimeSeriesGroupByStationReport',
            'daily',
            'start_of_period',
            f'{site_code}%7Cid=%22%22%7Cname',
            'POR_BEGIN,POR_END',
            param_str,
        ]
    )
    url = url + '?fitToScreen=false'
    df = pd.read_csv(url, comment='#')
    # Filters out data where the value is > 100%
    df.iloc[:,1:] = df.iloc[:,1:].map(lambda x: np.nan if x > 100 else x)
    df.columns = [
        'Date',
        'minus_2inch_pct',
        'minus_4inch_pct',
        'minus_8inch_pct',
        'minus_20inch_pct',
        'minus_40inch_pct'
    ]
    df['site'] = site_code
    return df

def main(args: argparse.Namespace):
    """ Input:
            args: populated namespace from Argument.Parser.parse_args()
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    verbose = args.verbose
    if args.snotel:
        get_snotel_data(end_date, verbose)
    if args.weather:
        get_weather_data(verbose)
    if args.soil_moisture:
        get_soil_moisture_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--snotel', 
                        action='store_true',
                        help='download the SNOTEL data')
    parser.add_argument('-w',
                        '--weather', 
                        action='store_true',
                        help='read the weather data from excel docs stored in dropbox.')
    parser.add_argument('-m',
                        '--soil-moisture', 
                        action='store_true',
                        help='get soil moisture data from the USDA api.')
    parser.add_argument('-v',
                        '--verbose', 
                        action='store_true',
                        help='print a bunch of stuff to stdout - useful for debugging')
    args = parser.parse_args()
    main(args)
