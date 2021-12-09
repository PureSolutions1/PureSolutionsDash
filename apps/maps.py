import streamlit as st
import streamlit.components.v1 as components

def app():
    st.header('Revenue 2021 Map')
    HtmlFile = open('data/clean/geo/revenue_21.html', 'r', encoding='utf-8').read()
    components.html(HtmlFile, height=600)