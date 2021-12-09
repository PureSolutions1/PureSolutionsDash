import os
from os import listdir
from os.path import isfile, join, splitext
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import pandas as pd
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

def get_multiple_csv_from_folder(folder_path: str):
    onlyfiles = [f for f in listdir(folder_path) if (isfile(join(folder_path, f))\
        and splitext(f)[1]=='.csv')]
        
    print(f'FILES: {onlyfiles}')
    return onlyfiles

def import_csv(append_df: pd.DataFrame, folder_path: str, file_name: str):
    df = pd.DataFrame(pd.read_csv(f'{folder_path}/{file_name}'))
    date = f"{file_name.split('_')[1].split('.')[0][:2]}/{file_name.split('_')[1].split('.')[0][2:]}"
    df['Date'] = pd.to_datetime(f"{date}/2021", format='%m/%d/%Y')
    df = df.loc[~(df['StartTime']==0) & ~(df['EndTime']==0)]
    return df[['EmployeeName', 'Date', 'StartTime', 'EndTime', 'Address']]

def get_next_address(df, row):
    global count
    count += 1
    services = df.loc[
        (df['EmployeeName']==row['EmployeeName']) & 
        (df['Date']==row['Date']) & 
        (pd.to_datetime(df['StartTime'], format='%H%M')>row['StartTime'])
    ]
    if services.empty:
        print_state = 'LastService'
        out =  None
    else:
        try:
            print_state = str(services['Address'].loc[services['StartTime'] == services['StartTime'].min()].iloc[0])
            out =  str(services['Address'].loc[services['StartTime'] == services['StartTime'].min()].iloc[0])
        except:
            print_state = 'Fail'
            out =  None
    print(f'''{print_state} ::: {count} / {len(df)}''')
    return out

'''
csv_current = pd.read_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/services_with_addresses.csv')
df_current = pd.DataFrame(csv_current)
for i in df_current.columns:
    if 'Unnamed:' in i:
        df_current = df_current.drop(columns=[i])

df_current['Date'] = pd.to_datetime(df_current['Date'], format='%Y-%m-%d')
df_current['StartTime'] = pd.to_datetime(df_current['StartTime'], format='%Y-%m-%d %H:%M:%S')
df_current['EndTime'] = pd.to_datetime(df_current['EndTime'], format='%Y-%m-%d %H:%M:%S')
'''

file_names = get_multiple_csv_from_folder(
    '/data/dirty/tech_recap/daily_recaps'
)

df_daily_times = pd.DataFrame(columns=['EmployeeName', 'StartTime', 'EndTime', 'Date', 'Address'])
for i in file_names:
    df_daily_times = pd.concat([
        df_daily_times,
        import_csv(df_daily_times, '/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/daily_recaps', i)
    ])

df_daily_times = df_daily_times.loc[df_daily_times['EmployeeName'].isin(tick_employees)]
df_daily_times['StartTime'] = pd.to_datetime(df_daily_times['StartTime'], format='%H%M')
df_daily_times['EndTime'] = pd.to_datetime(df_daily_times['EndTime'], format='%H%M')
df_daily_times['Date'] = pd.to_datetime(df_daily_times['Date'], format='%Y-%m-%d')

'''
df = pd.concat([df_daily_times, df_current])
df = df.drop_duplicates(subset=['EmployeeName', 'StartTime', 'EndTime', 'Date'], keep=False)
'''

pandarallel.initialize()
df_daily_times['NextAddress'] = df_daily_times.parallel_apply(lambda row: get_next_address(df_daily_times, row), axis=1)
#df_out = pd.concat([df_current, df]).drop_duplicates()

df_daily_times.to_csv('/Users/fabian_coll/Desktop/Pure-Solutions/data/dirty/tech_recap/services_with_addresses.csv')
print(df_daily_times)
