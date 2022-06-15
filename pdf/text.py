# -*- coding: utf-8 -*-
import requests
import datetime
import math
import json
import csv
import pandas as pd

general_headers = {
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty'
}
session = requests.Session()


def login():
    url = "https://tickets.museivaticani.va/api/agency/login"
    payload = dict(username="736611", password="bv77sx23")
    login_headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }
    session.request("POST", url, headers=login_headers, data=json.dumps(payload))


def vatican(date_value):
    date_string = date_value.strftime("%d/%m/%Y")
    url = "https://tickets.museivaticani.va/api/agency/reservations?"
    params = dict(lang="en", fromVisitDate=date_string, toVisitDate=date_string)
    response = session.get(url=url, headers=general_headers, params=params)
    response_json = response.json()
    refer = response_json['references']
    if len(refer) == 0:
        return 0
    else:
        total_entries = response_json['totalResults']
        total_pages = math.ceil(float(total_entries) / 10.0)
        return total_pages


def final_data(date_value):
    login()
    num_pages = vatican(date_value)
    vatican_final_per_page = []
    date_string = date_value.strftime("%d/%m/%Y")
    print(date_string)
    print(num_pages)
    for page in range(0, int(num_pages)):
        url = "https://tickets.museivaticani.va/api/agency/reservations?"
        params = dict(lang="en", fromVisitDate=date_string, toVisitDate=date_string, page=page)
        response = session.get(url=url, headers=general_headers, params=params)
        resp_json = response.json()
        references = resp_json['references']
        for reference in references:
            reference_dict = {}
            reference_dict['name'] = reference['groupName'].encode("utf-8")
            reference_dict['num_pax'] = reference['visitorNumber']
            reference_dict['order_num'] = reference['referenceOrder']
            reference_dict['inventory_date'] = reference['visitDateTime']['date']
            reference_dict['inventory_time'] = reference['visitDateTime']['time']
            reference_dict['price'] = reference['total']
            vatican_final_per_page.append(reference_dict)
    return vatican_final_per_page


if __name__ == '__main__':
    start_date_value = "2019-09-01"
    end_date_value = "2019-09-30"
    start_date = datetime.datetime.strptime(start_date_value, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_value, '%Y-%m-%d')
    num_days = (end_date - start_date).days + 1
    vatican_final = []
    df = pd.DataFrame()
    for x in range(0, num_days):
        date_value = start_date + datetime.timedelta(days=x)
        final_data_return = final_data(date_value)
        final_data_return_df = pd.DataFrame(final_data_return)
        df = df.append(final_data_return_df)
    df.to_csv('Sept.csv', index=False)