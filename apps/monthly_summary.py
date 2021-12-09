import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
from dateutil.relativedelta import relativedelta
from data.programs import OTC_with_addons
from functions import customer_growth_choices, get_specific_month_data, get_customer_growth_data
from functions import fix_programCode, get_year_end_results, make_multichart
OTC_with_addons['FZ1'] = 'Fertilizer Treatment 1'
previous_month_name = (dt.datetime.now() - relativedelta(months=1)).strftime('%B')
previous_month_int = int((dt.datetime.now() - relativedelta(months=1)).strftime('%m'))

def app():
    # LOAD DATA
    df_sales = get_specific_month_data(
        'data/clean/sales/sales_1522.csv',
        month_num=previous_month_int,
        low_memory=False
    )
    df_revenue = get_specific_month_data(
        'data/clean/revenue/clean_revenue.csv',
        month_num=previous_month_int,
        low_memory=False
    )
    df_cancels = get_specific_month_data(
        'data/clean/cancels/cancels_1522.csv',
        month_num=previous_month_int
    )
    df_customer_growth = get_customer_growth_data(
        'data/clean/customers/cg_monthly.csv'
    )
    df_customer_growth['ProgramCode'] = df_customer_growth.apply(lambda row: fix_programCode(row), axis=1)
    
    # MARKDOWN
    st.markdown(f'''
    # **Sales and Revenue by Program**
    ''')

    # GET YEARLY RESULTS
    yearly_sales = get_year_end_results(df_sales, 2016, 2022)
    yearly_revs = get_year_end_results(df_revenue, 2016, 2022)
    yearly_cancels = get_year_end_results(df_cancels, 2016, 2022)
    yearly_sales_to_cancels = yearly_sales / yearly_cancels

    # YEARLY PLOTS
        # Sales
    st.plotly_chart(px.bar(
        yearly_sales,
        x=yearly_sales.index,
        y=['T&M', 'OTC'],
        title=f'Yearly {previous_month_name} Sales by Program'
    ))
        # Revenue
    st.plotly_chart(px.bar(
        yearly_revs,
        x=yearly_revs.index,
        y=['T&M', 'OTC'],
        title=f'Yearly {previous_month_name} Revenues by Program'
    ))
        # Cancels
    st.plotly_chart(px.bar(
        yearly_cancels,
        x=yearly_cancels.index,
        y=['T&M', 'OTC'],
        title=f'Yearly {previous_month_name} Cancels by Program'
    ))
        # Cancels to Sales
    st.plotly_chart(px.bar(
        yearly_sales_to_cancels,
        x=yearly_sales_to_cancels.index,
        y=['T&M', 'OTC'],
        title=f'Yearly {previous_month_name} Sales:Cancels Ratio by Program'
    ))

    ### YoY GROWTH
    st.markdown(f'''
    # **Yearly Growth for Revenue and Sales by Program**
    ''')
        # Revenue
    st.plotly_chart(px.line(
        data_frame=yearly_revs,
        x=yearly_revs.index,
        y=['T&M Growth', 'OTC Growth', 'Total Growth'],
        title='Revenue Growth YoY (%)'
    ))

        # Sales
    st.plotly_chart(px.line(
        data_frame=yearly_sales,
        x=yearly_sales.index,
        y=['T&M Growth', 'OTC Growth', 'Total Growth'],
        title='Sales Growth YoY (%)'
    ))

        # Rev vs. Sales
    rev_and_sales = pd.DataFrame(index=yearly_sales.index)
    rev_and_sales['Total Sales'] = yearly_sales['Total Growth']
    rev_and_sales['Total Revenue'] = yearly_revs['Total Growth']
    st.plotly_chart(px.line(
        data_frame=rev_and_sales, 
        x=rev_and_sales.index, 
        y=['Total Sales', 'Total Revenue'], 
        title='Sales vs. Revenue Growth YoY (%)'
        ))

    ### CUSTOMER GROWTH ANALYSIS
    st.markdown(f'''
    # **Customer Growth Analysis for {previous_month_name} 2021**
    ''')
    select = st.selectbox('Stats:', list(customer_growth_choices.keys()))
    make_multichart(df_customer_growth, select)