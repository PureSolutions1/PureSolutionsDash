import streamlit as st
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime as dt
from datetime import timedelta
from download_button import download_link
from data.employee_lists import tick_employees
from functions import get_clean_data
from functions import get_tick_employee_results
from functions import get_average_weekly_hours, get_tick_product_data, get_average, get_profit_per_service
from functions import timezz, reverse_rank_metrics
from functions import tick_composite_cols, make_property_size_histogram
rate = None
max_rate = None
today = dt.datetime.today()
first_of_week = (dt.datetime.today() - dt.timedelta(days = dt.datetime.today().isoweekday() % 7)).day
currentMonth = dt.datetime.now().month

colors = {
    'North': px.colors.qualitative.Vivid[1],
    'Metro West': px.colors.qualitative.Vivid[0],
    'South': px.colors.qualitative.Vivid[2]
}

def get_percent_fullDays(row, df_time, start, end, index): 
    full_days_list = [row['NumFullProdDays'] / len(df_time.loc[(df_time['ReportDateFormatted'].dt.date >= start) &\
                            (df_time['ReportDateFormatted'].dt.date <= end) &\
                            (df_time['MainGroupDescriptionDisplayName'] == row.name)
                            ]),
            len(df_time.loc[(df_time['ReportDateFormatted'].dt.date >= start) &\
                            (df_time['ReportDateFormatted'].dt.date <= end) &\
                            (df_time['MainGroupDescriptionDisplayName'] == row.name)
                            ])]
    try:
        return full_days_list[index]
    except:
        pass

def get_average_over_time(row, rowName, df, stat_choice):
    return stat_choice(df[rowName].loc[df['Date'] <= row['Date']])

def app():
    adjust_rev = st.sidebar.checkbox('Adjust Vineyard Revenue?')
    if adjust_rev:
        rev_col = 'GrossSalesAdjusted'
    else:
        rev_col = 'GrossSalesAmount'

    # Load Data
    df_tick = get_clean_data(
        'data/clean/revenue/clean_revenue.csv',
        low_memory=False
    )
    df_tick['DoneDateFormatted'] = pd.to_datetime(df_tick['DoneDateFormatted'], format='%Y-%m-%d')

    csv = pd.read_csv('data/clean/employee_hours/employee_hours.csv')
    df_hours = pd.DataFrame(csv)
    df_hours['ReportDateFormatted'] = pd.to_datetime(df_hours['ReportDateFormatted'], format='%m/%d/%Y')
    csv2 = pd.read_csv('data/clean/production/tick_production_analysis.csv')
    df_prod = pd.DataFrame(csv2)

    time_frame = st.sidebar.selectbox(
    'Time Frame:',
    list(timezz.keys())
    )
    start = st.sidebar.date_input('Start:', dt.date(2021,1,1))
    end = st.sidebar.date_input('End:', dt.date.today())

    stat_choice = st.selectbox(
            'Mean or Median?', 
            ['Median', 'Mean']
            )

    csv4 = pd.read_csv('data/clean/employee_hours/tick_first_services.csv')
    df_first_services = pd.DataFrame(csv4)
    df_first_services = df_first_services.rename(columns={
        'AverageSpeedToFirstService': 'SpeedToFirstService'
    })
    df_first_services['Date'] = pd.to_datetime(df_first_services['Date'], format='%Y-%m-%d')
    mask1 = (df_first_services['Date'] >= pd.to_datetime(start,format='%Y-%m-%d')) &\
            (df_first_services['Date'] <= pd.to_datetime(end,format='%Y-%m-%d')) &\
            (df_first_services['SpeedToFirstService'] > 0)

    df_first_services = df_first_services.loc[mask1]
    df_first_services = df_first_services.loc[(df_first_services['SpeedToFirstService'] > 0) & (df_first_services['SpeedToFirstService'] < 60)]

    csv5 = pd.read_csv('data/clean/employee_hours/tick_inbetween_services.csv')
    df_inbetween_services = pd.DataFrame(csv5)
    df_inbetween_services['Date'] = pd.to_datetime(df_inbetween_services['Date'], format='%Y-%m-%d')
    mask2 = (df_inbetween_services['Date'] >= pd.to_datetime(start,format='%Y-%m-%d')) &\
            (df_inbetween_services['Date'] <= pd.to_datetime(end,format='%Y-%m-%d')) &\
            (df_inbetween_services['SpeedToNextService'] > 0)

    df_inbetween_services = df_inbetween_services[mask2]
    df_inbetween_services = df_inbetween_services.rename(columns={'MilesToNextAddress': 'MilesToNextService', 'TimeToNextService': 'HoursToNextService'})
    df_inbetween_services = df_inbetween_services.drop(columns=['Unnamed: 0'])
    if stat_choice=='Median':
        df_first_services_group = df_first_services.groupby(by=['EmployeeName']).agg(pd.Series.median)
        df_inbetween_services_group = df_inbetween_services.groupby(by=['EmployeeName']).agg(pd.Series.median)
    else:
        df_first_services_group = df_first_services.groupby(by=['EmployeeName']).agg(pd.Series.mean)
        df_inbetween_services_group = df_inbetween_services.groupby(by=['EmployeeName']).agg(pd.Series.mean)

    df_time_services = df_first_services_group.merge(df_inbetween_services_group, left_index=True, right_index=True)
    df_time_services = df_time_services[['SpeedToFirstService', 'SpeedToNextService', 'MilesToFirstService', 'MilesToNextService', 'HoursToFirstService', 'HoursToNextService']]
    st.markdown(f'''
    ** {stat_choice} Time, Distance and Speed to First and Next Properties (July-Current 2021)**
    ''')
    st.dataframe(df_time_services)
    st.write(f'''Correlation Between Distance and Speed (First Services): {np.corrcoef(df_first_services['SpeedToFirstService'], df_first_services['MilesToFirstService'])[0,1]}''')
    st.write(f'''Correlation Between Distance and Speed (In Between Services): {np.corrcoef(df_inbetween_services['SpeedToNextService'], df_inbetween_services['MilesToNextService'])[0,1]}''')

    
    employee_choice = st.selectbox(
            'Select Employee', 
            tick_employees
            )
    employee_first_df = df_first_services.loc[df_first_services['EmployeeName'] == employee_choice]
    [employee_first_df.drop(columns=[i], inplace=True) for i in employee_first_df.columns if 'Unnamed' in i]
    if stat_choice=='Median':
        employee_first_df['FirstPropSpeedToDate'] = employee_first_df.apply(lambda row: get_average_over_time(row, 'SpeedToFirstService', employee_first_df, pd.Series.median), axis=1)
        employee_first_df['10DayFirstPropSpeed'] = employee_first_df['SpeedToFirstService'].rolling(window=10).median()
        employee_next_df = df_inbetween_services.loc[df_inbetween_services['EmployeeName'] == employee_choice]\
            .groupby(by=['Date']).agg(pd.Series.median).reset_index()
        employee_next_df['NextPropSpeedToDate'] = employee_next_df.apply(lambda row: get_average_over_time(row, 'SpeedToNextService', employee_next_df, pd.Series.median), axis=1)
        employee_next_df['10DayNextPropSpeed'] = employee_next_df['SpeedToNextService'].rolling(window=10).median()

    else:
        employee_first_df['FirstPropSpeedToDate'] = employee_first_df.apply(lambda row: get_average_over_time(row, 'SpeedToFirstService', employee_first_df, pd.Series.mean), axis=1)
        employee_first_df['10DayFirstPropSpeed'] = employee_first_df['SpeedToFirstService'].rolling(window=10).mean()
        employee_next_df = df_inbetween_services.loc[df_inbetween_services['EmployeeName'] == employee_choice]\
            .groupby(by=['Date']).agg(pd.Series.mean).reset_index()
        employee_next_df['NextPropSpeedToDate'] = employee_next_df.apply(lambda row: get_average_over_time(row, 'SpeedToNextService', employee_next_df, pd.Series.mean), axis=1)
        employee_next_df['10DayNextPropSpeed'] = employee_next_df['SpeedToNextService'].rolling(window=10).mean()

    [employee_next_df.drop(columns=[i], inplace=True) for i in employee_next_df.columns if 'Unnamed' in i]

    st.markdown(f'** {employee_choice} 10-Day {stat_choice} Speed to First and Next Properties Over Time **')
    fig2 = make_subplots(rows=1, cols=2, 
        subplot_titles=(f'10-Day {stat_choice} Speeds (7/1-to-Date)', f'Speeds by Day')
    )
    fig2.add_trace(go.Scatter(
        x = employee_first_df['Date'],
        y = employee_first_df['10DayFirstPropSpeed'],
        mode = 'lines+markers',
        name = f'10-Day {stat_choice} First Service Speed',
        legendgroup='First'
        ),
        row=1, col=1
    )    
    fig2.add_trace(go.Scatter(
        x = employee_next_df['Date'],
        y = employee_next_df['10DayNextPropSpeed'],
        mode = 'lines+markers',
        name = f'10-Day {stat_choice} In-between Speed',
        legendgroup='Inbetween'
        ),
        row=1, col=1
    )
    fig2.add_trace(go.Scatter(
        x = employee_first_df['Date'],
        y = employee_first_df['SpeedToFirstService'],
        mode = 'lines+markers',
        name = 'Daily First Speeds',
        legendgroup='First'
        ),
        row=1, col=2
    )    
    fig2.add_trace(go.Scatter(
        x = employee_next_df['Date'],
        y = employee_next_df['SpeedToNextService'],
        mode = 'lines+markers',
        name = 'Daily In-between Speeds',
        legendgroup='Inbetween'
        ),
        row=1, col=2
    )
    fig2.update_xaxes(
        tickangle=45,
        title_text = 'Date'
    )
    fig2.update_yaxes(
        title_text = 'Speed (MPH)'
    )
    st.plotly_chart(fig2)


    csv_EODs = pd.read_csv('data/clean/employee_hours/missed_accounts.csv')
    df_EODs = pd.DataFrame(csv_EODs).set_index('index')
    [df_EODs.drop(columns=[i], inplace=True) for i in df_EODs.columns if 'Unnamed' in i]
    st.markdown(f'''**Accounts Unfinished by Employee**''')
    st.dataframe(df_EODs)
    fig3 = px.bar(df_EODs, x=df_EODs.index, y=df_EODs['Accounts/Week'])
    fig3.update_layout(
        title = 'Number of Accounts Missed / Week (Mon - Fri)',
        xaxis_title = 'Employee Name',
        yaxis_title = 'Accounts per Week'
    )           
    st.plotly_chart(fig3)

    df_prod = df_prod[['RouteCodeDescription', 'ProductionDays', 'AverageRevenuePerDay', 'AverageSizePerDay', 'TotalOfDistinctProductionDays']]
    df_prod = df_prod.loc[df_prod['RouteCodeDescription'].isin(tick_employees)]
    df_prod = df_prod.set_index('RouteCodeDescription')

    df_tick = df_tick.loc[(df_tick['DoneDateFormatted'] >= pd.to_datetime(start, format='%Y-%m-%d')) & (df_tick['DoneDateFormatted'] <= pd.to_datetime(end, format='%Y-%m-%d'))]
    df_prod_sum = df_tick.loc[df_tick['EmployeeName'].isin(tick_employees)].groupby(by=['EmployeeName', 'DoneDateFormatted']).sum()
    df_prod_sum = df_prod_sum.loc[df_prod_sum['GrossSalesAmount'] > 500].reset_index()
    df_prod_production_days = df_prod_sum.groupby(by=['EmployeeName']).agg({'GrossSalesAmount': pd.Series.count})\
        .rename(columns={'GrossSalesAmount': 'NumFullProdDays'})
    '''
    df_prod_production_days['TotalProdDays'] = df_prod_production_days.apply(lambda row: get_percent_fullDays(row, df_hours, start, end, 1), axis=1)
    df_prod_production_days['%DaysFull'] = df_prod_production_days.apply(lambda row: get_percent_fullDays(row, df_hours, start, end, 0), axis=1)

    df_prod_production_days = df_prod_production_days[['NumFullProdDays', 'TotalProdDays', '%DaysFull']]
    st.markdown(f'**Full Production Days by Employee**')
    st.dataframe(df_prod_production_days)
    st.markdown('
        *Full production day = days with earned revenue greater than $500*
    ')
    '''


    if end.isoweekday() in range(1, 6):
        first_of_week = end - timedelta(days=end.weekday())
        if first_of_week < start:
            end_alt = end
        else:
            end_alt = first_of_week - dt.timedelta(days=1)
    else:
        end_alt = end

    # Get average weekly hours per employee + results bar chart
    df_hours = get_average_weekly_hours(df_hours, start, end_alt, tick_employees)
    df_hours['Avg. Weekly Pay'] = (df_hours['RegularHours']*19)+(df_hours['OvertimeHours']*(19*1.5))
    df_hours = df_hours.sort_values(by=['TotalHours'], ascending=False)
    st.plotly_chart(px.bar(
        df_hours, 
        x=df_hours.index, 
        y=['OvertimeHours', 'TotalHours'],
        title=f'''Average Num. Hours Worked per Week ({start.strftime('%m/%d/%Y')} - {end_alt.strftime('%m/%d/%Y')})''',
        barmode='group'
    ).add_hline(
        y=40, 
        annotation_text='40 Hours',
        annotation_font_size=16
        ))

    tick_results_production = get_tick_employee_results(df_tick, rev_col=rev_col, start=start, end=end)
    results_prodUsage = get_tick_product_data(time_frame)

    # Combine Dataframes
    df_combine = tick_results_production.join(df_prod, how='outer').join(results_prodUsage, how='outer').join(df_hours, how='outer')
    df_combine = df_combine.join(df_prod_production_days)
    df_combine['Avg. Profit/Day'] = df_combine.apply(lambda row: get_profit_per_service(row), axis=1)
    df_combine['AvgServicesPerDay'] = df_combine['Number of Services'] / df_combine['NumFullProdDays']
    df_combine['AverageRevenuePerDay'] = df_combine['AvgServicesPerDay']*df_combine['Median Revenue/Service ($)']

    df_tick_ranks = pd.DataFrame(index=df_combine.index)
    for i in df_combine.columns:
        if i in reverse_rank_metrics:
            df_tick_ranks[f'{i} Rank'] = df_combine[i].rank(ascending=False)
        else:
            df_tick_ranks[f'{i} Rank'] = df_combine[i].rank(ascending=True)

    tick_select_stats = st.multiselect(
            'Choose Stats to Include in Composite Score:', 
            list(df_combine.columns),
            default = tick_composite_cols
            )
    df_combine['CompositeScore'] = df_tick_ranks.apply(lambda row: get_average(row, tick_select_stats), axis=1)
    # Trick to move last column to first column position
    tick_cols = list(df_combine.columns)
    tick_cols = [tick_cols[-1]] + tick_cols[:-1]
    df_combine = df_combine[tick_cols]
    df_combine = df_combine.sort_values(by=['CompositeScore'], ascending=False)
    df_graph2 = df_combine.sort_values(by=['Treatment/Area'], ascending=False)
    df_graph3 = df_combine.sort_values(by=['Median Servicing Speed (Acres/Hour-on-Sight)'], ascending=False)
    df_graph5 = df_combine.sort_values(by=['Avg. Profit/Day'], ascending=False)
 
    fig = make_subplots(rows=2, cols=2)
    fig.add_trace(
        go.Bar(
            x=df_hours.index,
            y=df_hours['OvertimeHours'],
            name='Average Overtime Hours per Week'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_hours.index,
            y=df_hours['TotalHours'],
            name='Average Total Hours per Week'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_graph2.index,
            y=df_graph2['Treatment/Area'],
            name='Treatment Applied per Area (Gallons/Acre)',
            marker_color='#FFA15A'
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(
            x=df_graph3.index,
            y=df_graph3['Median Servicing Speed (Acres/Hour-on-Sight)'],
            name='Median Servicing Speed (Acres/Hour-on-Sight)',
            marker_color='#00CC96'
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_graph5.index,
            y=df_graph5['Avg. Profit/Day'],
            name='Average Profit per Day ($ Profit/Day)',
            marker_color='#AB63FA'
        ),
        row=2, col=2
    )
    fig.add_hrect(y0=9, y1=11,
        row=1, col=2, 
        annotation_text='Target Range', 
        annotation_position='top right',
        annotation_font_size=16,
        line_width=0, 
        fillcolor='green', 
        opacity=0.5)
    fig.add_hline(y=40, line_dash='dot',
        row=1, col=1,
        annotation_text='40 Hours',
        annotation_font_size=16)
    fig.update_layout(
        title=f'''Employee Stats From {start.strftime('%m/%d')} to {end.strftime('%m/%d')}''', 
        barmode='group'
        )
    fig.update_xaxes(
        tickangle=45,
        tickfont_size=10.5
    )
    st.plotly_chart(fig)
    

    # Download results as CSV
    if st.button('Download Dataframe as CSV'):
        tmp_download_link = download_link(
            df_combine.reset_index(), 
            f"employee_stats_{''.join(filter(str.isalpha, time_frame.lower()))}.csv", 
            'Download data.'
            )
        st.markdown(tmp_download_link, unsafe_allow_html=True)
    st.dataframe(df_combine.sort_values(by=['CompositeScore'], ascending=False))


    chosen_ones = st.multiselect('Choose Employees: ', sorted(tick_employees))
    show_curve = st.checkbox('Show histogram:')
    try:
        if show_curve:
            make_property_size_histogram(df_tick, start, end, chosen_ones, show_hist=True)
        else:
            make_property_size_histogram(df_tick, start, end, chosen_ones, show_hist=False)
    except IndexError:
        st.write('No employees chosen.')
    