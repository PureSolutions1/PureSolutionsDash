import pandas as pd
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import slack
import plotly.express as px
from data.employee_lists import slack_user_ids, tick_employees
from time import sleep
from juicy_secrets import slack_token

CHANNEL = "C01SMBMLNR4"
MESSAGES_PER_PAGE = 1000
MAX_MESSAGES = 1000
MATCHES = ['EOD', 'END OF DAY', 'END OF DAY+', 'OUT OF TIME']
CANCEL_MATCHES = ['WEATHER SENSITIVE', 'DUE TO WEATHER', 'WEATHER', 'ISSUES']

def get_EOD_messages(row, messages, matches, cancel_matches):
    count = 0
    for key in messages.keys():
        if key == row.name:
            for i in messages[key]:
                if any(x.upper() in i.upper() for x in matches):
                    if any(y.upper() in i.upper() for y in cancel_matches):
                        pass
                    else:
                        for line in i.split('\n'):
                            for word in line.split(' '):
                                if word.isnumeric():
                                    count += 1
                                else:
                                    pass
                else:
                    pass
        else:
            pass
    return count


# init web client
client = slack.WebClient(slack_token)

# get first page
page = 1
print("Retrieving page {}".format(page))
response = client.conversations_history(
    channel=CHANNEL,
    limit=MESSAGES_PER_PAGE,
)
assert response["ok"]
messages_all = response['messages']

# get additional pages if below max message and if they are any
while len(messages_all) + MESSAGES_PER_PAGE <= MAX_MESSAGES and response['has_more']:
    page += 1
    print("Retrieving page {}".format(page))
    sleep(1)   # need to wait 1 sec before next call due to rate limits
    response = client.conversations_history(
        channel=CHANNEL,
        limit=MESSAGES_PER_PAGE,
        cursor=response['response_metadata']['next_cursor']
    )
    assert response["ok"]
    messages = response['messages']
    messages_all = messages_all + messages

print(
    "Fetched a total of {} messages from channel {}".format(
        len(messages_all),
        CHANNEL
))

user_ids = []
for dictionary in messages_all:
    try:
        user_ids.append(slack_user_ids[dictionary['user']])
    except KeyError:
        pass

user_ids = set(user_ids)
messages = {}
for id in user_ids:
    messages[id] = []

for dictionary in messages_all:
    try:
        messages[slack_user_ids[dictionary['user']]].append(dictionary['text'])
    except KeyError:
        pass

for dictionary in messages_all:
    try:
        if slack_user_ids[dictionary['user']] == 'Francisco Nieves':
            print('-'*100, '\n', dictionary['text'])
    except KeyError:
        pass

user_end_of_day_messages = {}
df_messages = pd.DataFrame(index=user_ids)
df_messages['Num_Accounts'] = 0
df_messages['Num_Accounts'] = df_messages.apply(lambda row: get_EOD_messages(row, messages, MATCHES, CANCEL_MATCHES), axis=1)

csv_tick = pd.read_csv('data/clean/employee_hours/employee_stats_0915_1208.csv')
df_tick = pd.DataFrame(csv_tick)
df_tick = df_tick.groupby('MainGroupDescription').agg({
    'ReportDateFormatted': pd.Series.nunique
}).reset_index().rename(columns={
    'MainGroupDescription': 'Name',
    'ReportDateFormatted': 'TotalProdDays'
}).set_index('Name')

df_messages = pd.concat([df_messages, df_tick], axis=1)
df_messages['Accounts/Week'] = (df_messages['Num_Accounts'] / df_messages['TotalProdDays'])*5
df_messages = df_messages.sort_values(by=['Accounts/Week'], ascending=False)
df_messages = df_messages.reset_index()
df_messages = df_messages.loc[df_messages['index'].isin(tick_employees)]
df_messages.to_csv('data/clean/employee_hours/missed_accounts.csv')

fig = px.bar(df_messages, x=df_messages['index'], y=df_messages['Accounts/Week'])
fig.update_layout(
    title = 'Number of Accounts Missed / Week (Mon - Fri)',
    xaxis_title = 'Employee Name',
    yaxis_title = 'Accounts per Week'
)           
fig.show()