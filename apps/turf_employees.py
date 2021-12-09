import streamlit as st
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime as dt
from download_button import download_link
from data.products import products
from data.programs import OTC_with_addons
from data.employee_lists import turf_employees
from download_button import download_link
from functions import make_datetime
from functions import get_average_weekly_hours, get_turf_product_data, get_average
from functions import timezz, reverse_rank_metrics
from functions import turf_composite_cols, get_turf_profit_perDay, make_listCol
from functions import get_employee_daily_programs, make_daily_program_graph
from functions import get_revenue_by_programCode
rate = None
max_rate = None
first_of_week = (dt.datetime.today() - dt.timedelta(days = dt.datetime.today().isoweekday() % 7)).day
currentMonth = dt.datetime.now().month

stat_translations = {
    'Number Services': ['TeamServiceNumber', pd.Series.nunique],
    'Square Feet (000s)': ['Size', 'sum'],
    'Revenue': ['GrossSalesAmount', 'sum']
}

def f(row):
    index = min(row['B'].cumsum().searchsorted(1), len(row))
    return row.iloc[0:index+1]

def app():
    '''
    adjust_rev = st.sidebar.checkbox('Adjust Vineyard Revenue?')
    if adjust_rev:
        rev_col = 'GrossSalesAdjusted'
    else:
        rev_col = 'GrossSalesAmount'
    '''
    rev_col = 'GrossSalesAmount'
    csv = pd.read_csv('data/clean/employee_hours/turf_employees.csv')
    csv2 = pd.read_csv('data/clean/employee_hours/employee_hours.csv')
    csv3 = pd.read_csv('data/clean/production/turf_production_analysis.csv')
    csv4 = pd.read_csv('data/clean/revenue/clean_revenue.csv', low_memory=False)
    csv5 = pd.read_csv('data/clean/product_usage/yearly_product_costs.csv')
    turf_results_production = pd.DataFrame(csv)
    df_hours = pd.DataFrame(csv2)
    df_prod = pd.DataFrame(csv3)
    df_rev = pd.DataFrame(csv4)
    df_product_costs = pd.DataFrame(csv5)
    df_prod = df_prod[['RouteCodeDescription', 'ProductionCompleted', 'ProductionDays', 'ProductionSize', 'AverageRevenuePerDay', 'AverageSizePerDay']]
    df_prod = df_prod.loc[df_prod['RouteCodeDescription'].isin(turf_employees)]
    df_prod = df_prod.set_index('RouteCodeDescription')

    time_frame = st.sidebar.selectbox(
    'Time Frame:',
    list(timezz.keys())
    )
    start = st.sidebar.date_input('Start:', timezz['Current Year'][0])
    end = st.sidebar.date_input('Start:', timezz['Current Year'][1])
    mask = (make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') >= make_datetime(timezz['Current Year'][0])) & (make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(timezz['Current Year'][1]))
    
    df_product_costs['ProductCode'] = df_product_costs.apply(lambda row: make_listCol(row, 'ProductCode'), axis=1)
    df_product_costs['TotalRevenue'] = df_product_costs.apply(lambda row: get_revenue_by_programCode(row, df_product_costs, 'AssociatedService', df_rev.loc[mask], 'GrossSalesAmount'), axis=1)
    df_product_costs['Profit'] = df_product_costs['TotalRevenue'] - df_product_costs['Cost']
    st.markdown('''
    **Product Profitability Stats (Year-to-date)**
    ''')
    st.dataframe(df_product_costs)

    st.markdown(f'''
    **General Information by Product**
    ''')

    product_download = st.button('Download Dataframe as CSV', key='Product Data')
    if product_download:
        tmp_download_link = download_link(
            pd.DataFrame.from_dict(products, orient='index').sort_values(['Name']).rename_axis('ProductCode').reset_index(), 
            f"product_info.csv", 
            'Download data.'
            )
        st.markdown(tmp_download_link, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame.from_dict(products, orient='index').sort_values(['Name']).rename_axis('ProductCode').reset_index().set_index('Name'))
    df_use = get_turf_product_data(time_frame)
    df_hours = get_average_weekly_hours(df_hours, start, end, turf_employees)
    df_hours = df_hours.sort_values(by=['TotalHours'], ascending=False)
    st.plotly_chart(px.bar(
        df_hours, 
        x=df_hours.index, 
        y=['OvertimeHours', 'TotalHours'],
        title=f'''Average Num. Hours Worked per Week ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})''',
        barmode='group'
    ))
    product_choice = st.selectbox('Select Product', df_use['ProductDescription'].unique())
    product_code = list(df_use['ProductCode'].loc[df_use['ProductDescription']==product_choice].mode())[0]
    stat_choice = st.selectbox('Select Stat', [f'AmountApplied', 'PropertySize', f'Treatment/Area', 'Cost/Area ($/1000 Ft^2)'])
    if stat_choice == 'AmountApplied':
        units = f" ({products[product_code]['Units']})"
    elif stat_choice == 'Treatment/Area':
        units = f" ({products[product_code]['Units']}/1000 Ft^2)"
    elif stat_choice == 'PropertySize':
        units = f' (000s Ft^2)'
    else:
        units = ''
    df_use_graph = df_use.loc[df_use['ProductDescription'] == product_choice]
    df_use_graph = df_use_graph.sort_values(by=[stat_choice], ascending=False)
    st.plotly_chart(px.bar(
        df_use_graph,
        x=df_use_graph['TechnicianName'],
        y=[stat_choice],
        title=f'''{stat_choice}{units}  for {product_choice}'''
    ))
    df_use_combine = df_use.drop(columns=['ProductDescription'])
    df_use_combine = df_use_combine.groupby(by='TechnicianName').sum()

    st.dataframe(turf_results_production)
    mask = (make_datetime(turf_results_production['DoneDateFormatted'], format='%Y-%m-%d') >= pd.to_datetime(start)) & (make_datetime(turf_results_production['DoneDateFormatted'], format='%Y-%m-%d') <= make_datetime(end))
    turf_results_production = turf_results_production.loc[mask]


    results = {}
    for emp in turf_employees:
        results[emp] = []
        temp_df = turf_results_production.loc[turf_results_production['EmployeeName'] == emp]
        results[emp] = [
            np.nanmean(temp_df[rev_col]),
            np.nanmean(temp_df['CustomerSize']),
            np.nanmean(temp_df['TotalManHours']),
            np.nanmean(temp_df['size_per_hour']), 
            np.nanmean(temp_df['value_per_hour']),
            len(temp_df['IndividualServiceNumber'].unique())
            ]
    
    turf_results_production = pd.DataFrame.from_dict(
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
    turf_results_production = turf_results_production.join(df_prod, how='outer').join(df_use_combine, how='outer').join(df_hours, how='outer')
    turf_results_production['AverageProfitPerDay ($/Day)'] = turf_results_production.apply(lambda row: get_turf_profit_perDay(row), axis=1)
    df_turf_ranks = pd.DataFrame(index=turf_results_production.index)

    for i in turf_results_production.columns:
        if i in reverse_rank_metrics:
            df_turf_ranks[f'{i} Rank'] = turf_results_production[i].rank(ascending=False)
        else:
            df_turf_ranks[f'{i} Rank'] = turf_results_production[i].rank(ascending=True)
    

    turf_select_stats = st.multiselect(
            'Choose Stats to Include in Composite Score:', 
            list(turf_results_production.columns),
            default = turf_composite_cols
            )
    turf_results_production['CompositeScore'] = df_turf_ranks.apply(lambda row: get_average(row, turf_select_stats), axis=1)

    turf_cols = list(turf_results_production.columns)
    turf_cols = [turf_cols[-1]] + turf_cols[:-1]
    turf_results_production = turf_results_production[turf_cols]

    choice = st.selectbox('Choose Stat:', turf_results_production.columns)
    df_graph = turf_results_production.sort_values(by=[choice], ascending=False)
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(
            x=df_graph.index,
            y=df_graph[choice],
            name=f'{choice}',
            marker_color='#A777F1'
        ),
        row=1, col=1
    )
    fig.update_layout(
        showlegend=True,
        title=f'''Employee Stats for {choice}'''
        )
    st.plotly_chart(fig)
    st.dataframe(turf_results_production.sort_values(by=['CompositeScore'], ascending=False))


    chosen_emp = st.selectbox('Choose Employee:', turf_employees+['All'])
    summary_stat_choice = st.selectbox('Choose Stat:', ['Number Services', 'Square Feet (000s)', 'Revenue'])
    df_programs, unique_progs = get_employee_daily_programs(
        df=df_rev,
        start=start,
        end=end,
        employee=chosen_emp,
        choice=stat_translations[summary_stat_choice][0],
        func=summary_stat_choice
    )

    st.dataframe(df_programs)
    if df_programs.empty:
        pass
    else:
        st.plotly_chart(make_daily_program_graph(
            df=df_programs,
            unique_programs=unique_progs,
            all_stats=True,
            title=f'''Daily {summary_stat_choice} for {chosen_emp} ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})''',
            colors=px.colors.qualitative.Light24,
            stat=summary_stat_choice
        ))

        options = []
        for column in df_programs.columns:
            if column.split('_')[0].upper() not in ['ALL', 'OTHER']:
                options.append(f"{column.split('_')[0].upper()}: {OTC_with_addons[column.split('_')[0].upper()]}")
            else:
                continue
        choice = st.selectbox('Choose Program:', options)
        st.dataframe(df_programs)
        df_programs[f'''Other_{''.join(summary_stat_choice.split(' '))}'''] = df_programs[f'''All_{''.join(summary_stat_choice.split(' '))}'''] - df_programs[f'''{choice.split(': ')[0].upper()}_{''.join(summary_stat_choice.split(' '))}''']
        st.plotly_chart(make_daily_program_graph(
            df=df_programs,
            unique_programs=unique_progs,
            all_stats=False,
            title=f'''Daily Count Split by {choice.split(': ')[0]}''',
            choice=choice,
            stat=summary_stat_choice
        ))

        unique_progs.append('All')
        statzz = {
            'ProgramCode': [],
            f'Total {summary_stat_choice}': [],
            f'Average Daily {summary_stat_choice}': [],
            f'Median Daily {summary_stat_choice}': [],
            f'Max Daily {summary_stat_choice}': [],
            'Num. Production Days': []
        }

        for i in range(len(unique_progs)):
            non_zero_stats = df_programs[f'''{unique_progs[i]}_{''.join(summary_stat_choice.split(' '))}'''].loc[df_programs[f'''{unique_progs[i]}_{''.join(summary_stat_choice.split(' '))}''']!=0]
            if len(non_zero_stats)==0:
                continue
            else:
                statzz['ProgramCode'].append(unique_progs[i])
                statzz[f'Total {summary_stat_choice}'].append(round(np.sum(non_zero_stats), 0))
                statzz[f'Average Daily {summary_stat_choice}'].append(f'{round(np.mean(non_zero_stats), 2):,.0f}')
                statzz[f'Median Daily {summary_stat_choice}'].append(round(np.quantile(non_zero_stats, 0.5), 0))
                statzz[f'Max Daily {summary_stat_choice}'].append(f'{np.max(non_zero_stats):,.0f}')
                statzz['Num. Production Days'].append(f'{len(non_zero_stats):,.0f}')
        
        df_allstuff = pd.DataFrame.from_dict(statzz)
        df_allstuff = df_allstuff.set_index('ProgramCode')

        stats_download = st.button('Download Dataframe as CSV', key=f'{chosen_emp} Stats')
        if stats_download:
            tmp_download_link = download_link(
                df_allstuff.reset_index(),
                f'''{chosen_emp.replace(' ', '_')}_{summary_stat_choice.lower().replace(' ', '_')}_stats_{start.strftime('%m%d%Y')}_{end.strftime('%m%d%Y')}.csv''', 
                'Download data.'
                )
            st.markdown(tmp_download_link, unsafe_allow_html=True)
        st.markdown(f'''**Daily {summary_stat_choice} Statistics by Service for {chosen_emp} ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})**''')
        st.dataframe(df_allstuff)
        st.markdown(f'''*NOTE: All calculations only take into account days where technician: {chosen_emp} did 1 or more services of said service.*''')
        st.markdown(f'''**{summary_stat_choice} Stats by Day for {chosen_emp} ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})**''')
        st.dataframe(df_programs)

        single_day_choice = st.date_input('Inspect Particular Day:', dt.date(2021,4,1))
        df_single_day = df_rev.loc[(make_datetime(df_rev['DoneDateFormatted'], format='%Y-%m-%d') == make_datetime(single_day_choice)) & (df_rev['EmployeeName'].isin(turf_employees))]
        '''
        df_single_day = df_single_day[['EmployeeName', 'ProgramCode', 'GrossSalesAmount', 'Size', 'Address', 'City']]\
            .groupby(['EmployeeName', 'ProgramCode']).agg(list)
        '''
        '''
        st.dataframe(df_single_day[['EmployeeName', 'ProgramCode', 'GrossSalesAmount', 'Size', 'Address', 'City']]\
            .sort_values(['EmployeeName', 'ProgramCode']).set_index(['EmployeeName', 'ProgramCode']))
        '''
        st.dataframe(df_single_day[['EmployeeName', 'ProgramCode', 'GrossSalesAmount', 'Size', 'Address', 'City']]\
            .set_index(['EmployeeName', 'ProgramCode']).sort_index())


        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '# Services: All', 
                '# Services: TD', 
                'Square Feet (000s): All',
                'Square Feet (000s): TD')
            )
        fig.add_trace(go.Bar(
            x=df_programs.index,
            y=df_programs['All_NumberServices'],
            name='All: # Services',
            legendgroup='All',
            marker_color='#AB63FA'
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=df_programs.index,
            y=df_programs['TD_NumberServices'],
            name='TD: # Services',
            legendgroup='TD',
            marker_color='#FFA15A'
        ), row=1, col=2)
        fig.add_trace(go.Bar(
            x=df_programs.index,
            y=df_programs['All_SquareFeet(000s)'],
            name='All: Square Feet (000s)',
            legendgroup='All',
            marker_color='#00CC96'
        ), row=2, col=1)
        fig.add_trace(go.Bar(
            x=df_programs.index,
            y=df_programs['TD_SquareFeet(000s)'],
            name='TD: Square Feet (000s)',
            legendgroup='TD',
            #showlegend=False,
            marker_color='#AB63FA'
        ), row=2, col=2)
        fig.update_layout(
            title=f'''**Daily Service Stats Split by All & Top Dressing for {chosen_emp} ({start.strftime('%m/%d/%Y')} - {end.strftime('%m/%d/%Y')})**''', 
            barmode='group'
            )
        st.plotly_chart(fig)