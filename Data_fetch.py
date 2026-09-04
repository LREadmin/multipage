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
import requests
from utils import error_logger

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
        'SMS:-2',
        'SMS:-4',
        'SMS:-8',
        'SMS:-20',
        'SMS:-40'
    ]
    param_str = ','.join(param_list)

    df_list = []
    for site_code in site_codes:
        print(f'Beginning site: {site_code}')
        df_list.append(soil_moisture_for_site(site_code, param_str))
        time.sleep(1)
    df = pd.concat(df_list)
    df.to_csv("SNOTEL_SMS.csv.gz", index_label='Date')
    return df

def api_data_to_df(data_list):
    df_list = []
    depth_to_param = {
        -2: 'minus_2inch_pct',
        -4: 'minus_4inch_pct',
        -8: 'minus_8inch_pct',
        -20: 'minus_20inch_pct',
        -40: 'minus_40inch_pct'
    }
    # the reason for this whole hullabaloo is that the API stopped returning
    # empty columns - so if there's no -4 inch data for a site, for example,
    # we just don't get that column at all even though we specifically request
    # it. So we make an empty dataframe as a template
    template = pd.DataFrame(columns=list(depth_to_param.values()))
    for d in data_list:
        param_info = d['stationElement']
        depth = param_info['heightDepth']
        param = depth_to_param[depth]
        values = d['values']
        temp = pd.DataFrame([(i['date'], i.get('value', np.nan)) for i in values])
        temp.columns = ['Date', param]
        temp = temp.set_index('Date')
        df_list.append(temp)
    df = pd.concat(df_list, axis=1)
    # this will return the data we got from the API, along with empty
    # columns (in the right places) for the data we didn't get from the API
    return pd.concat((template, df))

def req_data_for_site(site_code, param_str, begin_date=-3):
    # por_start_dict = {}
    # por_start = por_start_dict[site_code]
    base_url = 'https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data?'
    url_params = '&'.join(
        [
            f'stationTriplets={site_code}',
            f'elements={param_str}',
            'duration=DAILY',
            f'beginDate={begin_date}'
        ]
    )
    url = base_url + url_params
    req = requests.get(url, timeout=5)
    req.raise_for_status()
    return req.json()

def get_por_start(site_codes, param_str):
    por_dict = dict()
    for site_code in site_codes:
        d = req_data_for_site(site_code, param_str)
        start = min([i['stationElement']['beginDate'] for i in d[0]['data']])
        por_dict[site_code] = start
    return por_dict

def soil_moisture_for_site(site_code, param_str):
    """ Gets all the available soil moisture data for a site
    """
    # Yeah, this is a gross hardcoded dictionary of POR start times.
    # It's generated by the "get_por_start" function, but it doesn't change,
    # so it seems wasteful to run it every time
    por_start_dict = {
        '335:CO:SNTL': '2002-07-03 14:00',
        '938:CO:SNTL': '2005-09-21 07:00',
        '415:CO:SNTL': '2013-08-27 00:00',
        '485:CO:SNTL': '2010-06-15 08:00',
        '505:CO:SNTL': '2007-12-05 10:00',
        '1187:CO:SNTL': '2015-09-24 10:00',
        '531:CO:SNTL': '2005-09-21 07:00',
        '935:CO:SNTL': '2005-09-21 07:00',
        '970:CO:SNTL': '2016-03-17 07:00',
        '937:CO:SNTL': '2005-10-20 08:00',
        '1014:CO:SNTL': '2005-11-01 12:00',
        '939:CO:SNTL': '2005-10-21 11:00'
    }
    por_start = por_start_dict[site_code]
    base_url = 'https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data?'
    url_params = '&'.join(
        [
            f'stationTriplets={site_code}',
            f'elements={param_str}',
            'duration=DAILY',
            f'beginDate={por_start}'
        ]
    )
    url = base_url + url_params
    req = requests.get(url, timeout=5)
    req.raise_for_status()
    json_data = json.loads(req.text)
    data_list = json_data[0]['data']
    df = api_data_to_df(data_list)
    # replace values greater than 100% with NAN
    df = df.map(lambda x: np.nan if x > 100 else x)
    df['site'] = site_code
    return df

@error_logger(channel_name='denver-water')
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
