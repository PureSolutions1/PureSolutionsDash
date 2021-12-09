import pandas as pd
import datetime as dt
rate = None
max_rate = None
first_of_week = (dt.datetime.today() - dt.timedelta(days = dt.datetime.today().isoweekday() % 7)).day
currentMonth = dt.datetime.now().month

turf_employees = [
    'Fahad Rashid',
    'Jonathan Gonzalez',
    'Bryan Regalado',
    'Gabriel Salas',
    'Erick Lopez Lopez',
    'Ariel Ortega',
    'Jose Lopez Lopez',
    'Cole Morrison',
    'Jordi Gonzalez',
    'Moises Lopez-Noriega',
    'Jose Mejia'
]

OTC_with_addons = {
    'OTC': 'Organic Turf Care (Full)',
    'CA': 'Core Aeration',
    'GM': 'Grub and Insect Application',
    'LAG': 'Limestone Granular',
    'MS': 'Mechanical Seeding',
    'OS': 'Over-Seeding Application',
    'PRE': 'Organic Weed Pre-Emergent',
    'ST': 'Soil Test',
    'TD': 'Organic Top Dressing',
    'TWC': 'Plant Based Weed Control',
    'WM': 'Weed Management',
    'FZ1': 'Feritilizer 1',
    'FZ2': 'Feritilizer 2',
    'FZ3': 'Feritilizer 3',
    'FZ4': 'Feritilizer 4',
    'FZ5': 'Feritilizer 5',
}

def get_clean_data(path, rev_col='GrossSalesAmount', low_memory = True):
    csv1 = pd.read_csv(path, low_memory = low_memory)
    df1 = pd.DataFrame(csv1)
    if 'data\\clean\\sales' in path:
        df1['SoldDateFormatted'] = pd.to_datetime(df1['SoldDateFormatted'], format='%m/%d/%Y')
        return df1
    elif 'data\\clean\\revenue' in path:
        df1['DoneDateFormatted'] = pd.to_datetime(df1['DoneDateFormatted'], format='%Y-%m-%d')
        df1['IndividualServiceNumber'] = df1.index
        '''
        df1['GrossSalesAdjusted'] = df1.apply(lambda row: adjust_vineyard_revenue(row), axis=1)
        df1['size_per_hour'] = df1.apply(lambda row: make_rate_stats(row, 'CustomerSize', 'TotalManHours')*60, axis=1)
        df1['value_per_hour'] = df1.apply(lambda row: make_rate_stats(row, rev_col, 'TotalManHours')*60, axis=1)
        '''
        return df1
    else:
        print('Weird data you\'re using there.')

def get_turf_employee_results(df, rev_col, start=None, end=None, time_frame=None, sort_by=None):
    df = df.loc[df['ProgramCode'].isin(OTC_with_addons.keys())]
    print(df[['IndividualServiceNumber', 'CustomerFirstNameLastNameOrCompany']])

    df = df[[   
        'EmployeeName', 'DoneDateFormatted', 'GrossSalesAmount', 'CustomerSize', 'TotalManHours', 'Size', 
        'GrossSalesAdjusted', 'size_per_hour', 'value_per_hour', 'IndividualServiceNumber'
    ]]

    df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%Y-%m-%d')

    df = df.groupby(['IndividualServiceNumber']).agg({
        'DoneDateFormatted': pd.Series.mode,
        'EmployeeName': pd.Series.mode,
        'GrossSalesAmount': 'sum',
        'CustomerSize': 'mean',
        'TotalManHours': 'mean',
        'Size': 'mean',
        'GrossSalesAdjusted': 'sum',
        'size_per_hour': 'mean',
        'value_per_hour': pd.Series.sum
    })
    print(df[['DoneDateFormatted', 'EmployeeName']])
    df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%Y-%m-%d')
    return df.reset_index()

def make_rate_stats(row, name1, name2):
    try:
        global rate
        rate = row[name1] / row[name2]
    except ZeroDivisionError:
        pass
    return rate

def adjust_vineyard_revenue(row):
    if row['ProgramCode'].upper() in ['MVB', 'MVM', 'MVT']:
        return float(row['GrossSalesAmount']*0.8)
    else:
        return float(row['GrossSalesAmount'])

df = get_clean_data(
        'C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\revenue\\clean_revenue.csv',
        low_memory=False,
        rev_col='GrossSalesAmount'
    )

df_out = get_turf_employee_results(df, 'GrossSalesAmount')
df_out.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\employee_hours\\turf_employees.csv')