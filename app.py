import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import streamlit as st
from rq import Queue
from dotenv import load_dotenv
from worker import conn
from utils import initialize, run
load_dotenv()

if __name__ == '__main__':
    st.set_page_config(
        page_title='Pure Dash',
        page_icon='images/pure_icon2.ico'
    )
    q = Queue(connection=conn)
    result = q.enqueue(initialize, 'http://heroku.com')
    run()
