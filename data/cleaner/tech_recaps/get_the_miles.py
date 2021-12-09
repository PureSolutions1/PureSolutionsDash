import os
import sys
import requests
import json
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pandas as pd
import numpy as np
from geopy.geocoders import OpenMapQuest
from datetime import datetime
from pandarallel import pandarallel
count = 0
bad_count = 0

tick_employees = [
    'Francisco Nieves',
    'Jose Rosado',
    'Brendon Deveaux',
    'Eduardo Cortez',
    'Seamus O\'connell',
    'Ryan Fratus',
    'Jamir Alexander',
    'Ryan Fleet',
    'John Moudarri',
    'Kevin Enriques-Uluan',
    'Daniel Cook',
    'Marcus Harrington',
    'Jeremy Lucyk',
    'Mohamed Aljundi',
    'Luis Alberto Pena',
    'Christopher Polack',
    'Justin Deveaux',
    'Cameron Gaudette'
]

cape_guys = [
    'Daniel Cook',
    'Marcus Harrington',
    'Christopher Polack',
    'Jeremy Lucyk'
]

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

geolocator = OpenMapQuest(api_key='wF44sqHSGb9AnCYodekjAkGtBN4nUcb9')
def geocode_twoAddresses(df, row, address1, address2, date):
    global count
    global bad_count
    dist = None
    routes = None
    #location_start = geolocator.geocode(address1)
    #location_end = geolocator.geocode(address2)
    url = 'https://maps.googleapis.com/maps/api/geocode/json'

    if (row['Date'] > datetime.strptime(date, '%Y-%m-%d')): #or (pd.isnull(row['MilesToNextAddress'])):
        print('------------------------------------------------------------')
        print(row['Date'])
        count+=1
        params_start = {'address': f'{address1}', 'key': 'AIzaSyCJYIfJRX4Z2BeOEKKjv8fj2f2EOyuUWQY'}
        r_start = requests.get(url, params=params_start)
        results_start = r_start.json()['results']
        location_start = results_start[0]['geometry']['location']

        params_end = {'address': f'{address2}', 'key': 'AIzaSyCJYIfJRX4Z2BeOEKKjv8fj2f2EOyuUWQY'}
        r_end = requests.get(url, params=params_end)
        results_end = r_end.json()['results']
        location_end = results_end[0]['geometry']['location']
        try:
            if (address1 is None) or (address2 is None):
                print(f'''Start or End Location is None ::: {address1} ::: {address2}''')
                bad_count += 1
                dist = None
            else:
                try:
                    r = requests.get(
                        f"http://router.project-osrm.org/route/v1/car/{location_start['lng']},{location_start['lat']};{location_end['lng']},{location_end['lat']}?overview=false"""
                    )
                    routes = json.loads(r.content)
                    #dist = geodesic((location_start.latitude, location_start.longitude), (location_end.latitude, location_end.longitude)).miles
                    dist = routes.get('routes')[0]['distance']*0.000621371
                    #print(f\'''{dist:,.2f} ::: {count}/{len(df)}\''')
                    if dist >= 100:
                        dist = None
                        print(f'BIG WEIRD NUMBER. MAKE NO SENSE ::: {location_start} ::: {location_end}\n{type(address1)} ::: {type(address2)}')
                        bad_count += 1
                except Exception as e:
                    print(f'''Can\'t get routes ::: {address1} ::: {address2}''')
                    print(str(e))
                    bad_count += 1
        except:
            print(f'''Couldn't find Address ::: {address1} ::: {address2}''')
        print(f'Returned: {dist}')
        print(f'ENTRIES:')
        print(f'''\t Failed: {(bad_count/count)*100:,.2f}%''')
        print(f'''\t Processed: {count}/{len(df.loc[(df['Date'] > datetime.strptime(date, '%Y-%m-%d')) | (df['MilesToNextAddress'].isnull())])}''')
        print('------------------------------')
        return dist
    else:
        return row['MilesToNextAddress']

def time_to_next_service(df, row):
    try:
        leave_time = list(df['EndTimeFormatted'].loc[(df['NextAddress']==row['Address']) & (df['Date']==row['Date'])])[0]
        arrive_time = row['StartTimeFormatted']
        out = float(((arrive_time - leave_time).days*24) + ((arrive_time - leave_time).seconds/3600))
    except IndexError:
        print('------------------------------')
        print(f'''FAIL \n{row['Address']} ::: {row['NextAddress']} \n{row['Date']} ::: {row['MilesToNextAddress']}''')
        print('------------------------------')
        out = None
    return out

def clean_zip_code(row):
    address = row['Address'].split(', ')
    state_zip = address[-1]
    street_town = address[:-1]
    if ('VT' in state_zip) or ('NH' in state_zip):
        out = None
    else:
        zip = state_zip.split(' ')[1]
        state = state_zip.split(' ')[0]
        if '-' in zip:
            zip = zip.split('-')[0]
            state_zip = ' '.join((state, zip))
            out = ', '.join((', '.join(street_town), state_zip))
        else:
            out = row['Address']
    return out

csv = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/test.csv')
df_daily_times = pd.DataFrame(csv)
df_daily_times['Date'] = pd.to_datetime(df_daily_times['Date'], format='%Y-%m-%d')


print('Initialize Pandarallel')
pandarallel.initialize()

try:
    date = '2021-11-09'#input(f'Please enter split date (YYYY-MM-DD): ')
except:
    date = input(f'Please enter split date (YYYY-MM-DD): ')
print('Getting Miles to Next Services')
#df_daily_times['Address'] = df_daily_times.apply(lambda row: clean_zip_code(row), axis = 1)

df_daily_times['MilesToNextAddress'] = df_daily_times.parallel_apply(lambda row: geocode_twoAddresses(df_daily_times, row, row['Address'], row['NextAddress'], date), axis=1)
print('ADDRESSES COMPLETE')
df_daily_times = df_daily_times.rename(columns={'StartTime': 'StartTimeFormatted', 'EndTime': 'EndTimeFormatted'})

df_daily_times['StartTimeFormatted'] = pd.to_datetime(df_daily_times['StartTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_daily_times['StartTimeFormatted'] = pd.to_datetime(df_daily_times['StartTimeFormatted'], format='%H:%M')
df_daily_times['EndTimeFormatted'] = pd.to_datetime(df_daily_times['EndTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_daily_times['EndTimeFormatted'] = pd.to_datetime(df_daily_times['EndTimeFormatted'], format='%H:%M')
df_daily_times['TimeToNextService'] = df_daily_times.parallel_apply(lambda row: time_to_next_service(df_daily_times, row), axis=1)
df_daily_times['SpeedToNextService'] = df_daily_times['MilesToNextAddress'] / df_daily_times['TimeToNextService']
df_daily_times = df_daily_times.replace([np.inf, -np.inf], None)
df_daily_times = df_daily_times.loc[(df_daily_times['SpeedToNextService'] != 0) & (df_daily_times['SpeedToNextService'] <= 60)]
df_daily_times = df_daily_times.dropna()
for i in df_daily_times.columns:
    if 'Unnamed' in i:
        df_daily_times = df_daily_times.drop(columns=[i])

print(df_daily_times)
print('Saving')
df_daily_times.to_csv('/Users/fabian_coll/Desktop/Pure-Solutions/pure_dash/data/employee_hours/tick_inbetween_services.csv')