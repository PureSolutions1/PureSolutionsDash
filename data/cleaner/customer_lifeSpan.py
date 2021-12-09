import pandas as pd
import datetime as dt

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

df_cancels = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\cancels\\cancels_1522.csv')
df_cancels = pd.DataFrame(df_cancels)

df_rev = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\revenue\\clean_revenue.csv', 
                    low_memory=False)
df_rev = pd.DataFrame(df_rev)
df_rev['DoneDateFormatted'] = pd.to_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d').dt.strftime('%m/%d/%Y')

dict_combo = {}
def get_disgruntled_customers(row):
    if row['CustomerStatus'] == 5:
        dict_combo[row['CustomerFirstNameLastNameOrCompany']] = ['Cancelled', row['FormattedCancelDate'], [], 0, 0]
    else:
        pass
def get_current_customers(row):
    if row['CustomerFirstNameLastNameOrCompany'] in dict_combo.keys():
        pass
    else:
        dict_combo[row['CustomerFirstNameLastNameOrCompany']] = ['Current', None, [], 0, 0]
def get_service_dates(row):
    if row['CustomerFirstNameLastNameOrCompany'] in dict_combo.keys():
        dict_combo[row['CustomerFirstNameLastNameOrCompany']][2].append(row['DoneDateFormatted'])
    else:
        pass
def count_program_services(row, program):
    if program.upper() == 'T&M':
        if row['CustomerFirstNameLastNameOrCompany'] in dict_combo.keys():
            if row['ProgramCode'] in TM_list.keys():
                dict_combo[row['CustomerFirstNameLastNameOrCompany']][3] += 1
        else:
            pass
    elif program.upper() == 'TURF':
        if row['CustomerFirstNameLastNameOrCompany'] in dict_combo.keys():
            if row['ProgramCode'] in OTC_with_addons.keys():
                dict_combo[row['CustomerFirstNameLastNameOrCompany']][4] += 1
        else:
            pass
def get_life_span_days(row):
    if row['DeathDate'] is pd.NaT:
        return (pd.Timestamp.today() - row['BirthDate']).days
    else:
        return (row['DeathDate'] - row['BirthDate']).days
def get_life_span_months(row):
    if row['DeathDate'] is pd.NaT:
        return ((pd.Timestamp.today() - row['BirthDate']).days)/30
    else:
        return ((row['DeathDate'] - row['BirthDate']).days)/30
def get_life_span_years(row):
    if row['DeathDate'] is pd.NaT:
        return ((pd.Timestamp.today() - row['BirthDate']).days)/365
    else:
        return ((row['DeathDate'] - row['BirthDate']).days)/365
def get_num_services(row):
    return len(row['ServiceDates'])

def get_buyer_type(row):
    if ((row['Num. T&M Services'] > 0) and (row['Num. Turf Services'] > 0)):
        return 'Both'
    elif row['Num. T&M Services'] == 0:
        if row['Num. Turf Services'] == 0:
            return 'Other'
        else:
            return 'Turf'
    elif row['Num. Turf Services'] == 0:
        if row['Num. T&M Services'] == 0:
            return 'Other'
        else:
            return 'T&M'

#df_cancels['FormattedCancelDate'] = pd.to_datetime(df_cancels['CanDate'], format='%m/%d/%Y')
df_cancels['FormattedCancelDate'] = df_cancels['CanDate']
df_cancels.apply(lambda row: get_disgruntled_customers(row), axis=1)
df_rev.apply(lambda row: get_current_customers(row), axis=1)
df_rev.apply(lambda row: get_service_dates(row), axis=1)
df_rev.apply(lambda row: count_program_services(row, 'T&M'), axis=1)
df_rev.apply(lambda row: count_program_services(row, 'Turf'), axis=1)
for key in dict_combo.keys():
    dict_combo[key][2] = [dt.datetime.strptime(i, '%m/%d/%Y') for i in dict_combo[key][2]]
    try:
        dict_combo[key].append(min(dict_combo[key][2]))
    except ValueError:
        dict_combo[key].append(None)
    try:
        dict_combo[key].append(max(dict_combo[key][2]))
    except ValueError:
        dict_combo[key].append(None)

df_combo = pd.DataFrame.from_dict(
    dict_combo,
    orient='index',
    columns=['Status', 'DeathDate', 'ServiceDates', 'Num. T&M Services', 'Num. Turf Services', 'BirthDate', 'LastService']
)

df_combo['NumServices'] = df_combo.apply(lambda row: get_num_services(row), axis=1)
df_combo['BirthDate'] = pd.to_datetime(df_combo['BirthDate'], format='%Y-%m-%d')
df_combo['DeathDate'] = pd.to_datetime(df_combo['DeathDate'], format='%m/%d/%Y')
df_combo['CustomerType'] = df_combo.apply(lambda row: get_buyer_type(row), axis=1)
df_combo = df_combo[pd.notnull(df_combo['BirthDate'])]
df_combo['LifeSpan (Days)'] = df_combo.apply(lambda row: get_life_span_days(row), axis=1)
df_combo['LifeSpan (Months)'] = df_combo.apply(lambda row: get_life_span_months(row), axis=1)
df_combo['LifeSpan (Years)'] = df_combo.apply(lambda row: get_life_span_years(row), axis=1)
df_combo = df_combo.reset_index()
df_combo = df_combo.rename(columns={
    'index': 'CustomerName'
})

df_combo.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\customers\\customer_lifeSpan.csv')
