import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from scipy import stats


TM_list = {
    'AD': 'Add-On Deer Control',
    'ANT': 'Ant Granular Application',
    'BC': 'Custom Tick & Mosquito',
    'BCO': 'Commercial Service',
    'BD': 'Bundled Deer Service',
    'BET': 'Beetle Control', 
    'BTI': 'Routine Bti Treatment', 
    'B14': '14-Day Mosquito & Tick', 
    'B21': '21-Day Mosquito & Tick', 
    'B28': '28-Day Mosquito & Tick', 
    'D': 'Deer Repellent Service',
    'ES': 'Event Treatment',
    'MC': 'Custome Routine Mosquito',
    'MMM': 'Mosquito Magnet Maintenance',
    'M14': '14-Day Routine Mosquito',
    'M21': '21-Day Routine Mosquito',
    'M28': '28-Day Routine Mosquito',
    'MVB': 'MV Mosquito & Tick',
    'MVD': 'Island Routine Deer Treatment',
    'MVM': 'Routine Mosquito Program',
    'MVT': 'MV Tick Control',
    'NMM': 'New Mosquito Magnet Machine',   
    'ORT': 'Residual Treatment: M&T',
    'R': 'Routine Rabbit Deterrent',
    'RTB': 'Residual Treatment: M&T',
    'RTM': 'Residual Treatment: Mosquito',
    'RTT': 'Residual Treatment: Tick',
    'SCP': 'Pest Service Call',
    'SWP': 'Pest Sales Walkthrough',
    'TC': 'Custome Routine Tick',
    'TF': 'Tick Flagging Service',
    'T14': '14-Day Routine Tick',
    'T21': '21-Day Routine Tick',
    'T28': '28-Day Routine Tick',
    'WT': 'Winter Tick Service'
}

OTC_with_addons = {
    'OTC': 'Organic Turf Care (Full)',
    'CA': 'Core Aeration',
    'DWC': 'Granular Crabgrass/Broadleaf', 
    'DWM': 'Driveway/Walkway Weed Management', 
    'GM': 'Grub and Insect Application',
    'LAG': 'Limestone Granular',
    'LR': 'Lawn Renovation',
    'LR1': 'Lawn Renovation: Prep',
    'LR2': 'Lawn Renovation: Install',
    'LR3': 'Lawn Renovation: Finish Work',
    'MS': 'Mechanical Seeding',
    'OS': 'Over-Seeding Application',
    'PRE': 'Organic Weed Pre-Emergent',
    'SCT': 'Turf Care Service Call',
    'SWT': 'Turf Sales Walkthrough',
    'ST': 'Soil Test',
    'TD': 'Organic Top Dressing',
    'TWC': 'Plant Based Weed Control',
    'TSL': 'Top Soil/Loam',
    'WM': 'Weed Management',
    'VOL': 'Vole Repellent Service',
    'YNG': 'Yard Granular Treatment',
    'FZ1': 'Organic Fertilizer: Round 1',
    'FZ2': 'Organic Fertilizer: Round 2',
    'FZ3': 'Organic Fertilizer: Round 3',
    'FZ4': 'Organic Fertilizer: Round 4',
    'FZ5': 'Organic Fertilizer: Round 5',
}

days_of_week = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def get_day_name(row):
    return days_of_week[row['DayOfWeekNum']]

def confidence_interval(series: pd.Series, conf_level: float):
    mean, sigma = series.mean(), series.std()
    interval = list(stats.norm.interval(conf_level, loc=mean, scale=sigma))
    if interval[0] < 0:
        interval[0] = 0
    return interval

def make_dataframe(df_rev_all: pd.DataFrame, rev_dataframes: dict, df_weather: pd.DataFrame):
    df = pd.concat([df_weather, df_rev_all], axis=1)
    for key in rev_dataframes.keys():
        df = pd.concat([df, rev_dataframes[key][f'{key.capitalize()}Rev']], axis=1)
    df = df.replace(np.nan, 0)
    df['DayOfWeekNum'] = df.index.weekday # Returns day of week as an integer (0 = Monday, 6 = Sunday)
    df['DayOfWeekName'] = df.apply(lambda row: get_day_name(row), axis=1) # Get name of day of week
    return df

def combine_dataframes(rev_dataframes: list, df_weather: pd.DataFrame):
    return [pd.concat([df_weather, i['GrossSalesAmount']], axis=1) for i in rev_dataframes]



csv1 = pd.read_csv('data\\clean\\weather\\weather_data.csv')
csv2 = pd.read_csv('data\\clean\\revenue\\clean_revenue.csv')

df_weather = pd.DataFrame(csv1)
df_rev = pd.DataFrame(csv2)

# Clean Weather DataFrame
df_weather = df_weather.rename(columns={'Date': 'DoneDateFormatted'})
df_weather['DoneDateFormatted'] = df_weather.apply(
    lambda row: datetime.strptime(row['DoneDateFormatted'].split(' ')[0], '%m/%d/%y').strftime('%Y-%m-%d'), 
    axis=1
    )
df_weather['DoneDateFormatted'] = pd.to_datetime(df_weather['DoneDateFormatted'], format='%Y-%m-%d')
df_weather = df_weather.set_index(['DoneDateFormatted'])

# Clean Revenue DataFrame
df_rev['DoneDateFormatted'] = df_rev.apply(
    lambda row: datetime.strptime(row['DoneDateFormatted'].split(' ')[0], '%Y-%m-%d'), 
    axis=1
    )
df_rev['DoneDateFormatted'] = pd.to_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d')

# Make DataFrames for programs: Tick, Turf and All
df_rev_turf = df_rev.loc[(df_rev['DoneDateYear']==2021) & (df_rev['ProgramCode'].isin(OTC_with_addons.keys()))][['DoneDateFormatted', 'GrossSalesAmount']]
df_rev_turf = df_rev_turf.groupby(by=['DoneDateFormatted']).sum().rename(columns={'GrossSalesAmount': 'TurfRev'})

df_rev_tick = df_rev.loc[(df_rev['DoneDateYear']==2021) & (df_rev['ProgramCode'].isin(TM_list.keys()))][['DoneDateFormatted', 'GrossSalesAmount']]
df_rev_tick = df_rev_tick.groupby(by=['DoneDateFormatted']).sum().rename(columns={'GrossSalesAmount': 'TickRev'})

df_rev_all = df_rev.loc[(df_rev['DoneDateYear']==2021)][['DoneDateFormatted', 'GrossSalesAmount']]
df_rev_all = df_rev_all.groupby(by=['DoneDateFormatted']).sum().rename(columns={'GrossSalesAmount': 'AllRev'})


# Concatenate DataFrames
df_combine = make_dataframe(
    df_rev_all,
    {
        'Tick': df_rev_tick, 
        'Turf': df_rev_turf
    }, 
    df_weather
    )
df_combine = df_combine.loc[df_combine.index >= '2021-03-01']
print(df_combine)
'''
df_combine_tick = make_dataframe(df_rev_tick, df_weather)
df_combine_turf = make_dataframe(df_rev_turf, df_weather)
'''

# Save Data
df_combine.to_csv('data/clean/weather/rain_rev_21.csv')

# Observe Rain Days
'''
Filters:
    1. Days with rain
    2. Days with 0 revenue
    3. Days after February
    4. Weekdays
'''
mask = (df_combine['Precipitation'] > 0) &\
        (df_combine['AllRev'] == 0) &\
        (df_combine.index >= '2021-03-01') &\
        (df_combine['DayOfWeekNum'].isin(range(0, 5)))


fig = px.histogram(
    df_combine, 
    x='GrossSalesAmount', 
    marginal='box', 
    title='Distribution of Daily Revenue Totals'
)
#fig.show()

print(len(df_combine.loc[mask]) * np.median(df_combine['GrossSalesAmount']))

'''
ESTIMATED REVENUE LOST
*NOTE* Only accounts for days that had the following:
    1. A measurable amount of rain
    2. $0 revenue earned
    3. Were weekdays

T&M: 45000
OTC: 16000
'''