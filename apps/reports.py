import streamlit as st
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
from data.programs import Programs, TM_list, OTC_with_addons, Snow, Miscellaneous
from functions import get_clean_data, get_summary
from functions import format_percentages, get_year_end_results, months

stat_conversions = {
    'Sum': [pd.Series.sum, 'Total'],
    'Mean': [pd.Series.mean, 'Average'],
    'Median': [pd.Series.median, 'Median'],
    'Minimum': [pd.Series.min, 'Minimum'],
    'Maximum': [pd.Series.max, 'Maximum']
}

def app():
    df_paths = {
        'Sales': 'data/clean/sales/sales_1522.csv',
        'Revenue': 'data/clean/revenue/clean_revenue.csv'
    }

    start = st.sidebar.date_input('Start:', dt.date(2021,1,1))
    end = st.sidebar.date_input('End:', dt.date.today()-timedelta(1))
    choice = st.selectbox('Choose Data:', list(df_paths.keys()))
    df = get_clean_data(df_paths[choice], low_memory=False)
    csv_goals = pd.read_csv('data/clean/revenue/revenue_goals.csv')
    df_goals = pd.DataFrame(csv_goals).set_index('Month')
    if choice == 'Sales':
        numeric_cols = ['TotalPrice', 'ProgramSize']
    elif choice == 'Revenue':
        numeric_cols = ['GrossSalesAmount', 'Size']

    pre_select_option = st.selectbox(
        'Program quick select',
        ['None', 'All', 'Tick & Mosquito', 'Turf Care + Addons', 'Snow', 'Miscellaneous']
    )

    pre_selects = {
        'Tick & Mosquito': TM_list,
        'Turf Care + Addons': OTC_with_addons,
        'Snow': Snow,
        'Miscellaneous': Miscellaneous,
        'All': Programs
    }

    if 'FZ' in OTC_with_addons.keys():
        del OTC_with_addons['FZ'] 
    
    if pre_select_option in pre_selects.keys():
        insert = pre_selects[pre_select_option]
        programs = st.multiselect(
            'Choose Programs to Include:', 
            list(Programs.keys()),
            default = list(insert.keys())
            )
    else:
        programs = st.multiselect(
            'Choose Programs to Include:', 
            list(Programs.keys())
            )
    
    column_of_interest = st.selectbox('Choose Stat:', numeric_cols)
    branch_list = [x for x in list(df['Branch'].unique())] #if str(x) != 'nan']
    state_list = [x for x in list(df['State'].unique())] #if str(x) != 'nan' and len(str(x)) > 1 and str(x).isalpha()]
    branches = st.multiselect('Choose branches to include:', sorted(branch_list), default=sorted(branch_list))
    states = st.multiselect('Choose states to include:', sorted(state_list), default=sorted(state_list))
    try:
        get_summary(df=df, column_of_interest=column_of_interest, start=start, end=end, choice=choice, programs=programs, branches=branches, states=states)
    except IndexError:
        st.write('No program selected / No sales for given criteria.')
    
    df_graph = get_year_end_results(df, 2016, 2022, start_date_string=start.strftime('%m/%d'), end_date_string=end.strftime('%m/%d'))
    df_diff = df_graph.diff(periods=1)
    #df_graph.loc['Average', :] = df_graph.agg(np.nanmean, axis=0)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'{choice} Amount', 'Percentage Growth')
        )
    fig.add_trace(go.Bar(
        x=df_diff.index[1:],
        y=df_diff['T&M'][1:],
        name='T&M',
        legendgroup='T&M',
        marker_color='#FFA15A'
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=df_diff.index[1:],
        y=df_diff['OTC'][1:],
        name='OTC',
        legendgroup='OTC',
        marker_color='#00CC96'
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=df_diff.index[1:],
        y=df_diff['Total'][1:],
        name='Total',
        legendgroup='Total',
        marker_color='#AB63FA'
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=df_graph.index[1:],
        y=df_graph['T&M Growth'][1:],
        name='T&M',
        legendgroup='T&M',
        showlegend=False,
        marker_color='#FFA15A'
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=df_graph.index[1:],
        y=df_graph['OTC Growth'][1:],
        name='OTC',
        legendgroup='OTC',
        showlegend=False,
        marker_color='#00CC96'
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=df_graph.index[1:],
        y=df_graph['Total Growth'][1:],
        name='Total',
        legendgroup='Total',
        showlegend=False,
        marker_color='#AB63FA'
    ), row=1, col=2)
    fig.update_layout(
        title=f'''YoY {choice} Growth by Program ({start.strftime('%m/%d')} - {end.strftime('%m/%d')})''', 
        barmode='group'
        )

    df_graph_format = df_graph
    df_graph_format['T&M'] = df_graph_format['T&M'].map('${:,.2f}'.format)
    df_graph_format['OTC'] = df_graph_format['OTC'].map('${:,.2f}'.format)
    df_graph_format['Total'] = df_graph_format['Total'].map('${:,.2f}'.format)
    df_graph_format['T&M Growth'] = df_graph_format.apply(lambda row: format_percentages(row, 'T&M Growth'), axis=1)
    df_graph_format['OTC Growth'] = df_graph_format.apply(lambda row: format_percentages(row, 'OTC Growth'), axis=1)
    df_graph_format['Total Growth'] = df_graph_format.apply(lambda row: format_percentages(row, 'Total Growth'), axis=1)
    
    st.markdown(f'''**Yearly {choice} Amount + Growth by Program ({start.strftime('%m/%d')} - {end.strftime('%m/%d')})**''')
    st.dataframe(df_graph_format)
    st.plotly_chart(fig)

### SERVICES PER MONTH ###
    st.markdown(f'''**Average Number of Services Per Month**''')
    csv_services_perMonth = pd.read_csv('data/clean/revenue/average_services_per_month.csv')
    df_services_perMonth = pd.DataFrame(csv_services_perMonth)
    [df_services_perMonth.drop(columns=[i], inplace=True) for i in df_services_perMonth.columns if 'Unnamed' in i]

    program_choice = st.selectbox('Choose Program:', sorted(list(df_services_perMonth['ProgramCode'].unique())))
    stat_choice = st.selectbox('Choose Summary Statistic: ', list(stat_conversions.keys()))
    df_services_filter = df_services_perMonth.loc[df_services_perMonth['ProgramCode'] == program_choice]
    df_services_filter = df_services_filter.drop(columns=['DoneDateMonthYear'])\
        .groupby(by=['Month']).agg(stat_conversions[stat_choice][0])\
        .reindex(months)

    fig2 = go.Figure(
        data=[go.Bar(
            x=df_services_filter.index,
            y=df_services_filter['NumServices'],
        
        )]
    )
    fig2.update_layout(
        title=f'{program_choice} {stat_conversions[stat_choice][1]} Number of Services per Month (2016 - 2021)',
        xaxis_title='Month',
        yaxis_title='Number of Services'
    )
    st.plotly_chart(fig2)

### REVENUE GOALS ###
    st.markdown(f'''**Monthly Revenue Goals**''')
    st.dataframe(df_goals)
    