import requests
import json
import time
import re
import os
import traceback

from google.cloud import bigquery
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/headout1/workSpace/service_account_credentials.json"

bigquery.Client.SCOPE = ('https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/cloud-platform',
                         'https://www.googleapis.com/auth/drive')
client = bigquery.Client()

MASTER_SHEET_ID = "1i1sh7aDqv5ZJxbK8saoAJTiKv6UyS1wJhqxVzQGQsGc"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
KEY_FILE_LOCATION = '/Users/headout1/workSpace/service_account_credentials.json'

credentials = service_account.Credentials.from_service_account_file(KEY_FILE_LOCATION)
# credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)

service = build('sheets', 'v4', credentials=credentials)


##########################
# FUNCTIONS
##########################

def read_sheets_data(spreadsheet_id, range):
    """ Function to read a Google Sheet using the Sheets API and
    return the data from the input range.

    Args:
        spreadsheet_id: The ID of the spreadsheet to retrieve data from.
        range: The A1 notation of the values to retrieve.
    """
    # Call the Sheets API to read the values
    sheet = service.spreadsheets()
    print(spreadsheet_id)
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    values = result.get('values', [])
    return values


def write_sheets_data(spreadsheet_id, range, values, value_input_option='USER_ENTERED'):
    """ Function to write data to a Google Sheet using the Sheets API.

    Args:
        spreadsheet_id: The ID of the spreadsheet to update.
        range: The A1 notation of a range to search for a logical table of data. Values will be
        appended after the last row of the table.
        values (array): The data that is to be written. This is an array of arrays, the outer array representing
        all the data and each inner array representing a major dimension (row by default). Each item in the inner
        array corresponds with one cell.
        value_input_option: Determines how input data should be interpreted.
    """

    value_range_body = {
        'values': values
    }
    # Call the Sheets API to write the rows
    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption=value_input_option,
        body=value_range_body
    )

    response = request.execute()
    return response


# ## get data from the recon tracker
master_sheet_data = read_sheets_data(MASTER_SHEET_ID, 'Input!A2:E')
recon_sheets = []

for row in master_sheet_data:
    print(row)
    if len(row) > 1:
        try:
            sheet_obj1 = {}
            sheet_obj1['month'] = row[0]
            sheet_obj1['sheet_id'] = re.search(r"/d/(.*)/", row[1]).group(1)
            sheet_obj1['recon_type'] = 'VCC'
            recon_sheets.append(sheet_obj1)
        except:
            print('No sheet available for',sheet_obj1)

        try:
            sheet_obj2 = {}
            sheet_obj2['month'] = row[0]
            sheet_obj2['sheet_id'] = re.search(r"/d/(.*)/", row[2]).group(1)
            sheet_obj2['recon_type'] = 'FD'
            recon_sheets.append(sheet_obj2)
        except:
            print('No sheet available for',sheet_obj2)

        try:
            sheet_obj3 = {}
            sheet_obj3['month'] = row[0]
            sheet_obj3['sheet_id'] = re.search(r"/d/(.*)/", row[3]).group(1)
            sheet_obj3['recon_type'] = 'PP'
            recon_sheets.append(sheet_obj3)
        except:
            print('No sheet available for',sheet_obj3)

        try:
            sheet_obj4 = {}
            sheet_obj4['month'] = row[0]
            sheet_obj4['sheet_id'] = re.search(r"/d/(.*)/", row[4]).group(1)
            sheet_obj4['recon_type'] = 'AP'
            recon_sheets.append(sheet_obj4)
        except:
            print('No sheet available for', sheet_obj4)



print(f"Recon tracker scanned. Found {len(recon_sheets)} recon sheets")

## clear the 'Output' tab from the Recon Master Sheet
output_tab_data = read_sheets_data(MASTER_SHEET_ID, 'Output!A:D')
rows_to_write = []
for i in range(1, len(output_tab_data), 1):
    temp_row = ["", "", "", ""]
    rows_to_write.append(temp_row)

write_sheets_data(
    spreadsheet_id=MASTER_SHEET_ID,
    range=f"Output!A2:D",
    values=rows_to_write,
    value_input_option='USER_ENTERED')

print("Output tab cleared")

## write to the 'Output' tab from the Recon Master Sheet
row_number = 2
i = 0
while i < len(recon_sheets):
    recon_month = recon_sheets[i]['month']
    recon_sheet_id = recon_sheets[i]['sheet_id']
    recon_type = recon_sheets[i]['recon_type']
    recon_sheet_data = []
    i = i + 1
    try:
        recon_sheet_data = read_sheets_data(recon_sheet_id, 'Final Format!A2:R')
    except:
        ## todo - check if traceback msg contains timeout msg or not, for now assume that the problem was due to timeout
        # print(traceback.print_exc())
        # print(type(traceback.print_exc()))
        print(f"Timeout error: {recon_type} - {recon_month}")
        time.sleep(5)
        continue
    rows_to_write = []

    for recon_sheet_row in recon_sheet_data:
        if recon_sheet_row[16] == '':
            print(f"Incomplete data for {recon_type} - {recon_month}: Booking ID - {recon_sheet_row[1]}")

        else:
            temp_array = []
            temp_array.extend((recon_sheet_row[1], recon_sheet_row[16], recon_type, recon_month))
            rows_to_write.append(temp_array)

    write_sheets_data(
        spreadsheet_id=MASTER_SHEET_ID,
        range=f"Output!A{row_number}:D",
        values=rows_to_write,
        value_input_option='USER_ENTERED')

    print(f"Done: {recon_type} - {recon_month}: Rows - {len(rows_to_write)}")
    row_number = row_number + len(rows_to_write)

    time.sleep(5)

## insert the new rows into the recon_table in BQ
print("Starting BQ insert opn")

query_job = client.query(
    """
    INSERT INTO `segment-data.dilshad_recon_temp.recon_table`
    SELECT
        *,
        DATE(CURRENT_TIMESTAMP()),
        "ACTIVE"
    FROM
        `segment-data.dilshad_recon_temp.recon_sheet`
    WHERE
        booking_id is not null
    """
)

bq_results = query_job.result()
print(bq_results)




# result = read_sheets_data("13oWBqD4XCq-AdX6ivervfmqB6xV03dCVikJ890uimws", 'Final Format!A2:B')
# print(result)