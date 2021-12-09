import pandas as pd
import numpy as np
import datetime
from data.programs import TM_list

def get_month(date):
    return date.strftime('%m %B')

def find_multi_services(row):
    if len(row['DoneDateFormatted']) > 1:
        return 1
    else:
        return 0

def agg_func(x):
    try: 
        return pd.Series.unique(x)
    except ValueError:
        print(x)
        return None

def get_time_inbetween(row):
    lst = []
    for i in range(1, len(row['DoneDateFormatted'])):
        diff = row['DoneDateFormatted'][i] - row['DoneDateFormatted'][i-1]
        lst.append(diff)
    average_time = sum(lst, datetime.timedelta(0)) / len(lst)
    average_time = average_time / np.timedelta64(1, 'D') # Convert to numeric type
    return average_time
    

csv = pd.read_csv('data/clean/revenue/clean_revenue.csv')
df = pd.DataFrame(csv)

tick_codes = list(TM_list.keys())

df = df[['Address', 'DoneDateFormatted', 'ProgramCode', 'DoneDateYear']]
df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%Y/%m/%d')
df['DoneDateMonth'] = df.apply(lambda row: get_month(row['DoneDateFormatted']), axis=1)

df = df.loc[(df['DoneDateYear'] == 2021) & (df['ProgramCode'].isin(tick_codes))]
df = df[['Address', 'ProgramCode', 'DoneDateFormatted', 'DoneDateMonth']]

df = df.groupby(['Address', 'ProgramCode', 'DoneDateMonth']).agg(set)

df['Multi'] = df.apply(lambda row: find_multi_services(row), axis=1)
df = df.loc[df['Multi'] > 0].drop(columns=['Multi'])
df['DoneDateFormatted'] = df.apply(lambda row: sorted(row['DoneDateFormatted']), axis=1)

print(df)
df['DaysBetween'] = df.apply(lambda row: get_time_inbetween(row), axis=1)
#print(df['DaysBetween'])

'''
df = df.reset_index().groupby(['ProgramCode', 'DoneDateMonth']).agg(['nunique', 'mean', 'median', 'max'])

print(df.sort_index())
df.to_excel('/Users/fabian_coll/Desktop/2021_services_by_month.xlsx')
print(df['DaysBetween'])
'''