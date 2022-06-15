import os
import time
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User

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
zenpy_client = Zenpy(proactive_ratelimit=100, **creds)

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

    spreadsheetId = spreadsheet.get('spreadsheetId')
    # print('Spreadsheet ID: {0}'.format(sheet_id))

    ##Create a new tab and rename tab except for master link sheets
    if title != "Master sheet for links":
        body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': "adjustment",
                            "sheetId": 1
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
            spreadsheetId=spreadsheetId,
            body=body).execute()

    # Move the created Spreadsheet to the specific folder.
    drive_service.files().update(fileId=spreadsheetId, addParents=folderId,
                                 removeParents='root').execute()
    print(spreadsheetId)
    return spreadsheetId


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


def insert_permission(sheet_id, mail):
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
    # mail = "dilshad.davood@headout.com"

    batch = drive_service.new_batch_http_request(callback=callback)
    user_permission1 = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'payables@headout.com',

    }

    batch.add(drive_service.permissions().create(fileId=sheet_id,
                                                 body=user_permission1,
                                                 fields='id',
                                                 sendNotificationEmail=False
                                                 ))

    user_permission2 = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': mail,

    }
    batch.add(drive_service.permissions().create(fileId=sheet_id,
                                                 body=user_permission2,
                                                 fields='id',
                                                 sendNotificationEmail=False
                                                 ))

    batch.execute()


def hide_columns(spreadsheet_id):
    body = {
        'requests': [{
            'updateDimensionProperties': {
                "range": {
                    "sheetId": 0,
                    "dimension": 'COLUMNS',
                    "startIndex": 27,
                    "endIndex": 33,
                },
                "properties": {
                    "hiddenByUser": True,
                },
                "fields": 'hiddenByUser',
            }}, {
            'updateDimensionProperties': {
                "range": {
                    "sheetId": 1,
                    "dimension": 'COLUMNS',
                    "startIndex": 26,
                    "endIndex": 32,
                },
                "properties": {
                    "hiddenByUser": True,
                },
                "fields": 'hiddenByUser',
            }}]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def get_sales_report(start_date, end_date, sp_dod, sp_dob):
    print("Starting querying BQ")
    if len(sp_dod) == 0:
        sp_dod = '1'
    if len(sp_dob) == 0:
        sp_dob = '1'
    query_job = client.query(
        f"""
        WITH
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
                1 
        ),
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
                bookings.margin AS margin,
                orders.payment_amount_refunded AS amount_refunded,
                bookings.vendor_id AS vendor_id,
                fulfilment.fulfilment_type,
                bookings.completion_type,
                bookings.vendor_name AS sp_name_on_DB,
                fulfilment.ticket_tags
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
                AND fulfilment.fulfilment_type NOT IN ("Selenium")
        ), 
        main AS (
            (
            SELECT
                * ,"No" AS adjustments,"No" AS charge_loss
            FROM
                booking
            WHERE
                experience_date BETWEEN "{start_date}"
                AND "{end_date}"
                AND booking_status IN ("Completed")
                AND completion_type IN ("Super", "Amended")
                AND vendor_id IN ({sp_dod}) 
            )
            UNION ALL (
            SELECT
                * ,"No" AS adjustments,"No" AS charge_loss
            FROM
                booking
            WHERE
                created_at BETWEEN "{start_date}"
                AND "{end_date}"
                AND booking_status IN ("Completed")
                AND completion_type IN ("Super", "Amended")
                AND vendor_id IN ({sp_dob}) 
            )
            UNION ALL (
            SELECT
                * ,"Yes" AS adjustments,"No" AS charge_loss
            FROM
                booking
            WHERE
                created_at < "{start_date}"
                AND experience_date BETWEEN "{start_date}"
                AND "{end_date}"
                AND amount_refunded IS NOT NULL
                AND vendor_id IN ({sp_dob}) 
            ) 
            UNION ALL (
                SELECT
                    * ,"No" AS adjustments,"Yes" AS charge_loss
                FROM
                    booking
                WHERE
                    experience_date BETWEEN "{start_date}"
                    AND "{end_date}"
                    AND booking_status IN ("Cancelled")
                    AND ticket_tags LIKE "%CHARGE_LOSS%"
                    AND vendor_id IN ({sp_dod}) 
            ) 
            UNION ALL (
                SELECT
                    * ,"No" AS adjustments, "Yes" AS charge_loss
                FROM
                    booking
                WHERE
                    created_at BETWEEN "{start_date}"
                    AND "{end_date}"
                    AND booking_status IN ("Cancelled")
                    AND ticket_tags LIKE "%CHARGE_LOSS%"
                    AND vendor_id IN ({sp_dob}) 
            )   
        )

        SELECT 
        DISTINCT
            created_at,
            experience_date,
            experience_time,
            booking_id,
            customer_name,
            tour_group_name,
            variant_name,
            TGID,
            TID,
            booking_status,
            city,
            tour_currency_code,
            pax_summary,
            num_adult,
            num_child,
            num_general,
            num_youth,
            num_student,
            num_senior,
            num_infant,
            num_group,
            num_family,
            total_pax,
            price_net,
            margin,
            amount_refunded,
            CASE 
                WHEN amount_refunded IS NOT NULL AND charge_loss = "No"
                THEN price_net - (amount_refunded*(1-(COALESCE(margin,0)/100)))
                ELSE price_net 
            END AS final_net_price,
            vendor_id,
            fulfilment_type,
            completion_type,
            charge_loss,
            adjustments,
            sp_name_on_DB            
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


def getUserIds(email):
    user = zenpy_client.search(type='user', email=email)
    name = email.split('@')[0]
    if len(user) > 0:
        user_id = user[0:1][0].id
    else:
        user = User(name=name, email=email)
        created_user = zenpy_client.users.create(user)
        user_id = created_user.id
        print("created", user_id)
    return user_id


def create_tickets(spreadsheet_id, sheet_name, invoice_amount, sp_details, start_date, end_date):
    name = sp_details['sp_name_in_sheet'].values[0]
    city = sp_details['city'].values[0]
    currency = sp_details['currency'].values[0]
    zen_tag = sp_details['sp_name_tag'].values[0]
    basis = sp_details['basis'].values[0]
    if basis == "Date of Delivery":
        basis_tag = "date_of_experience"
    elif basis == "Date of Booking":
        basis_tag = "date_of_booking"
    # getting requester id
    primary_mail = sp_details['primary_mail'].values[0]
    requester_id = getUserIds(primary_mail)
    # getting collaborator id
    collaborator_ids = []
    secondary_mail = sp_details['secondary_mail'].values[0]
    if secondary_mail != "":
        for mail in secondary_mail.split(","):
            collaborator_ids.append(getUserIds(mail))

    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    description = f"""
    Dear Partner,
    
    I hope you and your team are doing well.

    Please find the report for the period May 01, 2022 - May 31, 2022.

    Link to report : {sheet_url}

    Let me know if this matches your records or if there are any discrepancies so that we can look into it and process payment accordingly.

    Please get back to us on the same within 15 days of the report being sent, for any discrepancies or approval of payment per our report - We will initiate an auto-payment and close the loop on this invoice in case we don't hear back from you in the next 15 days.
    Looking forward to hearing from you. :)
    """
    # Ticket(subject=f"October’21 - {sp}", description=description, requester_id=requester_id,
    ticketCreated = zenpy_client.tickets.create(
        Ticket(subject=f"May’22 - {name}", description=description, priority="urgent", requester_id=requester_id,
               collaborator_ids=collaborator_ids,
               custom_fields=[{
                   "id": 360043126093,
                   "value": city.lower()
               },
                   {
                       "id": 360035587913,
                       "value": currency.lower()
                   },
                   {
                       "id": 360036150174,
                       "value": "vendor_pending"
                   },
                   {
                       "id": 360044350833,
                       "value": "regular_ap"
                   },
                   {
                       "id": 4416545411865,
                       "value": zen_tag
                   },
                   {
                       "id": 360043126413,
                       "value": basis_tag
                   },
                   {
                       "id": 360035978714,
                       "value": start_date
                   },
                   {
                       "id": 360035978734,
                       "value": end_date
                   },
                   {
                       "id": 360035698494,
                       "value": invoice_amount
                   },
                   {
                       "id": 360035698654,
                       "value": sheet_name
                   },
                   {
                       "id": 360044350333,
                       "value": zen_tag.replace("_tag", "")
                   }
               ]
               )
    )
    print(ticketCreated.audit.ticket_id)
    return ticketCreated.audit.ticket_id


def main():
    start_date = "2022-05-01"
    end_date = "2022-05-31"
    abbr_date = "22-05"
    MASTER_SHEET_ID = "1th2ZQ-anyh5YPsK8TRvMRazfE1bq3SOZS2rhsqp3f0A"
    sp_raw_data = read_sheets_data(MASTER_SHEET_ID, "SP Master!A1:J")
    sp_data = pd.DataFrame(sp_raw_data)
    sp_data = sp_data.rename(columns=sp_data.iloc[0]).drop(sp_data.index[0])
    sp_data = sp_data[sp_data['skip_automation'] == "No"]
    sp_data_date_of_booking = sp_data[sp_data['basis'] == "Date of Booking"]
    sp_data_date_of_delivery = sp_data[sp_data['basis'] == "Date of Delivery"]

    # sp_array = list(sp_data['sp_name'].unique())
    # for sp in sp_array:
    #     sp_basis = sp_data[sp_data['sp_name'] == sp]['basis'].iloc[0]
    #     email = sp_data[sp_data['sp_name'] == sp]['email'].iloc[0]
    #     print(sp, sp_basis,email)

    sp_dod = ", ".join(map(str, sp_data_date_of_delivery['sp_id']))
    sp_dob = ", ".join(map(str, sp_data_date_of_booking['sp_id']))
    sales = get_sales_report(start_date, end_date, sp_dod, sp_dob)
    print("Shape of sales data", sales.shape)
    print(pd.unique(sales['vendor_id']).shape)

    sp_data = sp_data.rename(columns={'sp_id': 'vendor_id', 'sp_name': 'sp_name_in_sheet'})
    sales = sales.rename(columns={'margin': 'margin %'})
    sp_data['vendor_id'] = sp_data['vendor_id'].astype(int)
    sales = sales.merge(sp_data[['vendor_id', 'sp_name_in_sheet']], on='vendor_id')
    sales.replace(np.nan, '', inplace=True)
    sales['created_at'] = sales['created_at'].apply(str)
    sales['experience_date'] = sales['experience_date'].apply(str)
    sales['experience_time'] = sales['experience_time'].apply(str)
    vendor_ids = list(sales['vendor_id'].unique())
    print("vendor IDs", vendor_ids)
    sheets_array = []

    folderId = createRemoteFolder(f"May - {datetime.now()}", "1YgeUuCupA73ANSZs_YykZdcV2JnHtSpd")
    # folderId = "1nROddFIrWW_oJMHWlY5ttQ5EFHFF8JH_"
    for vendor_id in vendor_ids:
        try:
            print(vendor_id)
            sp_sales = sales[sales['vendor_id'] == vendor_id]
            sp_details = sp_data[sp_data['vendor_id'] == vendor_id]
            sp_name = sp_details['sp_name_in_sheet'].values[0]
            basis = sp_details['basis'].values[0]
            abbreviation = sp_details['abbreviation'].values[0]
            sheet_name = str(abbreviation) + "-" + abbr_date
            spreadsheet_id = create_sheets(sheet_name, folderId)
            primary_mail = sp_details['primary_mail'].values[0]
            insert_permission(spreadsheet_id, primary_mail)
            secondary_mail = sp_details['secondary_mail'].values[0]
            if secondary_mail != "":
                for mail in secondary_mail.split(","):
                    insert_permission(spreadsheet_id, mail)
            sp_sales_completed = sp_sales[sp_sales['adjustments'] == "No"]
            # sp_sales_completed.drop('charge_loss', axis=1, inplace=True)
            del sp_sales_completed['adjustments']
            write_sheets_data(spreadsheet_id, "sale!A1:AG", sp_sales_completed, value_input_option='USER_ENTERED')
            time.sleep(1)
            sp_sales_cancelled = sp_sales[sp_sales['adjustments'] == 'Yes']
            del sp_sales_cancelled['adjustments']
            del sp_sales_cancelled['final_net_price']
            write_sheets_data(spreadsheet_id, "adjustment!A1:AG", sp_sales_cancelled, value_input_option='USER_ENTERED')
            adjustment_present = "No"
            if len(sp_sales_cancelled) > 0:
                adjustment_present = "Yes"
                write_sheets_data(spreadsheet_id, "adjustment!A1:AF", sp_sales_cancelled, value_input_option='USER_ENTERED')
            hide_columns(spreadsheet_id)
            # Calling copy sheet function
            copy_sheets_data(spreadsheet_id)

            total_net_price = sp_sales_completed["final_net_price"].sum()
            total_adjustment_price = sp_sales_cancelled["price_net"].sum()
            invoice_amount = str(round(total_net_price - total_adjustment_price, 2))
            ticket_id = create_tickets(spreadsheet_id, sheet_name, invoice_amount, sp_details, start_date, end_date)
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            sheets_array.append([vendor_id, sp_name, basis, sheet_url, ticket_id, adjustment_present])
            time.sleep(10)
        except Exception as e:
            print("error", str(e), vendor_id)
            sheets_array.append([vendor_id, "error", str(e), "", "", ""])
            time.sleep(10)

    pd.DataFrame(sheets_array).to_csv('sales-may.csv')
    link_sheet_id = create_sheets("Master sheet for links", folderId)
    master_sheet_data = pd.DataFrame(sheets_array,
                                     columns=["sp_id", 'sp_name', "basis", "sheet_url", "ticket_id", "adjustments"])
    write_sheets_data(link_sheet_id, "Sheet1!A1:F", master_sheet_data, value_input_option='USER_ENTERED')

main()
