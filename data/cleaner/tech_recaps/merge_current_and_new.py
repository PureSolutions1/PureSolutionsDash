import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pandas as pd

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

def find_appropriate_miles(df, row):
    try:
        return float(df['MilesToNextAddress'].loc[df['Keyyyyy'] == row['Key']])
    except:
        return None

def merge_columns(df, row):
    lst = []
    for i in df.columns:
        if i=='MilesToNextAddress':
            pass
        else:
            lst.append(str(row[i]).replace(' ',''))
    return '_'.join(lst)

csv_current = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/inbetween_services_dirty.csv')
df_current_all = pd.DataFrame(csv_current)
df_current_all = df_current_all.rename(columns={'StartTime': 'StartTimeFormatted', 'EndTime': 'EndTimeFormatted'})
df_current_all['StartTimeFormatted'] = pd.to_datetime(df_current_all['StartTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_current_all['StartTimeFormatted'] = pd.to_datetime(df_current_all['StartTimeFormatted'], format='%H:%M')
df_current_all['EndTimeFormatted'] = pd.to_datetime(df_current_all['EndTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_current_all['EndTimeFormatted'] = pd.to_datetime(df_current_all['EndTimeFormatted'], format='%H:%M')
df_current_all['Date'] = pd.to_datetime(df_current_all['Date'], format='%Y-%m-%d')
for i in df_current_all.columns:
    if 'Unnamed' in i:
        df_current_all = df_current_all.drop(columns=[i])

df_current = df_current_all.drop(columns=['MilesToNextAddress'])
df_current = df_current.rename(columns={'StartTime': 'StartTimeFormatted', 'EndTime': 'EndTimeFormatted'})
df_current['StartTimeFormatted'] = pd.to_datetime(df_current['StartTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_current['StartTimeFormatted'] = pd.to_datetime(df_current['StartTimeFormatted'], format='%H:%M')
df_current['EndTimeFormatted'] = pd.to_datetime(df_current['EndTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_current['EndTimeFormatted'] = pd.to_datetime(df_current['EndTimeFormatted'], format='%H:%M')
df_current['Date'] = pd.to_datetime(df_current['Date'], format='%Y-%m-%d')
for i in df_current.columns:
    if 'Unnamed' in i:
        df_current = df_current.drop(columns=[i])

csv_new = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/services_with_addresses.csv')
df_new = pd.DataFrame(csv_new)
df_new = df_new.rename(columns={'StartTime': 'StartTimeFormatted', 'EndTime': 'EndTimeFormatted'})
df_new['StartTimeFormatted'] = pd.to_datetime(df_new['StartTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_new['StartTimeFormatted'] = pd.to_datetime(df_new['StartTimeFormatted'], format='%H:%M')
df_new['EndTimeFormatted'] = pd.to_datetime(df_new['EndTimeFormatted'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%H:%M')
df_new['EndTimeFormatted'] = pd.to_datetime(df_new['EndTimeFormatted'], format='%H:%M')
df_new['Date'] = pd.to_datetime(df_new['Date'], format='%Y-%m-%d')
for i in df_new.columns:
    if 'Unnamed' in i:
        df_new = df_new.drop(columns=[i])

df_concat = pd.concat([df_new, df_current])
df_concat = df_concat.drop_duplicates(subset=['EmployeeName', 'StartTimeFormatted', 'EndTimeFormatted', 'Date', 'Address'], keep='first')

print(df_concat.columns)
print(df_current_all.columns)

df_concat['Key'] = df_concat.apply(lambda row: merge_columns(df_concat, row), axis=1)
df_current_all['Keyyyyy'] = df_concat.apply(lambda row: merge_columns(df_current_all, row), axis=1)

#df_concat = df_concat.set_index(['EmployeeName', 'StartTimeFormatted', 'EndTimeFormatted', 'Date', 'Address'])
#df_current_all = df_current_all.set_index(['EmployeeName', 'StartTimeFormatted', 'EndTimeFormatted', 'Date', 'Address'])
'''
print(df_current_all['MilesToNextAddress'])
print('-'*100)
print(df_concat['Key'])
print('-'*100)
'''

df_concat['MilesToNextAddress'] = df_concat.apply(lambda row: find_appropriate_miles(df_current_all, row), axis=1)
df_concat = df_concat.drop(columns=['Key'])
print(df_concat)
df_concat.to_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/test.csv')
