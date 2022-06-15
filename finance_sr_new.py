import requests
import json
import time
import re
import os
import time
import traceback
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/headout1/workSpace/service_account_credentials.json"

bigquery.Client.SCOPE = ('https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/cloud-platform',
                         'https://www.googleapis.com/auth/drive')
client = bigquery.Client()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
KEY_FILE_LOCATION = '/Users/headout1/workSpace/service_account_credentials.json'

credentials = service_account.Credentials.from_service_account_file(KEY_FILE_LOCATION)
# credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)

# zen cred
creds = {
    'email': 'viraaj@headout.com',
    'token': 'BWKRETavF5Yuj8HTnFaekh5XIyxt0csPLoIuXOdU',
    'subdomain': 'headoutfin'
}

service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)


##########################
# FUNCTIONS
##########################

def createRemoteFolder(folderName, parentID=None):
    # Create a folder on Drive, returns the newely created folders ID
    body = {
        'name': folderName,
        'mimeType': "application/vnd.google-apps.folder"
    }
    if parentID:
        body['parents'] = [parentID]
    root_folder = drive_service.files().create(body=body).execute()
    return root_folder['id']


def create_sheets(title, folderId):
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()

    sheet_id = spreadsheet.get('spreadsheetId')
    print('Spreadsheet ID: {0}'.format(sheet_id))

    ##Create a new tab and rename tab except for master link sheets
    if title != "Master sheet for links":
        body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': "adjustment"
                        }
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": 0,
                            "title": "sale",
                        },
                        "fields": "title",
                    }
                }
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=body).execute()

        # Calling copy sheet function
        copy_sheets_data(sheet_id)

    # Move the created Spreadsheet to the specific folder.
    drive_service.files().update(fileId=sheet_id, addParents=folderId,
                                 removeParents='root').execute()

    return sheet_id


def copy_sheets_data(sheet_id):
    # The ID of the spreadsheet to copy the sheet to.
    copy_sheet_to_another_spreadsheet_request_body = {

        'destination_spreadsheet_id': sheet_id,

    }

    service.spreadsheets().sheets().copyTo(spreadsheetId="1th2ZQ-anyh5YPsK8TRvMRazfE1bq3SOZS2rhsqp3f0A",
                                           sheetId=647246743,
                                           body=copy_sheet_to_another_spreadsheet_request_body).execute()

    # Rename by sheet name after copying
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    tab_id = None
    for _sheet in spreadsheet['sheets']:
        if _sheet['properties']['title'] == "Copy of Summary":
            tab_id = _sheet['properties']['sheetId']
    print(tab_id)

    body = {
        'requests': [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": tab_id,
                        "title": "summary",
                    },
                    "fields": "title",
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=body).execute()


def read_sheets_data(spreadsheet_id, range):
    """ Function to read a Google Sheet using the Sheets API and
    return the data from the input range.

    Args:
        spreadsheet_id: The ID of the spreadsheet to retrieve data from.
        range: The A1 notation of the values to retrieve.
    """
    # Call the Sheets API to read the values
    sheet = service.spreadsheets()
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
        'values': values.T.reset_index().T.values.tolist(),
        'majorDimension': 'ROWS'
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


def insert_permission(sheet_id):
    """Insert a new permission.

      Args:
        services: Drive API service instance.
        file_id: ID of the file to insert permission for.
        value: User or group e-mail address, domain name or None for 'default'
               type.
        perm_type: The value 'user', 'group', 'domain' or 'default'.
        role: The value 'owner', 'writer' or 'reader'.
      Returns:
        The inserted permission if successful, None otherwise.
    """
    mail = "dilshad.davood@headout.com"
    batch = drive_service.new_batch_http_request(callback=callback)
    # user_permission = {
    #     'type': 'user',
    #     'role': 'writer',
    #     'emailAddress': mail
    # }
    # batch.add(drive_service.permissions().create(
    #     fileId=sheet_id,
    #     body=user_permission,
    #     fields='id',
    # ))
    domain_permission = {
        'type': 'domain',
        'role': 'writer',
        'domain': 'headout.com'
    }
    batch.add(drive_service.permissions().create(
        fileId=sheet_id,
        body=domain_permission,
        fields='id',
    ))
    batch.execute()


def get_sales_report():
    print("Starting querying BQ")
    query_job = client.query(
        f"""
        WITH  vendor_details AS(
SELECT 
  vendor_id,
  vendor_name,
  vendor_city,
  payment_basis,
  supply_partner_billing_entity_id 
FROM 
  `segment-data.analytics_staging.stg_database__vendors` 
WHERE 
  payment_method = "HEADOUT_STANDARD_REPORTING" AND 
  payment_basis IS NOT NULL),
  doe_sp AS (
    SELECT vendor_id
    FROM vendor_details
    WHERE payment_basis = "DATE_OF_EXPERIENCE"
  ),
  dob_sp AS (
    SELECT vendor_id
    FROM vendor_details
    WHERE payment_basis = "DATE_OF_BOOKING"
  ),
      booking_guest AS (
      SELECT
        booking_id,
        SUM(CASE WHEN guests.guest_type = "adult" THEN guests.number_of_guests ELSE 0 END) AS num_adult,
        SUM(CASE WHEN guests.guest_type = "child" THEN guests.number_of_guests ELSE 0 END) AS num_child,
        SUM(CASE WHEN guests.guest_type = "general" THEN guests.number_of_guests ELSE 0 END) AS num_general,
        SUM(CASE WHEN guests.guest_type = "youth" THEN guests.number_of_guests ELSE 0 END) AS num_youth,
        SUM(CASE WHEN guests.guest_type = "student" THEN guests.number_of_guests ELSE 0 END) AS num_student,
        SUM(CASE WHEN guests.guest_type = "senior" THEN guests.number_of_guests ELSE 0 END) AS num_senior,
        SUM(CASE WHEN guests.guest_type = "infant" THEN guests.number_of_guests ELSE 0 END) AS num_infant,
        SUM(CASE WHEN guests.guest_type = "group" THEN guests.number_of_guests ELSE 0 END) AS num_group,
        SUM(CASE WHEN (guests.guest_type LIKE "%family%") THEN guests.number_of_guests ELSE 0 END) AS num_family,
        STRING_AGG(CONCAT(guests.guest_type," : ",CAST(guests.number_of_guests AS STRING)),", ") AS pax_summary,
      FROM
        `segment-data.analytics_reporting.fct_bookings` bookings
      CROSS JOIN
        UNNEST(bookings.guests) AS guests
      GROUP BY
        1 ),
      booking AS (
      SELECT
        DATE(bookings.created_at) AS created_at,
        bookings.experience_date AS experience_date,
        bookings.experience_time AS experience_time,
        bookings.booking_id AS booking_id,
        bookings.primary_guest_name AS customer_name,
        bookings.experience_name AS tour_group_name,
        bookings.variant_name AS variant_name,
        bookings.experience_id AS TGID,
        bookings.tour_id AS TID,
        bookings.booking_status AS booking_status,
        bookings.city AS city,
        bookings.processing_currency AS tour_currency_code,
        booking_guest.pax_summary AS pax_summary,
        booking_guest.num_adult,
        booking_guest.num_child,
        booking_guest.num_general,
        booking_guest.num_youth,
        booking_guest.num_student,
        booking_guest.num_senior,
        booking_guest.num_infant,
        booking_guest.num_group,
        booking_guest.num_family,
        bookings.number_of_guests AS total_pax,
        bookings.price_net AS price_net,
        orders.payment_amount_refunded AS amount_refunded,
        CAST(bookings.vendor_id AS STRING) AS vendor_id,
        fulfilment.fulfilment_type,
        bookings.completion_type,
        bookings.vendor_name AS sp_name
      FROM
        `segment-data.analytics_reporting.fct_bookings` bookings
      LEFT JOIN 
        booking_guest USING (booking_id)
      LEFT JOIN
        `segment-data.analytics_reporting.fct_orders` orders USING (order_id)
      LEFT JOIN
        `segment-data.analytics_reporting.fct_fulfilments` fulfilment USING (booking_id)
      WHERE
        NOT REGEXP_CONTAINS(fulfilment.ticket_tags, "PREPURCHASEPLUGIN")
        AND fulfilment.fulfilment_type NOT IN ("Selenium")), 
    main AS (
      (
      SELECT
        * 
      FROM
        booking
      WHERE
        experience_date BETWEEN "2021-11-01"
        AND "2021-11-30"
        AND NOT booking_status IN ("Dummy",
          "Cancelled",
          "Pending")
        AND completion_type IN ("Super",
          "Amended")
        AND vendor_id IN (SELECT * FROM doe_sp) )
    UNION ALL (
      SELECT
        * 
      FROM
        booking
      WHERE
        created_at BETWEEN "2021-11-01"
        AND "2021-11-30"
        AND NOT booking_status IN ("Dummy",
          "Cancelled",
          "Pending")
        AND completion_type IN ("Super",
          "Amended")
        AND vendor_id IN (SELECT * FROM dob_sp) )
    UNION ALL (
      SELECT
        * 
      FROM
        booking
      WHERE
        created_at < "2021-11-01"
        AND experience_date BETWEEN "2021-11-01"
        AND "2021-11-30"
        AND amount_refunded IS NOT NULL
        AND vendor_id IN (SELECT * FROM dob_sp) ) )
        
      SELECT 
        * 
      FROM 
        main
      """
    )

    bq_results = query_job.result().to_dataframe(
        create_bqstorage_client=True,
    )
    print("Ended querying BQ")
    return bq_results


def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))


def zendesk(url, sp, total_net_price):
    # Default
    zenpy_client = Zenpy(proactive_ratelimit=100, **creds)
    #

    requester = zenpy_client.search(type='user', email="dilshad.davood@headout.com")
    if len(requester) > 0:
        requester_id = requester[0:1][0].id
        description = f"""
        Dear Partner,
        I hope you and your team are doing well.

        Please find the report for the period Oct 01, 2021 - Oct 31, 2021. 

        Sheet link : {url}

        Let me know if this matches your records or if there are any discrepancies so that we can look into it and process payment accordingly.

        Please get back to us on the same within 30 days of the report being sent, for any discrepancies or approval of payment per our report - We will initiate an auto-payment and close the loop on this invoice in case we don't hear back from you in the next 30 days.
        Looking forward to hearing from you. :)
        """

        job_status = zenpy_client.tickets.create(
            Ticket(subject=f"October’21 - {sp}", description=description, requester_id=requester_id,
                   custom_fields=[{
                       "id": 360043126093,
                       "value": "BALI"
                   },
                       {
                           "id": 360035587913,
                           "value": "USD"
                       },
                       {
                           "id": 360036150174,
                           "value": "Vendor Pending"
                       },
                       {
                           "id": 360044350833,
                           "value": "Regular AP"
                       },
                       {
                           "id": 360044350333,
                           "value": sp
                       },
                       {
                           "id": 360035978714,
                           "value": "2021-10-01"
                       },
                       {
                           "id": 360035978734,
                           "value": "2021-10-31"
                       },
                       {
                           "id": 360035698494,
                           "value": total_net_price
                       }
                   ]
                   )
        )


def main():
    sales = get_sales_report()

    sales.replace(np.nan, '', inplace=True)
    sales['created_at'] = sales['created_at'].apply(str)
    sales['experience_date'] = sales['experience_date'].apply(str)
    sales['experience_time'] = sales['experience_time'].apply(str)
    sp_array = list(sales['sp_name'].unique())
    print(sp_array)
    sheets_array = []

    folderId = createRemoteFolder(f"Nov - {datetime.now()}", "1YgeUuCupA73ANSZs_YykZdcV2JnHtSpd")
    # folderId = "1l9qOvknHHeZ519baxs9DmlHTwqBxY-gw"
    for sp in sp_array:
        sp_sales = sales[sales['sp_name'] == sp]
        sheet_id = create_sheets(sp, folderId)

        # insert_permission(sheet_id)
        print(sp)
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        # pd.DataFrame(sp_sales).to_csv(f'sheets/{sp}.csv')
        sp_sales_completed = sp_sales[sp_sales['booking_status'] == 'Completed']
        total_net_price = sp_sales_completed["price_net"].sum()
        print(total_net_price)
        total_net_price = str(round(total_net_price, 2))
        write_sheets_data(sheet_id, "sale!A1:AD", sp_sales_completed, value_input_option='USER_ENTERED')
        sp_sales_cancelled = sp_sales[sp_sales['booking_status'] == 'Cancelled']
        if len(sp_sales_cancelled) > 0:
            write_sheets_data(sheet_id, "adjustment!A1:AD", sp_sales_cancelled, value_input_option='USER_ENTERED')
        # else:
        #     #Run zendesk ticket creation if there is no adjustments
        #     zendesk(sheet_url, sp, total_net_price)
        sheets_array.append([sp, sheet_url])
        time.sleep(10)

    print(sheets_array)
    # pd.DataFrame(sheets_array).to_csv('sales-oct.csv')
    link_sheet_id = create_sheets("Master sheet for links", folderId)
    write_sheets_data(link_sheet_id, "Sheet1!A1:C", pd.DataFrame(sheets_array), value_input_option='USER_ENTERED')


main()

# sp_details = read_sheets_data("1th2ZQ-anyh5YPsK8TRvMRazfE1bq3SOZS2rhsqp3f0A", "details!A1:D")
# sp_data = pd.DataFrame(sp_details)
# sp_data = sp_data.rename(columns=sp_data.iloc[0]).drop(sp_data.index[0])
# print(sp_data[sp_data["vendor_name"] == "360 Amsterdam"]["mail"].iloc[0])
