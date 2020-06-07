import json
import datetime
import requests

class Covid19Logger(object):
    def __init__(self):
        print("Covid19 Logger initialized.")

    def get_data_from_covid19india_org(self):
        # url = 'https://www.covid19india.org/'
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
    y = json.loads(c.get_data_from_covid19india_org())
    print('===================================================================================================')
    print('Bangalore:', y['Karnataka']['districtData']['Bengaluru Urban'])
    print('Ranchi:', y['Jharkhand']['districtData']['Ranchi'])
    print('Deoghar:', y['Jharkhand']['districtData']['Deoghar'])
    print('===================================================================================================')

