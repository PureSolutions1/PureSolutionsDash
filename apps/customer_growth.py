import streamlit as st
import pandas as pd
import plotly.express as px
from functions import get_customer_growth_data, fix_programCode, make_bar, choices

def app():
    csv = pd.read_csv('data/clean/customers/customer_lifeSpan.csv', index_col='Unnamed: 0')
    df_customers = pd.DataFrame(csv)
    df_monthly = get_customer_growth_data(
        'data/clean/customers/cg_monthly.csv'
    )
    df_yearly = get_customer_growth_data(
        'data/clean/customers/cg_yearly.csv'
    )
    df_monthly['ProgramCode'] = df_monthly.apply(lambda row: fix_programCode(row), axis=1)
    df_yearly['ProgramCode'] = df_yearly.apply(lambda row: fix_programCode(row), axis=1)

    df_group = df_customers.groupby(['Status', 'CustomerType']).mean()
    df_group = df_group.reset_index()
    st.dataframe(df_group)
    st.plotly_chart(px.bar(
        df_group,
        x='Status',
        y='LifeSpan (Years)',
        color='CustomerType',
        title='Average Customer Lifespan (By Status and Type)'
    ))

    select = st.selectbox('Stats:', list(choices.keys()))
    make_bar(df_monthly, select)
    st.dataframe(df_monthly)


