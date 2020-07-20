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
        # If file does not exists, get data from covid19india.org and save it locally
        if not os.path.isfile(file):
            self.cov_refresh_date_wise_data(date)

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
        states = []
        data = self.cov_get_date_wise_data(date)
        try:
            data = json.loads(data)
        except ValueError as e:
            print('________Error: Failed to load JSON for {}, {}'.format(city, date))
            return ''

        try:
            states = data.keys()
        except Exception as e:
            print('________Error:', e, date)
            return ''

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
                print('________Error:', e, date)
                # data_dict = ''

        # print(data_dict)

        # pdb.set_trace()
        data_city = str(date)

        try:
            data_city += ',' + str(data_dict[city]['total']['confirmed'])
        except Exception as e:
            print('____Error:', e)
            # print(data_dict[city]['total']['confirmed'])
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
            data_city += ',' + str(data_dict[city]['total']['tested'])
        except Exception as e:
            # print('____Error:', e)
            data_city += ',' + '0'

        try:
            data_city += ',' + str(data_dict[city]['delta']['confirmed'])
        except Exception as e:
            # print('____Error:', e)
            data_city += ',' + '0'

        try:
            data_city += ',' + str(data_dict[city]['delta']['recovered'])
        except Exception as e:
            # print('____Error:', e)
            data_city += ',' + '0'

        try:
            data_city += ',' + str(data_dict[city]['meta']['population'])
        except Exception as e:
            # print('____Error:', e)
            data_city += ',' + '0'

        # Create a file for district
        path = r'data\districts\{}.csv'.format(city)
        lines = ''
        if os.path.exists(path):
            f = open(r'data\districts\{}.csv'.format(city), 'r')
            lines = f.readlines()
            f.close()
        else:
            f = open(r'data\districts\{}.csv'.format(city), 'w')
            f.write('Date,Confirmed,Recovered,Deceased,Tested,DeltaConfirmed,DeltaRecovered,Population\n')
            f.close()

        if str(data_city) + '\n' not in lines:
            f = open(r'data\districts\{}.csv'.format(city), 'a')
            f.write(str(data_city) + '\n')
            f.close()

        return data_city

    def get_data_from_covid19india_org(self):
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

    sdate = date(2020, 4, 20)  # start date
    edate = datetime.now().date() - timedelta(days=1)

    # cities = ['Bengaluru Urban', 'Delhi', 'Mumbai', 'Chennai', 'Hyderabad', 'Kolkata']
    cities = ['Kolkata']

    delta = edate - sdate  # as timedelta

    confirmed_data = {}
    active_data = {}
    recovered_data = {}
    deceased_data = {}
    bangalore_confirmed_data = []
    surat_confirmed_data = []
    dates = []
    annotations = []

    fig = go.Figure()

    for city in cities:
        confirmed_data[city] = []
        recovered_data[city] = []
        deceased_data[city] = []
        active_data[city] = []
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            dates.append(str(day))
            data_city = c.cov_get_date_wise_city_data(str(day), city)




