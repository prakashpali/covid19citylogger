import json
from datetime import datetime, date, timedelta
import requests
import os
import pdb
import plotly.graph_objects as go
import plotly.express as px

class Covid19Logger(object):
    def __init__(self):
        print("Covid19 Logger initialized.")

    def cov_refresh_date_wise_data(self):
        '''
        Get all the date till date
        '''

        sdate = date(2020, 4, 1)  # start date
        edate = date(2020, 6, 20)  # end date
        # edate = date(2020, 4, 3)  # end date

        # print(datetime.now().date())

        delta = edate - sdate  # as timedelta

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            print(day)

            # https://api.covid19india.org/v3/data-2020-05-20.json
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
            # file = r'data\{}_json.txt'.format(day)
            file = r'data\{}.csv'.format(day)      # Read write operation on csv was found to be faster
            f = open(file, 'w+')
            f.write(data)
            f.close()

        return

    def cov_get_date_wise_data(self, date):
        '''
        Get data for a particular date. Date has to be in YYYY-MM-DD format
        '''

        # file = r'data\{}_json.txt'.format(date)
        file = r'data\{}.csv'.format(date)      # Read write operation on csv was found to be faster
        data = ''
        try:
            f = open(file, 'r')
            data = f.read()
            # data = json.loads(data)
        except Exception as e:
            print('Failed to get data for date - {}. Error is {}'.format(date, e))

        return data

    def cov_get_date_wise_city_data(self, date, city):
        '''
        Get date wise data for each city
        '''
        data = self.cov_get_date_wise_data(date)
        data = json.loads(data)
        states = data.keys()
        data_dict = ''
        for key in states:
            try:
                # data_dict = data[key]['districts'].has_key(city)
                data_dict = data[key]['districts']
                cities = data_dict.keys()
                if city in cities:
                    break
                # print(data_dict[city])
            except Exception as e:
                print('________Error:', e)
                # data_dict = ''

        # print(data_dict[city])

        # pdb.set_trace()
        data_city = {'date': date}

        try:
            data_city.update({'confirmed': data_dict[city]['total']['confirmed']})
        except Exception as e:
            # print('____Error:', e)
            data_city.update({'confirmed': 0})

        try:
            data_city.update({'recovered': data_dict[city]['total']['recovered']})
        except Exception as e:
            # print('____Error:', e)
            data_city.update({'recovered': 0})

        try:
            data_city.update({'deceased': data_dict[city]['total']['deceased']})
        except Exception as e:
            # print('____Error:', e)
            data_city.update({'deceased': 0})

        try:
            data_city.update({'delta_confirmed': data_dict[city]['total']['confirmed']})
        except Exception as e:
            # print('____Error:', e)
            data_city.update({'delta_confirmed': 0})

        try:
            data_city.update({'delta_recovered': data_dict[city]['total']['recovered']})
        except Exception as e:
            # print('____Error:', e)
            data_city.update({'delta_recovered': 0})

        # Create a file for district
        path = r'data\districts\{}.csv'.format(city)
        lines = ''
        if os.path.exists(path):
            f = open(r'data\districts\{}.csv'.format(city), 'r')
            lines = f.readlines()
            f.close()

        if str(data_city) + '\n' not in lines:
            f = open(r'data\districts\{}.csv'.format(city), 'a')
            f.write(str(data_city) + '\n')
            f.close()

        return data_city

    def get_data_from_covid19india_org(self):
        # url = 'https://www.covid19india.org/'
        # https://api.covid19india.org/v3/data-2020-05-20.json
        url = 'https://api.covid19india.org/state_district_wise.json'
        rsp = requests.get(url)
        if rsp.status_code in (200,):

            # This magic here is to cut out various leading characters from the JSON
            # response, as well as trailing stuff (a terminating ']\n' sequence), and then
            # we decode the escape sequences in the response
            # This then allows you to load the resulting string
            # with the JSON module.
            data = rsp.content.decode('utf-8')
            return data

if __name__ == '__main__':
    c = Covid19Logger()

    # c.cov_refresh_date_wise_data()

    sdate = date(2020, 4, 20)  # start date
    edate = date(2020, 6, 20)  # end date

    cities = ['Bengaluru Urban', 'Surat', 'Ranchi', 'Mumbai']

    # print(datetime.now().date())

    delta = edate - sdate  # as timedelta

    confirmed_data = {}
    bangalore_confirmed_data = []
    surat_confirmed_data = []
    dates = []
    annotations = []

    fig = go.Figure()

    for city in cities:
        confirmed_data[city] = []
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            dates.append(str(day))
            confirmed_data[city].append(c.cov_get_date_wise_city_data(str(day), city)['confirmed'])

        fig.add_trace(go.Scatter(x=dates, y=confirmed_data[city], name=city, mode='lines+markers'))

        # Adding labels
        y_trace = confirmed_data[city]
        # labeling the left_side of the plot
        annotations.append(dict(xref='paper', x=0.05, y=y_trace[0],
                                xanchor='right', yanchor='middle',
                                text=city + ' {}'.format(y_trace[0]),
                                font=dict(family='Arial',
                                          size=10),
                                showarrow=False))
        # labeling the right_side of the plot
        annotations.append(dict(xref='paper', x=0.95, y=y_trace[-1],
                                xanchor='left', yanchor='middle',
                                text='{}'.format(y_trace[-1]),
                                font=dict(family='Arial',
                                          size=10),
                                showarrow=False))

    print(confirmed_data)
    print(dates)
    print(annotations)

    # Edit the layout
    fig.update_layout(title='Number of confirmed cases in cities',
                      xaxis_title='Date',
                      yaxis_title='Number',
                      xaxis=dict(
                          showline=True,
                          showgrid=True,
                          showticklabels=True,
                          linecolor='rgb(204, 204, 204)',
                          linewidth=2,
                          ticks='outside',
                          tickfont=dict(
                              family='Arial',
                              size=12,
                              color='rgb(82, 82, 82)',
                          ),
                      ),
                      annotations=annotations
    )

    fig.show()
    # fig.write_html('confirmed_cases.html', auto_open=True)



