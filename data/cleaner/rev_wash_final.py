import pandas as pd
import numpy as np
np.random.seed(1)

rate = None


print('Loading Data....')
csv = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\revenue\\revenue_22.csv',
                    low_memory=False)
csv2 = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\revenue\\revenue_1521.csv', 
                    low_memory=False)
df = pd.DataFrame(csv)
df2 = pd.DataFrame(csv2)

# Filter out duplicate current year results

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

respray_progs = {
    'RTB': ['B14', 'B21', 'B28', 'MVB'], 
    'RTM': ['M14', 'M21', 'M28', 'MVM'], 
    'RTT': ['T14', 'T21', 'T28', 'MVT']
}

teams = {
    'South': ['Ariel Ortega', 'Brendon Deveaux', 'Eduardo Cortez', 'Fahad Rashid', 'John Moudarri', 'Jose Rosado', 'Richard Rich', 'Mohamed Aljundi', 'Mason Bolivar', 'Benjamin Bolivar', 'Charles Bolivar'],
    'North': ['Seamus O\'connell', 'Marc Tisme', 'Ryan Fratus', 'Kevin Enriques-Uluan'],
    'Metro West': ['Francisco Nieves', 'Jamir Alexander', 'Ryan Fleet'],
    'Cape': ['Daniel Cook', 'Marcus Harrington', 'Jeremy Lucyk']
}
tick_guys = []
for lst in teams.values():
    for guy in lst:
        tick_guys.append(guy)

OTC_with_addons = {
    'OTC': 'Organic Turf Care (Full)',
    'CA': 'Core Aeration',
    'DWC': 'Granular Crabgrass\Broadleaf', 
    'DWM': 'Driveway\Walkway Weed Management', 
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
    'TSL': 'Top Soil\Loam',
    'WM': 'Weed Management',
    'VOL': 'Vole Repellent Service',
    'YNG': 'Yard Granular Treatment',
    'FZ1': 'Organic Fertilizer: Round 1',
    'FZ2': 'Organic Fertilizer: Round 2',
    'FZ3': 'Organic Fertilizer: Round 3',
    'FZ4': 'Organic Fertilizer: Round 4',
    'FZ5': 'Organic Fertilizer: Round 5',
}

def generate_id(s):
    return abs(hash(tuple(s))) % (10 ** 10)

def find_team(row):
    NotFound = True
    for key in teams.keys():
        if row['EmployeeName'] in teams[key]:
            NotFound = False
            return key
    if NotFound:
        return 'NoTeam'

def clean_program_codes(row):
    entry = row['MainGroupDescription'].split(' ')
    first_letter = entry[0].split()
    if first_letter[0].isnumeric():
        return 'expired_program_code'
    else:
        return entry[0]

invoice_list = []
def find_ogSpray_invoiceNums(df, roww):
    date_list = {}
    if roww['ProgramCode'] in respray_progs.keys():
        respray_date = roww['DoneDateFormatted']
        respray_year = roww['DoneDateYear']
        temp_df = df.loc[df['Address'] == roww['Address']]
        temp_df = temp_df.loc[np.abs((respray_date - temp_df['DoneDateFormatted']).astype('timedelta64[D]')) <= 180]
        temp_df = temp_df.loc[df['ProgramCode'].isin(respray_progs[roww['ProgramCode']])]
        for index, row in temp_df.iterrows():
            date_list[row['InvoiceNumber']] = np.abs((respray_date - row['DoneDateFormatted']).days)
        try:
            minval = min(date_list.values())
            magic_num = [k for k, v in date_list.items() if v==minval][0]
            invoice_list.append(magic_num)
    
        except ValueError:
            pass
    else:
        pass

def find_resprays_byInvoice(row):
    if row['InvoiceNumber'] in invoice_list:
        return int(1)
    else:
        return int(0)

def get_branch(row):
    try:
        if row['BranchNumberAndBranchNameOfCustomer'] == 'nan':
            return 'UNKNOWN'
        else:
            parts = row['BranchNumberAndBranchNameOfCustomer'].split(' ')
            return parts[0]
    except KeyError:
        if row['Branch'] == 'nan':
            return 'UNKNOWN'
        else:
            parts = row['Branch'].split(' ')
            return parts[0]
        

def clean_states(row):
    if len(str(row['State'])) == 2 and row['State'].isalpha():
        return str(row['State']).upper()
    else:
        return 'UNKNOWN'

def make_rate_stats(row, name1, name2):
    try:
        global rate
        rate = row[name1] / row[name2]
    except (ZeroDivisionError, TypeError):
        pass
    return rate

def make_by_hour(row, name):
    try:
        return row[name]*60
    except TypeError:
        pass

def adjust_vineyard_revenue(row):
    if row['ProgramCode'].upper() in ['MVB', 'MVM', 'MVT']:
        return float(row['GrossSalesAmount']*0.8)
    else:
        return float(row['GrossSalesAmount'])

print('Cleaning Data....')
df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%m/%d/%Y')
df['DoneDateYear'] = df['DoneDateFormatted'].dt.to_period('Y')
df['ProgramCode'] = df.apply(lambda row: clean_program_codes(row), axis=1)
df['Team'] = df.apply(lambda row: find_team(row), axis=1)
df['State'] = df.apply(lambda row: clean_states(row), axis=1)
df['Branch'] = df.apply(lambda row: get_branch(row), axis=1)

df = df[[
    'CustomerFirstNameLastNameOrCompany',
    'DoneDateFormatted', 
    'DoneDateYear',
    'GrossSalesAmount',
    'CustomerSize', 
    'ProgramCode',
    'EmployeeName',
    'Team',
    'Size',
    'TotalManHours',
    'Address',
    'City',
    'State',
    'InvoiceNumber',
    'Branch'
    ]]

# Remove Duplicate current year rows
if '2021' in df['DoneDateYear'].unique():
    df2 = df2.loc[df2['DoneDateYear'] != 2021]

print('Finding resprays....')
df.apply(lambda row: find_ogSpray_invoiceNums(df, row), axis=1)
df['NeedRespray'] = df.apply(lambda row: find_resprays_byInvoice(row), axis=1)

df_final = pd.concat([df, df2])
df_final['State'] = df_final.apply(lambda row: clean_states(row), axis=1)
df_final['Branch'] = df_final.apply(lambda row: get_branch(row), axis=1)

df_property_sub = df_final[[
    'DoneDateFormatted',
    'ProgramCode',
    'Address'
]]

df_team_sub = df_final[[
    'DoneDateFormatted',
    'Address'
]]
df_ind_sub = df_final[[
    'EmployeeName',
    'DoneDateYear',
    'DoneDateFormatted',
    'Address'
]]

print('Hashing unique services....')
df_final['TeamServiceNumber'] = pd.Series((hash(tuple(row)) for _, row in df_team_sub.iterrows()))
df_final['IndividualServiceNumber'] = df_final.index
#df_final['IndividualServiceNumber'] = pd.Series((hash(tuple(row)) for _, row in df_final.iterrows()))
df_final['PropertyNumber'] = pd.Series((hash(tuple(row)) for _, row in df_property_sub.iterrows()))

df_final['GrossSalesAdjusted'] = df_final.apply(lambda row: adjust_vineyard_revenue(row), axis=1)

df_final['size_per_hour'] = df_final.apply(lambda row: make_rate_stats(row, 'CustomerSize', 'TotalManHours'), axis=1)
df_final['size_per_hour'] = df_final.apply(lambda row: make_by_hour(row, 'size_per_hour'), axis=1)

df_final['value_per_hour'] = df_final.apply(lambda row: make_rate_stats(row, 'GrossSalesAmount', 'TotalManHours'), axis=1)
df_final['value_per_hour'] = df_final.apply(lambda row: make_by_hour(row, 'value_per_hour'), axis=1)

print('Saving data file....')
df_final.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\revenue\\clean_revenue.csv')
print('Complete.')