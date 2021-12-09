import os
from os import listdir
from os.path import isfile, join, splitext
import sys
import requests
import json
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pandas as pd
from pandarallel import pandarallel
from geopy.geocoders import OpenMapQuest
from datetime import datetime
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


def get_multiple_csv_from_folder(folder_path: str, current_df):
    onlyfiles = [f for f in listdir(folder_path) if (isfile(join(folder_path, f))\
        and splitext(f)[1]=='.csv')]
              #and pd.to_datetime(f"{f.split('_')[1].split('.')[0]}/2021", format='%m%d/%Y')\
                   #not in pd.to_datetime(current_df.index.levels[1], format='%Y-%m-%d').unique()]
        
    print(f'FILES: {onlyfiles}')
    return onlyfiles

def import_csv(append_df: pd.DataFrame, folder_path: str, file_name: str):
    df = pd.DataFrame(pd.read_csv(f'{folder_path}/{file_name}'))
    date = f"{file_name.split('_')[1].split('.')[0][:2]}/{file_name.split('_')[1].split('.')[0][2:]}"
    print(f"{date}/2021")
    df['Date'] = pd.to_datetime(f"{date}/2021", format='%m/%d/%Y')
    df = df.loc[~(df['StartTime']==0) & ~(df['EndTime']==0)]
    return df[['EmployeeName', 'Date', 'StartTime', 'Address']]

def get_time(row, start: bool):
    row_list = row['InOutTimeFormatted'].split(' ')
    row_list.remove('/')
    try:
        row_list = [row_list[0]+row_list[1].upper(), row_list[2]+row_list[3].upper()]
        if start:
            time = datetime.strptime(row_list[0], '%I:%M%p')
        else:
            time = datetime.strptime(row_list[1], '%I:%M%p')
        return time
    except:
        return None

def merge_columns(df, row):
    lst = []
    for i in df.columns:
        try:
            if i=='MilesToFirstService':
                pass
            else:
                lst.append(str(row[i]).replace(' ',''))
        except KeyError:
            pass
    return '_'.join(lst)

def find_appropriate_miles(df, row):
    try:
        return float(df['MilesToFirstService'].loc[df['Keyyyyy'] == row['Key']])
    except:
        return None

bad_count = 0
count = 0
#geolocator = Nominatim(user_agent='pure-solutions')
geolocator = OpenMapQuest(api_key='qdcSGA0YMU9EUWfrfFtQ08jAGNPRB63c')
def geocode(df, row, address, date):
    global count
    global bad_count
    dist = None
    routes = None
    #location_start = geolocator.geocode(address1)
    #location_end = geolocator.geocode(address2)
    url = 'https://maps.googleapis.com/maps/api/geocode/json'

    if (pd.isnull(row['MilesToFirstService']) or row['Date'] > datetime.strptime(date, '%Y-%m-%d')):
        location = geolocator.geocode(address)
        count+=1
        print('------------------------------------------------------------')
        if location is None:
            print('NONE')
            bad_count+=1
            print(f'''{(bad_count/count)*100:,.2f}% Bad''')
            pass
        else:
            params_start = {'address': f'{address}', 'key': 'AIzaSyCJYIfJRX4Z2BeOEKKjv8fj2f2EOyuUWQY'}
            r_start = requests.get(url, params=params_start)
            results = r_start.json()['results']
            location = results[0]['geometry']['location']
            try:
                if row['EmployeeName'] in cape_guys:
                    r = requests.get(
                        f"http://router.project-osrm.org/route/v1/car/{location['lng']},{location['lat']};-69.96357346008841,41.6955182350886?overview=false"""
                    )
                else:
                    r = requests.get(
                        f"http://router.project-osrm.org/route/v1/car/{location['lng']},{location['lat']};-71.31387091988164,42.36721418348649?overview=false"""
                    )
                routes = json.loads(r.content)
                dist = routes.get('routes')[0]['distance']*0.000621371
                if dist > 25:
                    print(f'''{row['Address']} ::: {row['EmployeeName']}''')
                print(dist)
                print(f'''{count} / {len(df.loc[df['MilesToFirstService'].isnull()])} COMPLETE''')
                return dist
            except:
                bad_count+=1
                print(f'''{(bad_count/count)*100:,.2f}% Bad''') 
                return None
        print(f'''{count} / {len(df.loc[(df['MilesToFirstService'].isnull()) | (df['Date'] > datetime.strptime('2021-10-19', '%Y-%m-%d'))])} COMPLETE''')
        print('-'*100)
    else:
        return row['MilesToFirstService']
    

csv2 = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/pure_dash/data/employee_hours/employee_hours.csv')
df_emp_hours = pd.DataFrame(csv2)
df_emp_hours = df_emp_hours.loc[df_emp_hours['MainGroupDescription'].isin(tick_employees)]
df_emp_hours['ClockInTime'] = df_emp_hours.apply(lambda row: get_time(row, start=True), axis=1)

print(df_emp_hours['MainGroupDescription'].unique())

csv3 = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/pure_dash/data/employee_hours/tick_first_services.csv')
df = pd.DataFrame(csv3)
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df['StartTimeFormatted'] = pd.to_datetime(df['StartTimeFormatted'], format='%Y-%m-%d %H:%M:%S')
df = df.drop(columns=['Unnamed: 0'])

file_names = get_multiple_csv_from_folder(
    '/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/daily_recaps',
    df
)

df_new = pd.DataFrame(columns=['EmployeeName', 'StartTime', 'Date', 'Address'])
for i in file_names:
    df_new = pd.concat([
        df_new,
        import_csv(df_new, '/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/daily_recaps', i)
    ])
df_new = df_new.rename(columns={'StartTime': 'StartTimeFormatted'})
df_new = df_new.loc[df_new['EmployeeName'].isin(tick_employees)]
df_new['Date'] = pd.to_datetime(df_new['Date'], format='%Y-%m-%d')
df_new['StartTimeFormatted'] = pd.to_datetime(df_new['StartTimeFormatted'], format='%H%M')


df_emp_hours = df_emp_hours[[
    'MainGroupDescription',
    'ReportDateFormatted',
    'ClockInTime'
]]

df_emp_hours = df_emp_hours.rename(columns={
    'MainGroupDescription': 'EmployeeName',
    'ReportDateFormatted': 'Date'
})
df_emp_hours['Date'] = pd.to_datetime(df_emp_hours['Date'], format='%m/%d/%Y')
df_emp_hours = df_emp_hours.loc[df_emp_hours['Date'].isin(df_new['Date'].unique())]

df_emp_hours = df_emp_hours.groupby(['EmployeeName', 'Date']).min()
df_new = df_new.groupby(by=['EmployeeName', 'Date']).min()


#### FIRST SERVICE ####
df_merge = df_emp_hours.join(df_new, how='outer')\
    .reset_index()\
        .drop_duplicates(subset=[
            'EmployeeName', 'Date'
        ])\
            .dropna(subset=['Address'])

df_merge = df_merge.loc[df_merge['EmployeeName'].isin(tick_employees)]
df = df.drop(columns=['HoursToFirstService', 'AverageSpeedToFirstService'])
df_merge = pd.merge(df_merge, df[['EmployeeName', 'Date', 'MilesToFirstService']], how='left', on=['EmployeeName', 'Date'])
print(df_merge[['Date', 'Address']].loc[df_merge['EmployeeName']=='Jeremy Lucyk'])
df_merge['Address'] = df_merge.apply(lambda row: clean_zip_code(row), axis = 1)


date = '2021-11-09'#input(f'Please enter split date (YYYY-MM-DD): ')
pandarallel.initialize()
df_merge['MilesToFirstService'] = df_merge.parallel_apply(lambda row: geocode(df_merge, row, row['Address'], date), axis=1)
df_merge['HoursToFirstService'] = df_merge.parallel_apply(lambda row: ((row['StartTimeFormatted'] - row['ClockInTime']).days*24) + ((row['StartTimeFormatted'] - row['ClockInTime']).seconds/3600)-(1/3), axis=1)
df_merge = df_merge.loc[(df_merge['HoursToFirstService'] > 0) & (df_merge['MilesToFirstService'] > 0)]
df_merge['AverageSpeedToFirstService'] = df_merge['MilesToFirstService'] / df_merge['HoursToFirstService']
df_merge = df_merge.loc[(df_merge['AverageSpeedToFirstService'] != 0) & (df_merge['AverageSpeedToFirstService'] <= 60)]

df_out_mean = df_merge.groupby(by=['EmployeeName']).mean()

df_out_mean.to_csv('/Users/fabian_coll/Desktop/Pure-Solutions/pure_dash/data/employee_hours/tick_first_services_mean.csv')
df_merge.to_csv('/Users/fabian_coll/Desktop/Pure-Solutions/pure_dash/data/employee_hours/tick_first_services.csv')
print(df_merge)
