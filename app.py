import json
from datetime import datetime, date, timedelta
import requests
import os
import sys
import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

states = ['AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'CT', 'DL', 'DN', 'GA', 'GJ', 'HP', 'HR', 'JH', 'JK', 'KA', 'KL', 'LA',
          'MH', 'ML', 'MN', 'MP', 'MZ', 'NL', 'OR', 'PB', 'PY', 'RJ', 'TG', 'TN', 'TR', 'TT', 'UP', 'UT', 'WB']

sdate = date(2020, 4, 26)  # start date
edate = datetime.now().date() - timedelta(days=1)
delta_date = edate - sdate  # as timedelta
# print(delta_date.days)
# dates = [sdate + timedelta(days=i) for i in range(delta_date.days + 1)]
dates = []
for i in range(delta_date.days + 1):
    day = sdate + timedelta(days=i)
    dates.append(str(day))
# print(dates)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv(r'data/states/KA_backup.csv')
available_indicators = df['city'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='state',
                options=[{'label': i, 'value': i} for i in states],
                value='KA'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='city',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value=str(available_indicators[0])
            )],
            style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        id='date_slider',
        min=0,
        max=delta_date.days,
        value=delta_date.days,
        marks={str(day): str(day) for day in range(delta_date.days)},
        step=None
    )
])
@app.callback(
    [Output('city', 'options'), Output('city', 'value')],
    [Input('state', 'value')]
)
def update_city_dropdown(name):
    path = r'data/states/{}.csv'.format(name)
    df = pd.read_csv(path)
    cities = df['city'].unique()
    cities.sort()
    return [{'label': i, 'value': i} for i in cities], cities[0]

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('state', 'value'),
     Input('city', 'value'),
     Input('yaxis-type', 'value'),
     Input('date_slider', 'value')])
def update_graph(state, city,
                 yaxis_type,
                 date_value):

    path = r'data/states/{}.csv'.format(state)
    df = pd.read_csv(path)
    # print('df y axis:', df['city'])
    # print('date:', sdate + timedelta(days=date_value))
    # dff = df[df['date'] == sdate + timedelta(days=date_value)]
    dff = df[df['city'] == str(city)]
    x_axis = dff[dff['city'] == str(city)]['date'][:date_value+2]
    y_axis_conf = dff[dff['city'] == str(city)]['confirmed'][:date_value+2]
    y_axis_rec = dff[dff['city'] == str(city)]['recovered'][:date_value+2]
    y_axis_dec = dff[dff['city'] == str(city)]['deceased'][:date_value+2]
    y_axis_act = y_axis_conf - y_axis_rec
    hover = dff[dff['city'] == str(city)]['city'][:date_value+2]

    # print('DFF: ', dff)
    # print(state, city, yaxis_type, date_value)
    # print('x axis: ', x_axis)
    # print('y axis: ', y_axis_conf)

    fig = px.line(title="{}, {}".format(state, city))

    fig.add_trace(go.Scatter(x=x_axis, y=y_axis_conf, name='Confirmed', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=x_axis, y=y_axis_act, name='Active', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=x_axis, y=y_axis_rec, name='Recovered', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=x_axis, y=y_axis_dec, name='Deceased', line=dict(color='brown')))

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 30, 'r': 10})

    fig.update_xaxes(title='Date')

    fig.update_yaxes(title='Number',
                     type='linear' if yaxis_type == 'Linear' else 'log')

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x")

    return fig


class Covid19Logger(object):
    def __init__(self):
        print("Covid19 Logger initialized.")

    def cov_refresh_date_wise_data(self, day):
        '''
        Get all the date till date
        '''

        print('Refreshing data for {} date', day)
        url = 'https://api.covid19india.org/v3/data-' + str(day) + '.json'
        rsp = requests.get(url)
        data = ''
        if rsp.status_code in (200,):
            # This magic here is to cut out various leading characters from the JSON
            # response, as well as trailing stuff (a terminating ']\n' sequence), and then
            # we decode the escape sequences in the response
            # This then allows you to load the resulting string
            # with the JSON module.
            data = rsp.content.decode('utf-8')
            # return data

        # data = json.loads(data)
        # file = r'data/{}_json.txt'.format(day)
        if not data == '':
            file = r'data/{}.csv'.format(day)      # Read write operation on csv was found to be faster
            f = open(file, 'w+')
            f.write(data)
            f.close()

        return

    def cov_get_date_wise_data(self, date):
        '''
        Get data for a particular date. Date has to be in YYYY-MM-DD format
        '''

        # file = r'data/{}_json.txt'.format(date)
        file = r'data/{}.csv'.format(date)      # Read write operation on csv was found to be faster
        # If file does not exists, get data from covid19india.org and save it locally
        if not os.path.isfile(file):
            print("File {} is not present. Getting it from server\n".format(file))
            self.cov_refresh_date_wise_data(date)

        data = ''
        try:
            f = open(file, 'r')
            data = f.read()
            # data = json.loads(data)
        except Exception as e:
            print('Failed to get data for date - {}. Error is {}'.format(date, e))

        return data

    def cov_get_state_data(self, date):
        '''
        Get date wise data for each city
        '''
        data = self.cov_get_date_wise_data(date)
        try:
            data = json.loads(data)
            states = data.keys()
        except Exception as e:
            print("Got exception {} in loading json from data {}".format(e, date))
            raise e
        
        data_dict = ''
        for state in states:
            path = r'data/states/all_states.csv'
            
            '''
            if os.path.exists(path):
                f = open(path, 'a')
                if 'linux' in sys.platform:
                    f.write("'{}',".format(str(state)))
                else:
                    f.write("/'" + str(state) + "/'" + ",")
                f.close()
            else:
                f = open(path, 'a')
                if 'linux' in sys.platform:
                    f.write('States\n')
                else:
                    f.write('States\n')
                f.close()
            '''
                
            try:
                data_dict = data[state]['districts']
                # print(data_dict)
                # Create a file for state
                path = r'data/states/{}.csv'.format(state)
                lines = ''
                if os.path.exists(path):
                    f = open(path, 'r')
                    lines = f.readlines()
                    f.close()
                else:
                    f = open(path, 'w')
                    data_city = 'date,city,confirmed,recovered,deceased,delta_confirmed,delta_recovered\n'
                    if 'linux' in sys.platform:
                        data_city = data_city#.rstrip()
                    f.write(data_city)
                    f.close()

                cities = data_dict.keys()
                for city in cities:
                    # print(state, city)
                    data_city = str(date) + ',' + str(city)

                    try:
                        data_city += ',' + str(data_dict[city]['total']['confirmed'])
                    except Exception as e:
                        # print('____Error:', e)
                        data_city += ',' + '0'

                    try:
                        data_city += ',' + str(data_dict[city]['total']['recovered'])
                    except Exception as e:
                        # print('____Error:', e)
                        data_city += ',' + '0'

                    try:
                        data_city += ',' + str(data_dict[city]['total']['deceased'])
                    except Exception as e:
                        # print('____Error:', e)
                        data_city += ',' + '0'

                    try:
                        data_city += ',' + str(data_dict[city]['delta']['confirmed'])
                    except Exception as e:
                        # print('____Error:', e)
                        data_city += ', ' + '0'

                    try:
                        data_city += ',' + str(data_dict[city]['delta']['recovered'])
                    except Exception as e:
                        # print('____Error:', e)
                        data_city += ',' + '0'

                    if (str(data_city) + '\n' not in lines): # or (str(data_city) not in lines):                           
                        f = open(path, 'a')
                        if 'linux' in sys.platform:
                            f.write(str(data_city) + '\n')
                        else:
                            f.write(str(data_city) + '\n')
                        f.close()

            except Exception as e:
                print('________Error:', e, date, state)

        return


if __name__ == '__main__':
    c = Covid19Logger()

    # ~ # Update latest data in all state files
    # ~ for i in range(delta_date.days + 1):
        # ~ date = sdate + timedelta(days=i)
        # ~ # print(date)
        # ~ c.cov_get_state_data(str(date))

    app.run_server(host='192.168.1.12', port='8080', debug=True)


