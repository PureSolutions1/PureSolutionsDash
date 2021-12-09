import streamlit as st
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime as dt
from data.programs import Programs, TM_list, OTC_with_addons
from data.employee_lists import tick_employees, turf_employees, all_employees
from functions import make_datetime
from functions import Goals
from functions import get_production_perMonth, set_color
today = dt.date.today()
low_date = dt.date(2021,4,1)
total_num_days = (today - low_date).days

choice_converts = {
    'All': [Programs, all_employees],
    'T&M': [TM_list, all_employees],
    'Turf': [OTC_with_addons, turf_employees]
}

#def get_num_service_techs(row):



def app():
    #### LOAD DATA ####
    csv = pd.read_csv('data/clean/production/tick_production_analysis.csv')
    csv2 = pd.read_csv('data/clean/production/turf_production_analysis.csv')
    csv3 = pd.read_csv('data/clean/revenue/revenue_goals.csv')
    csv4 = pd.read_csv('data/clean/production/tick_routes.csv')
    csv5 = pd.read_csv('data/clean/revenue/clean_revenue.csv')
    df_tick_prod = pd.DataFrame(csv)
    df_turf_prod = pd.DataFrame(csv2)
    df_goals = pd.DataFrame(csv3)
    df_routes = pd.DataFrame(csv4)
    df_rev = pd.DataFrame(csv5)
    df_tick_prod = df_tick_prod.loc[df_tick_prod['RouteCodeDescription'].isin(tick_employees)]
    df_turf_prod = df_turf_prod.loc[df_turf_prod['RouteCodeDescription'].isin(turf_employees)]
    df_routes_by_employee = df_routes[[
        'EmployeeName',
        'FormattedDate',
        'ActualMiles',
        'ProductionRevenue'
    ]]
    df_routes_by_employee = df_routes_by_employee.groupby(['EmployeeName']).agg({
        'FormattedDate': list,
        'ActualMiles': 'sum',
        'ProductionRevenue': 'sum'
    })
    df_routes_by_employee['Revenue/Mile'] = df_routes_by_employee['ProductionRevenue'] / df_routes_by_employee['ActualMiles']
    st.dataframe(df_routes_by_employee)
    choice = st.selectbox('Filter by Program:', ['All', 'T&M', 'Turf'])
    start = st.date_input('Start:', dt.date(2021,1,1))
    end = st.date_input('End:', dt.date.today())
    mask = (make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    df_rev = df_rev.loc[df_rev['ProgramCode'].isin(choice_converts[choice][0].keys())]
    df_rev_clean = df_rev[[
        'DoneDateFormatted',
        'GrossSalesAmount',
        'EmployeeName'
    ]]
    df_rev_clean = df_rev_clean.loc[mask]
    df_rev_grouped = df_rev_clean.groupby(['DoneDateFormatted']).agg({'EmployeeName': [lambda x: list(set(x)), pd.Series.nunique], 'GrossSalesAmount': 'sum'})
    df_rev_grouped.columns = df_rev_grouped.columns.droplevel(1)
    df_rev_grouped.columns = ['Technicians', 'NumberTechnicians', 'Revenue']
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Revenue', 'Number of Technicians')
        )
    fig.add_trace(go.Bar(
        x=df_rev_grouped.index,
        y=df_rev_grouped['Revenue'],
        name='Revenue',
        marker_color='#AB63FA'
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=df_rev_grouped.index,
        y=df_rev_grouped['NumberTechnicians'],
        name='NumberTechs',
        marker_color='#FFA15A'
    ), row=1, col=2)
    st.plotly_chart(fig)
    st.dataframe(df_rev_grouped)  

    df_corr = df_rev.loc[(make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(dt.date(2016, 1, 1))) & (make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))]
    df_corr = df_corr[['DoneDateFormatted', 'DoneDateYear', 'GrossSalesAmount', 'EmployeeName']].groupby('DoneDateFormatted').agg({'DoneDateYear': pd.Series.mode, 'GrossSalesAmount': 'sum', 'EmployeeName': pd.Series.nunique}).reset_index().drop(columns=['DoneDateFormatted'])
    df_corr = df_corr.groupby('DoneDateYear').apply(lambda df: df['GrossSalesAmount'].corr(df['EmployeeName']))
    df_corr = pd.DataFrame(df_corr, columns=['Correlation'])
    st.markdown(f'''
    **Correlation Between Daily Revenue and Number of Technicians (by Year)**
    ''')
    st.dataframe(df_corr)
    st.markdown(f'''
    **Meaning:** \n
    \t If correlation is close to 1, more technicians = more revenue \n
    \t If correlation is close to 0, more technicians ≠ more revenue
    ''')

    #### T&M ANALYSIS ####
    tick_num_prod_days = int(df_tick_prod.at[df_tick_prod.index[0], 'TotalOfDistinctProductionDays'])
    
    tick_avg_total_daily_rev = df_tick_prod['AverageRevenuePerDay'].sum()
    tick_max_total_daily_rev = tick_avg_total_daily_rev*1.2
    tick_percent_days_worked = tick_num_prod_days / total_num_days
    tick_avg_emp_production = df_tick_prod['AverageRevenuePerDay'].mean()
    tick_max_emp_production = tick_avg_emp_production*1.2

    df_tick_combine = pd.DataFrame(data={
        'Days': [28, 29, 30, 31]
    })
    
    df_capabilities = df_goals[['Month', 'Days']]

    df_tick_combine['AvgMonthlyProduction'] = df_tick_combine.apply(lambda row: get_production_perMonth(row, tick_avg_total_daily_rev, tick_percent_days_worked), axis=1)
    df_tick_combine['EstMaxMonthlyProduction'] = df_tick_combine['AvgMonthlyProduction']*1.2

    st.markdown(f'''
    ## **Tick Production Stats** ## \n
    ** Average Number Production Days** \n
    For any given month, we can expect the T&M team to service about **{tick_percent_days_worked*100:.2f}%** of days. \n
    *EXAMPLE*: For a **30-day month**, we can expect to have about **{tick_percent_days_worked*30:.0f}** days of production. \n
    ** Individual Technician Production ** \n
    Below are the following statistics for daily revenue produced per individual technician. \n
        AVERAGE: ${tick_avg_emp_production:,.2f} \n
        MAXIMUM: ${tick_max_emp_production:,.2f} \n
    *NOTE: Maximum production values are calculated using the assumption that, for any given technician,
    we expect that their maximum production capability is about 20% more than their average.* \n
    ** Technician Team Production ** \n
    Below are the following statistics for daily revenue produced for the entire T&M team. \n 
        AVERAGE: ${tick_avg_total_daily_rev:,.2f} \n
        MAXIMUM: ${tick_max_total_daily_rev:,.2f} \n
    ** Estimated Average Production per Month ** \n
    Based on average total daily revenue and number of production days, we earn on average the following given months with the given number of days below: \n
        {int(df_tick_combine.at[df_tick_combine.index[0], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[0], 'AvgMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[1], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[1], 'AvgMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[2], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[2], 'AvgMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[3], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[3], 'AvgMonthlyProduction']:,.2f} \n
    *EXAMPLE: for any given month with {int(df_tick_combine.at[df_tick_combine.index[2], 'Days'])} days, we can expect to earn a monthly revenue of about ${df_tick_combine.at[df_tick_combine.index[2], 'AvgMonthlyProduction']:,.2f}* \n
    ** Estimated Max Production per Month ** \n
    Based on maximum dailu revenue and number of production days, we estimate that we can earn a maximum of the following given the number of days below: \n
        {int(df_tick_combine.at[df_tick_combine.index[0], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[0], 'EstMaxMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[1], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[1], 'EstMaxMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[2], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[2], 'EstMaxMonthlyProduction']:,.2f} \n
        {int(df_tick_combine.at[df_tick_combine.index[3], 'Days'])}: ${df_tick_combine.at[df_tick_combine.index[3], 'EstMaxMonthlyProduction']:,.2f} \n
    *EXAMPLE: for any given month with {int(df_tick_combine.at[df_tick_combine.index[2], 'Days'])} days, we can expect that our maximum monthly production capability will be about ${df_tick_combine.at[df_tick_combine.index[2], 'EstMaxMonthlyProduction']:,.2f}* \n
    *NOTE: Maximum production values are calculated using the assumption that, for any given technician, we expect that their maximum production capability is about 20% more than their average.* \n
    ''')

    Goal = st.selectbox('Choose Revenue Goal:', list(Goals.keys()))
    goal_label = Goals[Goal]
    df_capabilities['EstProductionDays'] = np.round(df_capabilities['Days']*tick_percent_days_worked, 0)
    df_capabilities['PestGoal'] = df_goals[f'Pest {goal_label}'].loc[df_goals['Month'] == df_capabilities['Month']]
    df_capabilities['TotalGoal'] = df_goals[f'Total {goal_label}'].loc[df_goals['Month'] == df_capabilities['Month']]
    df_capabilities['EstAvgProduction'] = df_capabilities.apply(lambda row: get_production_perMonth(row, tick_avg_total_daily_rev, tick_percent_days_worked), axis=1)
    df_capabilities['EstMaxProduction'] = df_capabilities['EstAvgProduction']*1.2
    df_capabilities['DifferenceAtAvgProd'] = df_capabilities['EstAvgProduction'] - df_capabilities['PestGoal']
    df_capabilities['DifferenceAtMaxProd'] = df_capabilities['EstMaxProduction'] - df_capabilities['PestGoal']
    st.dataframe(df_capabilities)

    month = st.selectbox('Choose Month:', df_capabilities['Month'].unique())


    df_graph = pd.DataFrame(data={
        'TotalNumTechs': range(10, 31)
    })
    df_graph['NetAdditionalTechs'] = df_graph['TotalNumTechs'] - len(df_tick_prod.index)
    df_graph['EstProductionAtAvgProd'] = df_graph['TotalNumTechs']*(list(df_capabilities['EstProductionDays'].loc[df_capabilities['Month'] == month])[0]*tick_avg_emp_production)
    df_graph['EstProductionAtMaxProd'] = df_graph['TotalNumTechs']*(list(df_capabilities['EstProductionDays'].loc[df_capabilities['Month'] == month])[0]*tick_max_emp_production)   
    df_graph['DifferenceAtAvgProd'] = df_graph['EstProductionAtAvgProd'] - list(df_capabilities['PestGoal'].loc[df_capabilities['Month'] == month])[0]
    df_graph['DifferenceAtMaxProd'] = df_graph['EstProductionAtMaxProd'] - list(df_capabilities['PestGoal'].loc[df_capabilities['Month'] == month])[0]
    st.dataframe(df_graph)

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Scatter(
            x = df_graph['NetAdditionalTechs'],
            y = df_graph['DifferenceAtAvgProd'],
            name = 'Revenue Over Goal (At Average Production)',
            marker=dict(
                color=(
                    list(map(set_color, df_graph['DifferenceAtAvgProd']))
                )
            ),
            mode='markers+lines'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x = df_graph['NetAdditionalTechs'],
            y = df_graph['DifferenceAtMaxProd'],
            name = 'Revenue Over Goal (At Maximum Production)',
            marker=dict(
                color=(
                    list(map(set_color, df_graph['DifferenceAtMaxProd']))
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
        title=f'''Difference in Estimated Revenue and Goal for the Month of {month} (${Goal} Goal)''',
        xaxis_title='Additional Employees',
        yaxis_title=f'''Est. Revenue Minus Rev. Goal for {month}'''
    )
    st.plotly_chart(fig)


