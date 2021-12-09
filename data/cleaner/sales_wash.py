import pandas as pd
import numpy as np

csv = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\sales\\sales_1522.csv', 
                    low_memory=False)
csv2 = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\unserviced_accounts\\unserviced_accounts.csv')

csv3 = pd.read_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\dirty\\sales\\sales_1522.csv')

df = pd.DataFrame(csv)
df2 = pd.DataFrame(csv2)
df_current = pd.DataFrame(csv3)

def clean_date(row):
    parts = row['SoldDate'].split(' ')
    return parts[0]

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

df['SoldDate'] = df.apply(lambda row: clean_date(row), axis = 1)
df['Branch'] = df.apply(lambda row: get_branch(row), axis = 1)
df['State'] = df.apply(lambda row: clean_states(row), axis = 1)
df['SoldDateYear'] = pd.to_datetime(df['SoldDateFormatted'], format='%m/%d/%Y').dt.year
df = df[[
    'CustomerFirstNameLastNameOrCompany',
    'CustomerNumber',
    'SoldDateFormatted',
    'SoldDateYear',
    'City',
    'State',
    'Address',
    'TotalPrice',
    'ProgramSize',
    'ProgramCode',
    'EmployeeName',
    'ProgramId',
    'Branch'
]]

df_invoice = df[[
    'CustomerNumber',
    'ProgramCode',
    'Address'
]]

df['InvoiceNumber'] = pd.Series((hash(tuple(row)) for _, row in df_invoice.iterrows()))


df = df.loc[~((pd.to_numeric(pd.DatetimeIndex(pd.to_datetime(df['SoldDateFormatted'], format='%m/%d/%Y')).year) <= 2020) & (df['Branch']=='MV'))]

df2 = df2[[
    'City',
    'ServiceId',
    'ServiceSize',
    'ServicePrice'
]]

[df.drop(columns = [i], inplace=True) for i in df.columns if 'Unnamed' in i]
[df2.drop(columns = [i], inplace=True) for i in df2.columns if 'Unnamed' in i]

df.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\sales\\sales_1522.csv')
df2.to_csv('C:\\Users\\spenc\\Desktop\\PureSolutionsDash\\data\\clean\\unserviced\\top_dress.csv')
