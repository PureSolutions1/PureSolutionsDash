import pandas as pd
import numpy as np
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import datetime as dt
from datetime import date
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from math import ceil
from dateutil.relativedelta import relativedelta
from data.products import products
from data.programs import Programs, TM_list, OTC_with_addons
from data.employee_lists import tick_employees, turf_employees


######################### CONSTANTS #########################
rate = None
max_rate = None
today = dt.datetime.today()
first_of_week = (dt.datetime.today() - dt.timedelta(days = dt.datetime.today().isoweekday() % 7)).day
currentMonth = dt.datetime.now().month
currentDay = dt.datetime.now().day
previous_month = (dt.datetime.now() - relativedelta(months=1)).strftime('%B')


######################### LISTS / DICTIONARIES #########################
colummns = {
    'Production': ['Avg. Acres/Hour', 'Avg. Value/Hour', 'Number of Services'],
    'Product Usage': ['AmountApplied', 'TreatedArea', 'Treatment/Area']
}

teams = {
    'South': ['Ariel Ortega', 'Brendon Deveaux', 'Eduardo Cortez', 'Fahad Rashid', 'John Moudarri', 'Jose Rosado', 'Richard Rich', 'Mohamed Aljundi'],
    'North': ['Seamus O\'connell', 'Marc Tisme', 'Ryan Fratus'],
    'Metro West': ['Francisco Nieves', 'Jamir Alexander', 'Ryan Fleet'],
    'Cape': ['Daniel Cook', 'Marcus Harrington', 'Jeremy Lucyk']
}

timezz = {
    'All-Time': [dt.date(2015,1,1), dt.date.today(), 'data/clean/product_usage/pu_allTime.csv'],
    'Current Year': [dt.date(2021,1,1), dt.date.today(), 'data/clean/product_usage/pu_yearly.csv'],
    'Current Month': [dt.date(2021,currentMonth,1), dt.date.today(), 'data/clean/product_usage/pu_monthly.csv'],
}
try:
    timezz['Current Week'] = [dt.date(2021,currentMonth,first_of_week), dt.date.today(), 'data/clean/product_usage/pu_weekly.csv']
except ValueError:
    timezz['Current Week'] = [dt.date(2021,currentMonth-1,first_of_week), dt.date.today(), 'data/clean/product_usage/pu_weekly.csv']


choices = {
    'Number of Customers': ['OLD: Num. of Customers', 'NEW: Num of Customers'],
    'Number of Cancels': ['OLD: Num. of Cancels', 'NEW: Num. of Cancels'],
    'Cancel Value': ['OLD: Cancel Value ($)', 'NEW: Cancel Value ($)'],
    'Cancels as a Percentage of Total Customers': ['OLD: Cancels as a Percentage of Total Customers', 'NEW: Cancels as a Percentage of Total Customers']
}

customer_growth_choices = {
    'Number of Customers': ['OLD: Num. of Customers', 'NEW: Num of Customers'],
    'Number of Cancels': ['OLD: Num. of Cancels', 'NEW: Num. of Cancels'],
    'Cancel Value': ['OLD: Cancel Value ($)', 'NEW: Cancel Value ($)'],
    'Cancels as a Percentage of Total Customers': ['OLD: Cancels as a Percentage of Total Customers', 'NEW: Cancels as a Percentage of Total Customers']
}

Goals = {
    '4.5 Million': '(4.5)',
    '4.9 Million': '(4.9)',
    '5.2 Million': '(5.2)'
}

stat_translations = {
    'Number Services': ['TeamServiceNumber', pd.Series.nunique],
    'Square Feet (000s)': ['Size', 'sum'],
    'Revenue': ['GrossSalesAmount', 'sum']
}

reverse_rank_metrics = [
    'Avg. Time/Service (Minutes)',
    'Number of Services Needing Respray',
    'Percent of Services Needing Respray',
    'DiffFromGoal',
    'Cost/Acre'
]

months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

vineyard_codes = ['MVB', 'MVM', 'MVT']

ferts = ['FZ1', 'FZ2', 'FZ3', 'FZ4', 'FZ5']

tick_composite_cols = [
    'Median Servicing Speed (Acres/Hour-on-Sight)',
    'Median Revenue/Hour of Servicing ($/Hour-on-Sight)',
    'TotalHours',
    'AverageRevenuePerDay',
    'Avg. Profit/Day'
]

turf_composite_cols = [
    'Avg. Servicing Speed (Acres/Hour-on-Sight)',
    'Avg. Revenue/Hour of Servicing ($/Hour-on-Sight)'
]

turf_products = {
    'AMP-xc': 14.38,
    'Axxe': 0,
    'Bioworks 7-0-7': 13.03,
    'Bioworks 2-0-20': 12.92,
    'Crabgrass Barrier': 0.98,
    'Grass Seed: Elite Mix': 27.04,
    'Grass Seed: RPR Ryegrass': 21.6,
    'Grub Gone': 49.20,
    'Neptunes Harvest 2-0-2': 1.89,
    'Neptunes Harvest 2-3-1': 1.25,
    'Purely Organic 10-0-2': 8.48,
    'Quantum Grow': 5.12,
    'Solu-Cal Lime': 4.96,
    'SlipStream Liquid Weed Control': 0,
    'Tenacity Granular': 17.60,
    'Weed Shield': 2.72
}

money_cols = [
    'TotalPrice',
    'GrossSalesAmount'
]

program_colors = {
    'FZ': '#fd3216',
    'OTC': '#e48f72',
    'CA': '#00fe35',
    'GM': '#6a76fc',
    'LAG': '#fe00ce',
    'MS': '#0df9ff',
    'OS': '#6e899c',
    'PRE': '#eea6fb',
    'ST': '#479b55',
    'TD': '#85660d',
    'TWC': '#ff9616',
    'WM': '#eeca3b'
}

######################### HTML/CSS #########################
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)


######################### DATA LOADING #########################
    # GENERAl
@st.cache(allow_output_mutation = True, suppress_st_warning=True)
def get_clean_data(path, low_memory = True):
    csv1 = pd.read_csv(path, low_memory = low_memory)
    df1 = pd.DataFrame(csv1)
    if 'data/clean/sales' in path:
        df1['SoldDateFormatted'] = pd.to_datetime(df1['SoldDateFormatted'], format='%m/%d/%Y')
        return df1
    elif 'data/clean/revenue' in path:
        df1['DoneDateFormatted'] = pd.to_datetime(df1['DoneDateFormatted'], format='%Y-%m-%d')
        return df1
    else:
        st.write('Weird data you\'re using there.')

@st.cache(allow_output_mutation = True)
def get_specific_month_data(path, month_num=1, low_memory=True):
    csv1 = pd.read_csv(path, low_memory = low_memory)
    df1 = pd.DataFrame(csv1)
    if 'data/clean/sales' in path:
        df1['SoldDateFormatted'] = pd.to_datetime(df1['SoldDateFormatted'], format='%m/%d/%Y')
        mask = (df1['SoldDateFormatted'].dt.month==month_num)
    elif 'data/clean/revenue' in path:
        df1['DoneDateFormatted'] = pd.to_datetime(df1['DoneDateFormatted'], format='%Y-%m-%d')
        mask = (df1['DoneDateFormatted'].dt.month==month_num)
    elif 'data/clean/cancels' in path:
        df1['FormattedCancelDate'] = pd.to_datetime(df1['FormattedCancelDate'], format='%m/%d/%Y')
        mask = (df1['FormattedCancelDate'].dt.month==month_num)
    return df1.loc[mask]

    # CUSTOMER GROWTH
@st.cache(allow_output_mutation = True)
def get_customer_growth_data(path, low_memory = True):
    csv1 = pd.read_csv(path, low_memory = low_memory)
    df1 = pd.DataFrame(csv1)
    df1 = df1.rename(columns={
        'CustomerCountOld': 'OLD: Num. of Customers',
        'NewCustomersCount': 'NEW: Num of Customers',
        'CurrentCustomerCount': 'CURRENT: Num. of Customers',
        'CancelCountOld': 'OLD: Num. of Cancels',
        'CancelCountNew': 'NEW: Num. of Cancels',
        'CancelDollarOld': 'OLD: Cancel Value ($)',
        'CancelDollarNew': 'NEW: Cancel Value ($)',
        'CancelPercentageOld': 'OLD: Cancels as a Percentage of Total Customers',
        'CancelPercentageNew': 'NEW: Cancels as a Percentage of Total Customers',
        'NewCustomersPrice': 'NEW: Customer Value ($)', 
        'GrowthPercentage': 'GROWTH: Num. of Customers (%)'
    })
    df1 = df1[[
        'MainGroupDescription',
        'OLD: Num. of Customers',
        'NEW: Num of Customers',
        'CURRENT: Num. of Customers',
        'OLD: Num. of Cancels',
        'NEW: Num. of Cancels',
        'OLD: Cancel Value ($)',
        'NEW: Cancel Value ($)',
        'OLD: Cancels as a Percentage of Total Customers',
        'NEW: Cancels as a Percentage of Total Customers',
        'NEW: Customer Value ($)',
        'GROWTH: Num. of Customers (%)',
    ]]
    return df1

######################### DATA MANIPULATION/CLEANING #########################

    # REVENUE/SALES
def get_yearly_stats(df, year, num_col, programs=[]):
    try:
        mask = (df['DoneDateFormatted'] >= pd.to_datetime(f'{year}/1/1', format='%Y/%m/%d')) & (df['DoneDateFormatted'] <= pd.to_datetime(f'{year}/12/31', format='%Y/%m/%d'))
    except KeyError:
        mask = (df['SoldDateFormatted'] >= pd.to_datetime(f'{year}/1/1', format='%Y/%m/%d')) & (df['SoldDateFormatted'] <= pd.to_datetime(f'{year}/12/31', format='%Y/%m/%d'))
    temp_df = df.loc[mask]
    temp_df.reset_index(inplace=True, drop=True)
    temp_df = temp_df.loc[df['ProgramCode'].isin(programs)]
    return np.sum(temp_df[num_col])

def get_yearly_revenueSales(df, year, programs=None, start_date_string=None, end_date_string=None):
    if end_date_string is None:
        today = date.today().strftime('%m/%d')
        start = '1/1'
    else:
        today = end_date_string
        start = start_date_string
    try:
        mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(f'{year}/{start}', format='%Y/%m/%d')) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= pd.to_datetime(f'{year}/{today}', format='%Y/%m/%d'))
        temp_df = df.loc[mask]
    except KeyError:
        try:
            mask = (df['SoldDateFormatted'] >= pd.to_datetime(f'{year}/{start}', format='%Y/%m/%d')) & (df['SoldDateFormatted'] <= pd.to_datetime(f'{year}/{today}', format='%Y/%m/%d'))
            temp_df = df.loc[mask]
        except KeyError:
            mask = (make_datetime(df['FormattedCancelDate'], format='%m/%d/%Y') >= pd.to_datetime(f'{start}/{year}', format='%m/%d/%Y')) & (make_datetime(df['FormattedCancelDate'], format='%m/%d/%Y') <= pd.to_datetime(f'{today}/{year}', format='%m/%d/%Y'))
            temp_df = df.loc[mask]
    if programs is None:
        pass
    else:
        try:
            temp_df = temp_df.loc[temp_df['ProgramCode'].isin(programs)]
        except KeyError:
            pass
    try:
        return np.sum(temp_df['GrossSalesAmount'])
    except KeyError:
        return np.sum(temp_df['TotalPrice'])

def get_year_end_results(df, start_year, end_year, other=None, start_date_string=None, end_date_string=None):
    if other is None:
        end_year_revs = {}
        for i in range(start_year, end_year):
            end_year_revs[i] = []
            end_year_revs[i].append(get_yearly_revenueSales(df, i, TM_list, start_date_string, end_date_string))
            end_year_revs[i].append(get_yearly_revenueSales(df, i, OTC_with_addons, start_date_string, end_date_string))
            end_year_revs[i].append(get_yearly_revenueSales(df, i, Programs, start_date_string, end_date_string))
    else:
        end_year_revs = other
    end_year_revs = pd.DataFrame.from_dict(
        end_year_revs, 
        orient='index',
        columns=['T&M', 'OTC', 'Total'],
        )
    end_year_revs['T&M Growth'] = end_year_revs['T&M'].pct_change()*100
    end_year_revs['OTC Growth'] = end_year_revs['OTC'].pct_change()*100
    end_year_revs['Total Growth'] = end_year_revs['Total'].pct_change()*100
    end_year_revs.sort_index(ascending=True)
    return end_year_revs

def get_monthly_revenueSales(df, month, year, programs=[]):
    last = last_day_of_month(dt.date(year, month, 4))
    try:
        mask = (df['DoneDateFormatted'] >= pd.to_datetime(f'{year}/{month}/1', format='%Y/%m/%d')) & (df['DoneDateFormatted'] <= pd.to_datetime(last, format='%Y/%m/%d'))
        temp_df = df.loc[mask]
    except KeyError:
        try:
            mask = (df['SoldDateFormatted'] >= pd.to_datetime(f'{year}/{month}/1', format='%Y/%m/%d')) & (df['SoldDateFormatted'] <= pd.to_datetime(last, format='%Y/%m/%d'))
            temp_df = df.loc[mask]
        except KeyError:
            mask = (make_datetime(df['FormattedCancelDate'], format='%m/%d/%Y') >= pd.to_datetime(f'{year}/{month}/1', format='%Y/%m/%d')) & (make_datetime(df['FormattedCancelDate'], format='%m/%d/%Y') <= pd.to_datetime(last, format='%Y/%m/%d'))
            temp_df = df.loc[mask]
    temp_df = temp_df.loc[temp_df['ProgramCode'].isin(programs)]
    try:
        return np.sum(temp_df['GrossSalesAmount'])
    except KeyError:
        return np.sum(temp_df['TotalPrice'])

def get_month_end_results(df, start_year, end_year):
    end_months_revs = {}
    for i in range(start_year, end_year):
        currentYear = int(date.today().year)
        currentMonth = int(date.today().month)
        if i == currentYear:
            for month in range(1, currentMonth+1):
                end_months_revs[f'{month}/{i}'] = []
                end_months_revs[f'{month}/{i}'].append(get_monthly_revenueSales(df, month, i, programs=TM_list))
                end_months_revs[f'{month}/{i}'].append(get_monthly_revenueSales(df, month, i, programs=OTC_with_addons))
        else:
            for month in range(1, 13):
                end_months_revs[f'{month}/{i}'] = []
                end_months_revs[f'{month}/{i}'].append(get_monthly_revenueSales(df, month, i, programs=TM_list))
                end_months_revs[f'{month}/{i}'].append(get_monthly_revenueSales(df, month, i, programs=OTC_with_addons))
    end_months_revs = pd.DataFrame.from_dict(
        end_months_revs, 
        orient='index',
        columns=['T&M', 'OTC'],
        )
    end_months_revs['Total'] = end_months_revs['T&M'] + end_months_revs['OTC']
    end_months_revs['T&M Growth'] = end_months_revs['T&M'].pct_change()*100
    end_months_revs['OTC Growth'] = end_months_revs['OTC'].pct_change()*100
    end_months_revs['Total Growth'] = end_months_revs['Total'].pct_change()*100
    pd.to_datetime(end_months_revs.index, format='%m/%Y')
    return end_months_revs

    # REVENUE
def adjust_vineyard_revenue(row):
    if row['ProgramCode'].upper() in vineyard_codes:
        return float(row['GrossSalesAmount']*0.8)
    else:
        return float(row['GrossSalesAmount'])

def get_revenue_by_programCode(row, code_df, code_col, rev_df, rev_col='GrossSalesAdjusted', rev_code_col='ProgramCode'):
    programCode = row[code_col]
    num_services_with_code = len(code_df.loc[code_df[code_col]==programCode])
    if programCode == 'FZ':
        programCode = ['FZ1', 'FZ2', 'FZ3', 'FZ4', 'FZ5']        
    if type(programCode)==list:
        return np.sum([rev_df[rev_col].loc[rev_df[rev_code_col]==i].sum() for i in programCode])/num_services_with_code
    else:
        return rev_df[rev_col].loc[rev_df[rev_code_col]==programCode].sum()/num_services_with_code


    # CANCELS
def clean_cancels(row):
    sheeee = row['ProgramTypeAndCode'].split(' ')
    return sheeee[1]

    # GENERAL
def filter_by_date(df: pd.DataFrame, start, end, date_col):
    mask = (df[date_col] >= start) & (df[date_col] <= end)
    return df.loc[mask]


def make_datetime(col, format='%Y/%m/%d'):
    return pd.to_datetime(col, format=format)

def make_rate_stats(row, name1, name2):
    try:
        global rate
        rate = row[name1] / row[name2]
    except ZeroDivisionError:
        pass
    return rate

def identify_program(row):
    if row['ProgramCode'] in TM_list:
        return 'TickMosquito'
    elif row['ProgramCode'] in OTC_with_addons:
        return 'OTC'
    else:
        return 'N/A'

def make_listCol(row, name):
    split = row[name].split(', ')
    return split

def fix_programCode(row):
    return row['MainGroupDescription'].split(' - ')[1]

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + dt.timedelta(days=4)
    return next_month - dt.timedelta(days=next_month.day)


######################### EMPLOYEES #########################
def get_team_avg(df, name, row):
    return np.nanmean(df[name].loc[df['Team'] == row['Team']])

def get_service_diff(row, name1, name2):
    try:
        return (row[name1] - row[name2]) / row[name2]
    except ZeroDivisionError:
        return None

def remove_bad_results(row):
    if row['size_per_hour'] > 0.15:
        pass
    else:
        return row['size_per_hour']

def week_number_year(row):
    return f'''{row['WeekNumber']}-{row['Year']}'''

def get_average(row, select_stats):
    lst = []
    [lst.append(row[f'{i} Rank']) for i in select_stats]
    return np.nanmean(lst)

def make_col_into_list(row, name):
    lst = []
    lst.append(row[name])
    return lst

def find_topDressing_days(row):
    if 'TD' in set(row['ProgramCode']):
        return 1
    else:
        return 0

def make_that_dictionary(row):
    dic = {}
    for i in range(len(row['ProgramCode'])):
        try:
            dic[row['ProgramCode'][i]] += 1
        except KeyError:
            dic[row['ProgramCode'][i]] = 1
    return dic

def clean_ferts(row):
    if row['ProgramCode'] in ferts:
        return 'FZ'
    else:
        
        return row['ProgramCode']
    

def get_dailyTech_stats(row, stat):
    dic = {}
    for val in set(row['ProgramCode']):
        indices = [i for i, x in enumerate(row['ProgramCode']) if x==val]
        
        for s in indices:
            try:
                dic[val] += row[stat][s]
            except KeyError:
                dic[val] = row[stat][s]
    return dic
    

def get_tick_employee_results(df, rev_col, start=None, end=None, time_frame=None, sort_by=None):
    if time_frame is None:
        mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    else:
        start=timezz[time_frame][0]
        end=timezz[time_frame][1]
        mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    df = df.loc[mask]
    results = {}
    for emp in tick_employees:
        results[emp] = []
        temp_df = df.loc[df['EmployeeName'] == emp]
        try:
            percentage = len(temp_df['NeedRespray'].loc[temp_df['NeedRespray']==1])/len(temp_df.index)
        except ZeroDivisionError:
            percentage = 0
        try:
            results[emp] = [
                list(temp_df['Team'].unique())[0],
                np.sum(temp_df[rev_col]),
                np.nanmedian(temp_df[rev_col]),
                np.nanmedian(temp_df['CustomerSize']),
                len(temp_df['CustomerSize'].loc[temp_df['CustomerSize'] <= 0.1]) / len(temp_df['CustomerSize']),
                np.nanmedian(temp_df['TotalManHours']),
                np.nanmedian(temp_df['size_per_hour']), 
                np.nanmedian(temp_df['value_per_hour']),
                len(temp_df['NeedRespray'].loc[temp_df['NeedRespray']==1]),
                len(temp_df.index),
                percentage
                ]
            emp_team = list(temp_df['Team'].unique())[0]
        except IndexError:
            pass
        
        try:
            ind_avg = len(temp_df['DoneDateFormatted']) / len(temp_df['DoneDateFormatted'].unique())
        except ZeroDivisionError:
            ind_avg = 0  
        try:
            dailyRev_avg = np.sum(temp_df['GrossSalesAmount']) / len(temp_df['DoneDateFormatted'].unique())
        except ZeroDivisionError:
            dailyRev_avg = 0
        #results[emp].append(ind_avg)
        #results[emp].append(dailyRev_avg)
    
    results = pd.DataFrame.from_dict(
        results, 
        orient='index', 
        columns=[
            'Team',
            'Total Revenue ($)',
            'Median Revenue/Service ($)', 
            'Median Property Size (Acres)',
            'Percentage of Properties Less Than 0.1 Acres', 
            'Median Time/Service (Minutes)', 
            'Median Servicing Speed (Acres/Hour-on-Sight)', 
            'Median Revenue/Hour of Servicing ($/Hour-on-Sight)',
            'Number of Services Needing Respray', 
            'Number of Services',
            'Percent of Services Needing Respray',
            #'Individual Avg. Services/Day',
            #'Individual Avg. Revenue/Day'
            ])
    #results['Team Avg. Services/Day'] = results.apply(lambda row: get_team_avg(results, 'Individual Avg. Services/Day', row), axis=1)
    #results['Team Avg. Revenue/Day'] = results.apply(lambda row: get_team_avg(results, 'Individual Avg. Revenue/Day', row), axis=1)
    #results['Difference in Avg. Services/Day from Team (%)'] = results.apply(lambda row: get_service_diff(row, 'Individual Avg. Services/Day', 'Team Avg. Services/Day'), axis=1)
    #results['Difference in Avg. Revenue/Day from Team (%)'] = results.apply(lambda row: get_service_diff(row, 'Individual Avg. Revenue/Day', 'Team Avg. Revenue/Day'), axis=1)
    return results


def get_employee_daily_programs(df, start, end, employee, choice=None, func=None):
    df = df[[
        'DoneDateFormatted',
        'ProgramCode',
        'EmployeeName',
        'Size',
        'GrossSalesAmount',
        'TeamServiceNumber'
    ]]
    df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%Y-%m-%d')
    mask = (df['DoneDateFormatted'] >= pd.to_datetime(start, format='%Y/%m/%d')) & (df['DoneDateFormatted'] <= pd.to_datetime(end, format='%Y/%m/%d'))
    df = df.loc[df['ProgramCode'].isin(OTC_with_addons.keys())]
    df = df.loc[mask]
    df['ProgramCodeAdjust'] = df.apply(lambda row: clean_ferts(row), axis=1)
    if employee=='All':
        pass
    else:
        df = df.loc[df['EmployeeName'] == employee]

    df_program_final = pd.DataFrame(index=df['DoneDateFormatted'].unique())
    programs = list(set(df['ProgramCodeAdjust']))
    if len(programs)==0:
        st.markdown(f'''**No Turf Service Data for {employee} over {start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')}**''')
    else:
        if 'TD' in programs:
            pass
        else:
            programs = programs+['TD']

        for key in stat_translations.keys():
            df_program_count = pd.DataFrame(index=df['DoneDateFormatted'].unique())
            for i in range(len(programs)):
                prog_df = df.loc[(df['ProgramCodeAdjust']==programs[i])]
                prog_df = prog_df[[
                    'DoneDateFormatted',
                    stat_translations[key][0]
                ]]
                prog_df = prog_df.groupby('DoneDateFormatted').agg(stat_translations[key][1])
                prog_df = prog_df.rename(columns={stat_translations[key][0]: f'''{programs[i]}_{''.join(key.split(' '))}'''})
                df_program_count = df_program_count.fillna(0)
                df_program_count = df_program_count.groupby(level=0).mean()
                df_program_count = df_program_count.join(prog_df, how='outer')

            df_program_count = df_program_count.fillna(0)
            df_program_count = df_program_count.groupby(level=0).mean()
            df_program_count[f'''All_{''.join(key.split(' '))}'''] = df_program_count.sum(axis=1)
            df_program_final = df_program_final.join(df_program_count, how='outer')

        df_program_final = df_program_final.groupby(level=0).mean()
        df_program_final = df_program_final.fillna(0)
    return df_program_final, programs

def make_property_size_histogram(df, start, end, emps=[], show_hist=True):
    mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    df = df.loc[mask]
    emp_data = []
    emp_labels = []
    fig2 = go.Figure()
    for i in emps:
        df_emp = df.loc[df['EmployeeName']==i]
        emp_data.append(df_emp['Size'])
        emp_labels.append(i)

        
        fig2.add_trace(go.Histogram(
            x=df_emp['Size'],
            name=i,
            xbins=dict(start=0, end=2, size=0.1),
            opacity=0.75
        ))
    
    fig2.update_layout(
        title_text=f'''Histogram for Property Sizes for T&M Technicians ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})''',
        xaxis_title_text='Property Size (Acres)',
        yaxis_title_text='Count'
    )
    
    fig = ff.create_distplot(emp_data, emp_labels, bin_size=0.1, show_hist=show_hist)
    fig.layout.update({'title': f'''Property Size Distributions for T&M Technicians ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})'''})
    st.plotly_chart(fig)
    if show_hist:
        st.plotly_chart(fig2)
    else:
        pass

def get_turf_employee_results(df, rev_col, start=None, end=None, time_frame=None, sort_by=None):
    if time_frame is None:
        mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    else:
        start=timezz[time_frame][0]
        end=timezz[time_frame][1]
        mask = (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    df = df.loc[mask]
    df = df[[   
        'EmployeeName', 'GrossSalesAmount', 'CustomerSize', 'TotalManHours', 'Size', 
        'GrossSalesAdjusted', 'size_per_hour', 'value_per_hour', 'IndividualServiceNumber'
    ]]
    df = df.groupby(['IndividualServiceNumber']).agg({
        'EmployeeName': pd.Series.mode,
        'GrossSalesAmount': pd.Series.sum,
        'CustomerSize': pd.Series.mean,
        'TotalManHours': pd.Series.mean,
        'Size': pd.Series.mean,
        'GrossSalesAdjusted': pd.Series.sum,
        'size_per_hour': pd.Series.mean,
        'value_per_hour': pd.Series.sum
    })
    df = df.reset_index()
    results = {}
    for emp in turf_employees:
        results[emp] = []
        temp_df = df.loc[df['EmployeeName'] == emp]
        results[emp] = [
            np.nanmedian(temp_df[rev_col]),
            np.nanmedian(temp_df['CustomerSize']),
            np.nanmedian(temp_df['TotalManHours']),
            np.nanmedian(temp_df['size_per_hour']), 
            np.nanmedian(temp_df['value_per_hour']),
            len(temp_df['IndividualServiceNumber'].unique())
            ]
    
    results = pd.DataFrame.from_dict(
        results, 
        orient='index', 
        columns=[
            'Avg. Revenue/Service ($)', 
            'Avg. Property Size (Acres)', 
            'Avg. Time/Service (Minutes)', 
            'Avg. Servicing Speed (Acres/Hour-on-Sight)', 
            'Avg. Revenue/Hour of Servicing ($/Hour-on-Sight)',
            'Number of Services',
            ])
    return results

def get_average_weekly_hours(df, start, end, group):
    today = dt.datetime.today()
    df['ReportDateFormatted'] = pd.to_datetime(df['ReportDateFormatted'], format='%m/%d/%Y')
    df['ReportDateFormatted'] = df['ReportDateFormatted'].apply(lambda x: x.strftime('%Y/%m/%d'))
    df['ReportDateFormatted'] = pd.to_datetime(df['ReportDateFormatted'], format='%Y/%m/%d')
    df['Year'] = df['ReportDateFormatted'].dt.year
    df['WeekNumber'] = df.apply(lambda row: week_number_year(row), axis=1)
    mask = (make_datetime(df['ReportDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df['ReportDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))

    df = df.loc[mask]
    df = df.loc[df['MainGroupDescription'].isin(group)]
    df = df.groupby(['MainGroupDescription', 'WeekNumber']).sum()
    df.reset_index(inplace=True)
    df = df[[
        'MainGroupDescription', 
        'WeekNumber', 
        'RegularMinutes', 
        'OvertimeMinutes', 
        'TotalMinutes'
        ]]
    df['RegularHours'] = df['RegularMinutes'] / 60
    df['OvertimeHours'] = df['OvertimeMinutes'] / 60
    df['TotalHours'] = df['TotalMinutes'] / 60
    df.rename(columns={'MainGroupDescription': 'TechnicianName'}, inplace=True)
    df = df.groupby(['TechnicianName']).agg({
        'WeekNumber': 'count', 
        'RegularMinutes': 'mean', 
        'OvertimeMinutes': 'mean', 
        'TotalMinutes': 'mean',
        'RegularHours': 'mean',
        'OvertimeHours': 'mean',
        'TotalHours': 'mean'
    })
    df.rename(columns={'WeekNumber': 'NumberWeeksWorked'}, inplace=True)
    return df[['NumberWeeksWorked', 'RegularHours', 'OvertimeHours', 'TotalHours']]

######################### PRODUCT USAGE #########################
def get_diff_from_target(row, lower, upper):
    if row['Treatment/Area'] > upper:
        return row['Treatment/Area'] - upper
    elif row['Treatment/Area'] < lower:
        return lower - row['Treatment/Area']
    else:
        return 0

def fix_product_code(row):
    return ''.join(row['ProductCode'].rstrip().lstrip())

def get_cost_per_acre(row):
    amount_tm = row['Treatment/Area']*0.046875
    return amount_tm*37

def get_product_cost(row):
    try:
        return (row['AmountApplied']*products[row['ProductCode']]['Cost']) / row['PropertySize']
    except:
        return None

def get_profit_per_service(row):
    return row['AverageRevenuePerDay'] - ((row['AverageSizePerDay']*row['Avg. ProductCost/Acre'])+(row['Avg. Weekly Pay']/5))

def get_tick_product_data(time_frame, sort_by=None):
    path = timezz[time_frame][2]    
    csv = pd.read_csv(path)
    df = pd.DataFrame(csv)
    df = df.loc[df['ProductDescription'] == 'PROGAEA_TMPRO']
    df = df.loc[df['TechnicianName'].isin(tick_employees)]
    df = df[['TechnicianName', 'AmountApplied', 'TreatedArea']]
    df = df.groupby(['TechnicianName']).sum()
    df = df.reset_index()
    df['Treatment/Area'] = df.apply(lambda row: make_rate_stats(row, 'AmountApplied', 'TreatedArea'), axis=1)
    df['DiffFromGoal'] = df.apply(lambda row: get_diff_from_target(row, 9, 11), axis=1)
    df['Avg. ProductCost/Acre'] = df.apply(lambda row: get_cost_per_acre(row), axis=1)
    df.set_index(['TechnicianName'], inplace=True)
    if sort_by is None:
        return df
    else:
        return df.sort_values(by=[sort_by], ascending=False)

def get_turf_product_data(time_frame, sort_by=None):
    path = timezz[time_frame][2]
    csv = pd.read_csv(path)
    df = pd.DataFrame(csv)
    df = pd.DataFrame(csv)
    df['ProductCode'] = df.apply(lambda row: fix_product_code(row), axis=1)
    df = df.loc[df['TechnicianName'].isin(turf_employees)]
    df = df[['TechnicianName', 'ProductDescription', 'ProductCode', 'AmountApplied', 'PropertySize']]
    df = df.groupby(['TechnicianName', 'ProductCode', 'ProductDescription']).sum()
    df = df.reset_index()
    df['Treatment/Area'] = df['AmountApplied'] / df['PropertySize']
    df['Cost/Area ($/1000 Ft^2)'] = df.apply(lambda row: get_product_cost(row), axis=1)
    return df

######################### REPORTS #########################
def get_stats_by_day(df, column_of_interest, choice, title=''):
    if choice == 'Revenue':
        time_col = 'DoneDateFormatted'
        format='%Y-%m-%d'
    elif choice == 'Sales':
        time_col = 'SoldDateFormatted'
        format='%m/%d/%Y'
    df[time_col] = make_datetime(df[time_col], format=format)
    dat = df[column_of_interest].groupby(df[time_col].dt.to_period('D')).sum()
    dat.index = dat.index.to_timestamp()
    dat = dat.to_frame()
    dat = dat.reset_index()
    st.plotly_chart(px.bar(
        x=dat[time_col],
        y=dat[column_of_interest],
        hover_name=dat[time_col],
        title=title
    ))

def format_percentages(row, name):
    if pd.isna(row[name]):
        pass
    else:
        return f'{row[name]:,.2f}%'

def get_summary(df, column_of_interest, start, end, choice, programs=[], branches=[], states=[]):
    start = pd.to_datetime(start, format='%Y-%m-%d')
    end = pd.to_datetime(end, format='%Y-%m-%d')
    if choice == 'Sales':
        date_col = 'SoldDateFormatted'
    elif choice == 'Revenue':
        date_col = 'DoneDateFormatted'
    entries = filter_by_date(df, start, end, date_col)
    entries = entries.loc[entries['Branch'].isin(branches)]
    entries = entries.loc[entries['State'].isin(states)]
    entries = entries.loc[entries['ProgramCode'].isin(programs)]
    make_summary_table(entries, choice, entries[column_of_interest], entries, column_of_interest)

    make_dist_plot(
        entries, 
        column_of_interest,
        f'Distribution of {choice}'
    )
    get_stats_by_day(
        entries,
        column_of_interest,
        choice,
        title=f'Total {choice} by Day'
    )  


class Report:
    def __init__(self, df, start: str, end: str, choice: str, branches: list, programs: list):
        self.df = df
        self.choice = choice
        self.start = start
        self.end = end
        self.branches = branches
        self.programs = programs

        if choice == 'Sales':
            self.numeric_cols = ['TotalPrice', 'ProgramSize']
            self.date_col = ['SoldDateFormatted', 'SoldDateYear']
            self.count_col = 'ProgramId'
            self.format = '%m/%d/%Y'
        elif choice == 'Revenue':
            self.numeric_cols = ['GrossSalesAmount', 'Size']
            self.date_col = ['DoneDateFormatted', 'DoneDateYear']
            self.count_col = 'InvoiceNumber'
            self.format = '%Y/%m/%d'

    def make_stats_dataframe(self):
        sub_df = self.df.loc[(pd.to_datetime(self.df[self.date_col[0]], format=self.format) >= pd.to_datetime(self.start, format='%Y/%m/%d')) & (pd.to_datetime(self.df[self.date_col[0]], format=self.format) <= pd.to_datetime(self.end, format='%Y/%m/%d'))]
        sub_df = sub_df.loc[(sub_df['Branch'].isin(self.branches)) & (sub_df['ProgramCode'].isin(self.programs))]
        stat_dict = {
            'Total' : [f'${np.sum(sub_df[self.numeric_cols[0]]):,.2f}', f'{np.sum(sub_df[self.numeric_cols[1]]):,.2f}'],
            'Average' : [f'${np.mean(sub_df[self.numeric_cols[0]]):,.2f}', f'{np.mean(sub_df[self.numeric_cols[1]]):,.2f}'],
            'Median' : [f'${np.quantile(sub_df[self.numeric_cols[0]], 0.5):,.2f}', f'{np.quantile(sub_df[self.numeric_cols[1]], 0.5):,.2f}'],
            'Num. Customers': [f'{len(sub_df[self.count_col].unique()):,.0f}', f'{len(sub_df[self.count_col].unique()):,.0f}']
        }
        return pd.DataFrame(stat_dict, index = ['Price', 'Size'])
    
    def make_yearly_stats_dataframe(self, program_lists: dict):
        sub_df = self.df.loc[(pd.to_datetime(self.df[self.date_col[0]], format=self.format) >= pd.to_datetime(self.start, format='%Y/%m/%d')) & (pd.to_datetime(self.df[self.date_col[0]], format=self.format) <= pd.to_datetime(self.end, format='%Y/%m/%d'))]
        output_df = pd.DataFrame(index=self.df[self.date_col[1]].unique())
        for i in list(program_lists.keys()):
            output_df[f'{i} Total'] = sub_df.loc[sub_df['ProgramCode'].isin(program_lists[i])].groupby(self.date_col[1]).sum()
            output_df[f'{i} Growth'] = output_df.diff(periods=1)
        return sub_df.groupby(self.date_col[1]).sum()
        
######################### PRODUCTION ANALYSIS #########################
def get_production_perMonth(row, avg_total_daily_rev, percent_days_worked):
    return avg_total_daily_rev*(row['Days']*percent_days_worked)

def get_turf_profit_perDay(row):
    weekly_pay = ((row['RegularHours']*19) + (row['OvertimeHours']*19*1.5))/5
    return row['AverageRevenuePerDay'] - (weekly_pay)

def get_additional_emps(row, df_other, month, colName, avg_emp_production):
    try:
        return ceil((row[colName]/list(df_other['EstProductionDays'].loc[df_other['Month'] == month])[0])/avg_emp_production)
    except TypeError:
        return (row[colName]/list(df_other['EstProductionDays'].loc[df_other['Month'] == month])[0])/avg_emp_production

######################### PLOTLY / OTHER VISUALIZATIONS #########################
def make_plotly_table(df, columns=[]):
    lst = []
    [lst.append(list(df[i])) for i in columns]
    return st.plotly_chart(go.Figure(
        data = 
            [
                go.Table(
                header=dict(values=columns),
                cells = dict(values=lst))
            ]
        ))

def make_daily_program_graph(df, unique_programs, all_stats=True, title='Program Stats by Day', choice=None, colors=None, stat=None):
    turf_programs = OTC_with_addons
    turf_programs['FZ'] = 'Organic Fertilizer'
    if all_stats:
        fig = go.Figure()
        index_val=0
        for prog in unique_programs:
            try:
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df[f'''{prog}_{''.join(stat.split(' '))}'''],
                    name=f'{prog}: {OTC_with_addons[prog]}',
                    marker_color=program_colors[prog]
                ))
            except IndexError:
                    fig.add_trace(go.Bar(
                        x=df.index,
                        y=df[f'''{prog}_{''.join(stat.split(' '))}'''],
                        name=f'{prog}'
                    ))
            index_val +=1
    else:
        if choice is None:
            fig = go.Figure(data=[
            go.Bar(name='TD: Organic Top Dressing', x=df.index, y=df[f'''TD_{''.join(stat.split(' '))}''']),
            go.Bar(name='Others', x=df.index, y=df[f'''Other_{''.join(stat.split(' '))}'''])
            ]) 
        else:
            prog = choice.split(':')[0]
            fig = go.Figure(data=[
            go.Bar(name=f'{prog}: {OTC_with_addons[prog]}', x=df.index, y=df[f'''{prog}_{''.join(stat.split(' '))}''']),
            go.Bar(name='Others', x=df.index, y=df[f'''Other_{''.join(stat.split(' '))}'''])
            ]) 

    fig.update_layout(
        barmode='stack',
        title_text=title
    )
    return fig

def get_color(row):
    return np.where(float(row['Total'])<0, 'red', 'green')

def make_bar(df, choice):
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(
        go.Scatter(
            x=df['ProgramCode'], 
            y=df['GROWTH: Num. of Customers (%)'],
            name='Customer Growth (%)'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df['ProgramCode'],
            y=df[choices[choice][0]],
            name='Old'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df['ProgramCode'],
            y=df[choices[choice][1]],
            name='New'
        ),
        row=2, col=1
    )
    fig.update_layout(
        title=f'''Customer Growth by Programs (%) + {choice} Between Old and New Customers''', 
        barmode='group'
        )
    return st.plotly_chart(fig)

def make_color_plot(df, x_col, y_col, title=None, x_label=None, y_label=None):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            marker_color=df['Color'],
            ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    return st.plotly_chart(fig) 

def make_multichart(df, choice):
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(
        go.Scatter(
            x=df['ProgramCode'], 
            y=df['GROWTH: Num. of Customers (%)'],
            name='Customer Growth (%)'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df['ProgramCode'],
            y=df[customer_growth_choices[choice][0]],
            name='Old'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df['ProgramCode'],
            y=df[customer_growth_choices[choice][1]],
            name='New'
        ),
        row=2, col=1
    )
    fig.update_layout(
        title=f'''{previous_month} 2021: Customer Growth by Programs (%) + {choice} Between Old and New Customers''', 
        barmode='group'
        )
    return st.plotly_chart(fig)

def line_graph(x_col, y_col, y_label = '', x_label = '', title = '', hover_name=''):
    graph = px.line(
        x = x_col, 
        y = y_col,
        title = title,
        labels = {
            'y' : y_label, 
            'x' : x_label
        },
        hover_name=hover_name
        )
    st.plotly_chart(graph)

def bar_graph(x_col: pd.Series, y_col: pd.Series, title: str, x_label=None, 
                y_label=None, hover_data=None, color=None, labels=None):
    graph = px.bar(
        x = x_col, 
        y = y_col,
        title = title,
        color=None,
        labels = {
            'y' : y_label, 
            'x' : x_label
        },
        hover_data=hover_data
        )
    st.plotly_chart(graph)

def make_dist_plot(df, column_of_interest, title=''):
    fig = px.histogram(df, x=column_of_interest, marginal='box', title=title)
    st.plotly_chart(fig)

def make_summary_table(df, choice, y_col, entries, column_of_interest):
    count_customer_col = 'CustomerFirstNameLastNameOrCompany'
    count_program_col = 'InvoiceNumber'
    
    if column_of_interest in money_cols:
        symb = '$'
    else:
        symb = ''
    
    stat_dict = {
        'Total' : f'{symb}{np.sum(y_col):,.2f}',
        'Average' : f'{symb}{np.mean(y_col):,.2f}',
        'Median' : f'{symb}{np.quantile(y_col, 0.5):,.2f}',
        'Num. Customers': f'{len(df[count_customer_col].unique()):,.0f}',
        'Num. Programs': f'{len(df[count_program_col].unique()):,.0f}'
    }

    datzz = pd.DataFrame(stat_dict, index = [0])
    st.table(datzz)

def set_color(x):
    if x >= 0:
        return 'green'
    else:
        return 'red'