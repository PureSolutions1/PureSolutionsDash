from __future__ import print_function
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import httplib2
import os
 
# from apiclient import discovery
# Commented above import statement and replaced it below because of 
# reader Vishnukumar's comment
# Src: https://stackoverflow.com/a/30811628
 
import googleapiclient.discovery as discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from data.employee_lists import all_employees
from difflib import get_close_matches
 
import datetime
 
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
 
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'data/token.json'
APPLICATION_NAME = 'GoodToGo'
all_employees = [i.upper() for i in all_employees] + ['CHRIS POLACK', 'MARC TISME', 'JUSTIN DEVEAUX']
all_employees_firsts = [i.split(' ')[0] for i in all_employees]
all_employees_lasts = [i.split(' ')[1] for i in all_employees]

def get_credentials():
    """Gets valid user credentials from storage.
 
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
 
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'token.json')
 
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
 
 
def main():
    """Shows basic usage of the Google Calendar API.
 
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
 
    # This code is to fetch the calendar ids shared with me
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/calendarList/list
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        '''
        for calendar_list_entry in calendar_list['items']:
            print('-'*100, '\n', calendar_list_entry, '\n')
        '''
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
 
    # This code is to look for all-day events in each calendar for the month of September
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/events/list
    # You need to get this from command line
    # Bother about it later!
    start_date = datetime.datetime(2021, 1, 1, 0, 0, 0, 0).isoformat() + 'Z'
    end_date = datetime.datetime(2021, 12, 31, 23, 59, 59, 0).isoformat() + 'Z'
    

    eventsResult = service.events().list(
        calendarId='purepestmanagement.com_ve9a6i8hds6e7od0jkbakbsmbk@group.calendar.google.com',
        timeMin=start_date,
        timeMax=end_date,
        singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    sick_posts = []
    matches = ['OUT']
    cancel_matches = ['EARLY', 'OUT AT', 'LEAH', 'SPENCER', 'JEFF', 'COLLIN']#['CHILD', 'WIFE']
    for message in events:
        if any(x.upper() in message['summary'].upper() for x in matches):
            if any(y.upper() in message['summary'].upper() for y in cancel_matches):
                pass
            else:
                sick_posts.append(message['summary'].upper())
    
    #print(sick_posts)
    #print(len(sick_posts))
    
    employee_counts = {}
    for i in all_employees_firsts:
        employee_counts[i] = 0
    print(employee_counts)

    for i in sick_posts:
        split = i.split(' ')
        if 'OUT' in split[1]:
            name = split[0]
        else:
            last_name = split[1]
            bad = ".:"
            for char in bad:
                last_name = last_name.replace(char, "")
            name = f'{split[0]} {last_name}'
        print('-'*100)
        print(name.split(' ')[0])
        try:
            employee_counts[name.split(' ')[0]] += 1
        except KeyError:
            print(name.split(' ')[0])
            pass
    
    print(employee_counts)

    
if __name__ == '__main__':
    main()