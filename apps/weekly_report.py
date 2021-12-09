import datetime as dt
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data.programs import OTC_with_addons
from data.employee_lists import turf_employees
from functions import make_datetime, get_clean_data, identify_program
from functions import get_tick_product_data, get_year_end_results
from functions import get_color, get_tick_employee_results, make_subplots
from functions import get_month_end_results, remove_bad_results, set_color

OTC_with_addons['FZ1'] = 'Fertilizer Treatment 1'

def app():
#### LOAD DATA ####
    # Revenue
    df_rev = get_clean_data(
        path='data/clean/revenue/clean_revenue.csv',
        low_memory=False
    )
    df_rev['PackageProgram'] = df_rev.apply(lambda row: identify_program(row), axis=1)

    # Sales
    df_sales = get_clean_data(
        path='data/clean/sales/sales_1522.csv',
        low_memory=False
    )
    df_sales['PackageProgram'] = df_sales.apply(lambda row: identify_program(row), axis=1)

    # Cancels
    csv1 = pd.read_csv('data/clean/cancels/cancels_1522.csv')
    df_cancels = pd.DataFrame(csv1)   
    #df_cancels['PackageProgram'] = df_cancels.apply(lambda row: identify_program(row), axis=1)

    df_employees = get_clean_data(
        'data/clean/revenue/clean_revenue.csv',
        low_memory=False
    )
    df_employees['clean_size_per_hour'] = df_employees.apply(lambda row: remove_bad_results(row), axis=1)

#### OVERVIEW ####
    st.write('''
    # **LT Analytics Meeting Overview:** 
    ''')

    st.write('''
        - Revenue
        - Sales
        - Cancels
        - Growth (monthly + yearly)
        - Other relevant info \
    ''')

    st.write('''
    **Revenue**
    ''')

    st.write('''
    Year over year
    ''')

    end_year_revs = get_year_end_results(df_rev, 2016, 2022)
    end_year_sales = get_year_end_results(df_sales, 2016, 2022)
    end_year_cancels = get_year_end_results(df_cancels, 2016, 2022)
    end_month_sales = get_month_end_results(df_sales, 2016, 2022)
    end_month_cancels = get_month_end_results(df_cancels, 2016, 2022)

#### REVENUE ####

    st.plotly_chart(px.bar(
        end_year_revs, 
        x=end_year_revs.index, 
        y=['T&M', 'OTC'],
        title='Yearly Revenue by Program'
    ))

#### SALES ####
    st.write('''
        **Sales**
        ''')

    st.plotly_chart(px.bar(
        end_year_sales,
        x=end_year_sales.index,
        y=['T&M', 'OTC'],
        title='Yearly Sales by Program'
    ))
    st.plotly_chart(px.bar(
        end_month_sales,
        x=end_month_sales.index,
        y=['T&M', 'OTC'],
        title='Monthly Sales by Program'
    ))


#### CANCELS ####
    st.plotly_chart(px.bar(
        end_year_cancels,
        x=end_year_cancels.index,
        y=['T&M', 'OTC'],
        title='Yearly Cancels by Program'
    ))

    st.plotly_chart(px.bar(
        end_month_cancels,
        x=end_month_cancels.index,
        y=['T&M', 'OTC'],
        title='Monthly Cancels by Program'
    ))

    today = dt.datetime.today()
    today = today.strftime('%m/%d')
    mask = (make_datetime(df_cancels['FormattedCancelDate'], format='%m/%d/%Y') >= pd.to_datetime(f'2021/1/1', format='%Y/%m/%d')) & (make_datetime(df_cancels['FormattedCancelDate'], format='%m/%d/%Y') <= pd.to_datetime(f'2021/{today}', format='%Y/%m/%d'))
    cancels_21 = {}
    def get_total_cancels_perReason(row):
        try:
            cancels_21[row['CancelReason']] += row['TotalPrice']
        except KeyError:
            cancels_21[row['CancelReason']] = row['TotalPrice']
    df_cancels.apply(lambda row: get_total_cancels_perReason(row), axis=1)
    cancels_21 = pd.DataFrame.from_dict(
        cancels_21,
        orient='index',
        columns=['TotalPrice']
    )
    cancels_21.reset_index(inplace=True)
    cancels_21.columns = cancels_21.columns.str.replace('index', 'CancelReason')
 
    st.plotly_chart(px.bar(
        cancels_21,
        x='CancelReason',
        y='TotalPrice',
        color='TotalPrice'
    ))

### GROWTH ####
    st.markdown('''
    **Revenue and Sales Growth** \n
    NOTE: All growth rates are based on yearly revenue as of today.
    ''')

    st.plotly_chart(px.line(
        data_frame=end_year_revs,
        x=end_year_revs.index,
        y=['T&M Growth', 'OTC Growth', 'Total Growth'],
        title='Revenue Growth YoY (%)'
    ))

    temp_sales = end_year_sales.loc[[2019, 2020, 2021]]
    temp_sales.index = pd.to_datetime(temp_sales.index, format='%Y')
    st.plotly_chart(px.line(
        data_frame=temp_sales,
        x=temp_sales.index,
        y=['T&M Growth', 'OTC Growth', 'Total Growth'],
        title='Sales Growth YoY (%)'
    ))

    rev_and_sales = pd.DataFrame(index=end_year_sales.index)
    rev_and_sales['Total Sales'] = end_year_sales['Total Growth']
    rev_and_sales['Total Revenue'] = end_year_revs['Total Growth']
    st.plotly_chart(px.line(
        data_frame=rev_and_sales, 
        x=rev_and_sales.index, 
        y=['Total Sales', 'Total Revenue'], 
        title='Sales vs. Revenue Growth YoY (%)'

        ))

    
#### EMPLOYEE STATS ####

    # Production
    st.write('''
    T&M Employee Production (Avg. Acre Sprayed/Minute)
    ''')
    prod_results = get_tick_employee_results(df=df_employees, rev_col='GrossSalesAmount', time_frame='Current Month', sort_by='Avg. Acres/Minute')
    prod_results.reset_index(inplace=True)
    prod_results.rename(columns={'index': 'Employee'}, inplace=True)
    st.write('Monthly')
    st.dataframe(prod_results)


    # Product Usage
    st.write('''
    T&M Employee Product Usage
    ''')
    use_results = get_tick_product_data('Current Month', 'Treatment/Area')
    use_results.reset_index(inplace=True)
    st.write('Monthly')
    st.dataframe(use_results)

#### OTHER INFO ####
    st.write('''
    **Round 4 Status**
    ''')

    round4_to_be_serviced = {
        'CA': [682, 4761.46, 96630.00, 141.69],
        'FZ4': [821, 6133.41, 78934.50, 96.14],
        'OS': [681, 4633.83, 125758.00, 184.67],
        'TD': [279, 1832.43, 165475.50, 593.10],
        'Total': [2463, 17361.13, 466798.00, 189.52]
    }
    round4_to_be_serviced = pd.DataFrame.from_dict(
        round4_to_be_serviced, 
        orient='index',
        columns=['NumServings', 'Size', 'Value', 'Value/Serving'],
        )
    round4_to_be_serviced.reset_index(inplace=True)

    st.write('''
    Round 4 - Yet to be Serviced
    ''')
    st.dataframe(round4_to_be_serviced)

    round4_capabilities = {
        'NumServings': [16, 18, 15, 7, 56],
        'Size': [115.69, 145.31, 111.17, 50.74, 422.90],
        'Value': [2313.39, 1767.48, 2796.65, 4312.00, 11189.53]
    }
    round4_capabilities = pd.DataFrame.from_dict(
        round4_capabilities, 
        orient='index',
        columns = ['CA', 'FZ4', 'OS', 'TD', 'Total']
        )
    
    round4_capabilities_perEmployee = {
        'NumServings': [2.64, 3.01, 2.58, 1.18, 9.40],
        'Size': [19.28, 24.22, 18.53, 8.46, 70.48],
        'Value': [385.57, 294.58, 466.11, 718.67, 1864.92]
    }
    round4_capabilities_perEmployee = pd.DataFrame.from_dict(
        round4_capabilities_perEmployee, 
        orient='index',
        columns = ['CA', 'FZ4', 'OS', 'TD', 'Total']
        )

    daily_need_scenarios = {}
    for i in range(15, 31):
        daily_need_scenarios[f'{i}'] = []
        for index, row in round4_to_be_serviced.iterrows():
            try:
                needed = row['NumServings'] / i
            except ZeroDivisionError:
                needed = 0
            daily_need_scenarios[f'{i}'].append(needed)
    daily_need_scenarios = pd.DataFrame.from_dict(
        daily_need_scenarios, 
        orient='index',
        columns = ['CA', 'FZ4', 'OS', 'TD', 'Total']
        )

    needs_vs_capabilities = pd.DataFrame(columns=['CA', 'FZ4', 'OS', 'TD', 'Total'])
    employees_needed = pd.DataFrame(columns=['CA', 'FZ4', 'OS', 'TD', 'Total'])
    for i in daily_need_scenarios.columns:
        needs_vs_capabilities[i] = round4_capabilities.loc['NumServings', i] - daily_need_scenarios[i]
        employees_needed[i] = np.ceil(-1*(needs_vs_capabilities[i] / round4_capabilities_perEmployee.loc['NumServings', i]))-len(turf_employees)
    
    daily_need_scenarios.reset_index(inplace=True)
    daily_need_scenarios.columns = daily_need_scenarios.columns.str.replace('index', 'Days Remaining')
    needs_vs_capabilities.reset_index(inplace=True)
    needs_vs_capabilities.columns = needs_vs_capabilities.columns.str.replace('index', 'Days Remaining')
    needs_vs_capabilities['Color'] = needs_vs_capabilities.apply(lambda row: get_color(row), axis=1)
    employees_needed.reset_index(inplace=True)
    employees_needed.columns = employees_needed.columns.str.replace('index', 'Days Remaining')
    employees_needed['Color'] = employees_needed.apply(lambda row: get_color(row), axis=1)

    '''
    for i in daily_need_scenarios.columns:
        needs_vs_capabilities[i] = needs_vs_capabilities[i].map('{:,.2f}'.format)
        employees_needed[i] = employees_needed[i].map('{:,.0f}'.format)
        daily_need_scenarios[i] = daily_need_scenarios[i].map('{:,.2f}'.format)
    '''

    st.dataframe(needs_vs_capabilities)

    st.write('''
    Round 4 - Daily Capabilities
    ''')
    st.dataframe(round4_capabilities)
    st.write('''
    Round 4 - Number of Servings Needed by Number of Days
    ''')
    st.dataframe(daily_need_scenarios)
    
    st.write('''
    **Difference in Serving Capability vs. Services Needed for All Round 4 Programs(by Days Remaining)**
    ''')
    st.dataframe(needs_vs_capabilities)
    
    st.write('''
    **TAKEAWAY** \n
    We will need need additional turf care employees in order to complete all services within the next 4 days or less 
    ''')

    st.markdown('''
    **Number of additional employees needed to fulfill services in given number of days.**
    ''')
    st.dataframe(employees_needed)

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Scatter(
            x = employees_needed['Days Remaining'],
            y = employees_needed['Total'],
            name = 'Employees Needed',
            marker=dict(
                color=(
                    list(map(set_color, employees_needed['Total']))
                )
            ),
            mode='markers+lines'
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash='dot',
        row=1, col=1,
        annotation_text='Goal Line',
        annotation_font_size=16)
    fig.update_layout(
        title=f'''Additional Employees Needed vs. Days Remaining''',
        xaxis_title='Days Remaining',
        yaxis_title=f'''Employees Needed'''
    )
    st.plotly_chart(fig)

    st.markdown(f'''
    **TAKEAWAY:** \n
    Each cell represents the number of additional employees needed to fulfill the number of services 
    in the given number of days left in Round 4. \n
    *EXAMPLE: We will need at least {np.abs(int(employees_needed.iloc[2]['Total']))} additional turf care employee in order to fulfill all services
    for all programs of Round 4 within the next 3 days* \n
    *EXAMPLE 2: We can lose at most {np.abs(int(employees_needed.iloc[13]['Total']))} turf care employee and still be capable of fulfilling all services
    for all programs of Round 4 within the next 14 days*
    ''')

