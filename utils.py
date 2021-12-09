from apps import reports, employees, turf_employees, home, weekly_report, maps
from apps import customer_growth, monthly_summary, production_analysis, weather
from multiapp import MultiApp
import streamlit as st
import sys
import os
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import asyncio
import datetime as dt
from dateutil.relativedelta import relativedelta
from httpx_oauth.clients.google import GoogleOAuth2
from dotenv import load_dotenv
from SessionState import get
load_dotenv()
previous_month = (dt.datetime.now() - relativedelta(months=1)).strftime('%B')


try:
    from juicy_secrets import client_id, client_secret
    from juicy_secrets import redirect_uri
except ImportError:
    client_id = os.environ['GOOGLE_CLIENT_ID']
    client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    drive_client_email = os.environ['DRIVE_CLIENT_EMAIL']
    drive_client_id = os.environ['DRIVE_CLIENT_ID']
    redirect_uri = os.environ['REDIRECT_URI']
    refresh_token = os.environ['REFRESH_TOKEN']
    token_id = os.environ['TOKEN_ID']
    token_uri = os.environ['TOKEN_URI']
    scopes = os.environ['SCOPES']
    expiry = os.environ['EXPIRY']

def initialize():
    appl = MultiApp()
    appl.add_app('Home', home.app)
    appl.add_app('Reports', reports.app)
    appl.add_app('Tick Employees', employees.app)
    appl.add_app('Turf Employees', turf_employees.app)
    appl.add_app('Production Analysis', production_analysis.app)
    appl.add_app('Customer Analysis', customer_growth.app)
    appl.add_app('Maps', maps.app)
    appl.add_app('Weekly Report', weekly_report.app)
    appl.add_app(f'{previous_month} Summary', monthly_summary.app)
    appl.add_app('Weather', weather.app)
    appl.run()

async def write_authorization_url(client, redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=['email'],
        extras_params={'access_type': 'offline'},
    )
    return authorization_url

async def write_access_token(client, redirect_uri, code):
    token = await client.get_access_token(code, redirect_uri)
    return token

def authenticate(url='http://heroku.com'):
    client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(
            client=client,
            redirect_uri=redirect_uri
        )
    )
    session_state = get(token=None)
    if session_state.token is None:
        try:
            code = st.experimental_get_query_params()['code']
        except:
            st.write(
                f'''
                <h1>
                Please login here: <a target="_self"
                href="{authorization_url}">Login</a></h1>
                ''',
                unsafe_allow_html=True
            )
        else:
            try:
                token = asyncio.run(write_access_token(
                    client=client,
                    redirect_uri=redirect_uri,
                    code=code
                ))
            except:
                st.write(
                    f'''
                    <h1>
                    This account is not allowed or page was refreshed.
                    Please try again: <a target="_self"
                    href="{authorization_url}">Login</a></h1>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                if token.is_expired():
                    if token.is_expired():
                        st.write(
                            f'''<h1>
                            Login session has ended, please log in again: <a target="_self" 
                            href="{authorization_url}">Login</a></h1>
                            '''
                        )
                else:
                    session_state.token = token
                    initialize()
    else:
        initialize()

def run():
    authenticate()