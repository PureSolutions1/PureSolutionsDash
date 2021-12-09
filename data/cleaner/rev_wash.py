import pandas as pd
import numpy as np
import datetime as dt
import random
from time import sleep
import sys

print('Loading Data....')
csv = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\revenue\\revenue_1522.csv', 
                    low_memory=False)
df = pd.DataFrame(csv)

respray_progs = {
    'RTB': ['B14', 'B21', 'B28', 'MVB'], 
    'RTM': ['M14', 'M21', 'M28', 'MVM'], 
    'RTT': ['T14', 'T21', 'T28', 'MVT']
}

teams = {
    'South': ['Ariel Ortega', 'Brendon Deveaux', 'Eduardo Cortez', 'Fahad Rashid', 'John Moudarri', 'Jose Rosado', 'Richard Rich', 'Mohamed Aljundi', 'Mason Bolivar', 'Benjamin Bolivar', 'Jaden Colbert'],
    'North': ['Seamus O\'connell', 'Marc Tisme', 'Ryan Fratus', 'Kevin Enriques-Uluan'],
    'Metro West': ['Francisco Nieves', 'Jamir Alexander', 'Ryan Fleet'],
    'Cape': ['Daniel Cook', 'Marcus Harrington', 'Jeremy Lucyk']
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

def find_team(row):
    for key in teams.keys():
        if row['EmployeeName'] in teams[key]:
            return key
        else:
            continue

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
    parts = row['BranchNumberAndBranchNameOfCustomer'].split(' ')
    return parts[0]

print('Cleaning Data....')
df['RowNum'] = df.index
df['DoneDateFormatted'] = pd.to_datetime(df['DoneDateFormatted'], format='%m/%d/%Y')
df['DoneDateYear'] = df['DoneDateFormatted'].dt.to_period('Y')
df['ProgramCode'] = df.apply(lambda row: clean_program_codes(row), axis=1)
df['Team'] = df.apply(lambda row: find_team(row), axis=1)
df['Branch'] = df.apply(lambda row: get_branch(row), axis=1)

df = df[[
    'RowNum',
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

df_property_sub = df[[
    'DoneDateFormatted',
    'ProgramCode',
    'Address'
]]

df_team_sub = df[[
    'DoneDateFormatted',
    'Address'
]]
df_ind_sub = df[[
    'EmployeeName',
    'DoneDateFormatted',
    'Address'
]]

df = df.loc[~((df['DoneDateYear'].dt.year < 2021) & (df['ProgramCode'].isin(['MVB', 'MVD', 'MVM', 'MVT'])))]

print('Finding resprays....')
df.apply(lambda row: find_ogSpray_invoiceNums(df, row), axis=1)
df['NeedRespray'] = df.apply(lambda row: find_resprays_byInvoice(row), axis=1)
print('Hashing unique services....')
df['TeamServiceNumber'] = pd.Series((hash(tuple(row)) for _, row in df_team_sub.iterrows()))
df['IndividualServiceNumber'] = pd.Series((hash(tuple(row)) for _, row in df_ind_sub.iterrows()))
df['PropertyNumber'] = pd.Series((hash(tuple(row)) for _, row in df_property_sub.iterrows()))
print('Saving data file....')
df.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\revenue\\clean_revenue.csv')
print('Complete.')