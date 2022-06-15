from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket,User
import datetime
import pandas as pd

# creds = {
#     'email': 'yash.agarwal@headout.com',
#     'token': 'j7NowZao9dK23igW4sPNyKLICTAeyld6Z8UDUu2v',
#     'subdomain': 'headout'
# }

creds = {
    'email': 'MAIL',
    'token': 'TOKEN',
    'subdomain': 'headoutfin'
}

# Default
zenpy_client = Zenpy(proactive_ratelimit=100, **creds)
#


def create_tickets():
    requester = zenpy_client.search(type='user', email="dilshad.davoo@headout.com")
    if len(requester) > 0:
        requester_id = requester[0:1][0].id
        print("existed", requester_id)
    else:
        user = User(name="Dilshad", email="dilshad.davoo@headout.com")
        created_user = zenpy_client.users.create(user)
        requester_id = created_user.id
        print("created", requester_id)

    url = "https://docs.google.com/spreadsheets/d/13Fl19VWSSTZhgqMSgyDYpriH4QpR_qyaF2KQpePxarI"
    description = f"""
    Dear Partner,
    I hope you and your team are doing well.
    
    Please find the report for the period Oct 01, 2021 - Oct 31, 2021.
    
    Sheet link : {url}
    
    Let me know if this matches your records or if there are any discrepancies so that we can look into it and process payment accordingly.
    
    Please get back to us on the same within 30 days of the report being sent, for any discrepancies or approval of payment per our report - We will initiate an auto-payment and close the loop on this invoice in case we don't hear back from you in the next 30 days.
    Looking forward to hearing from you. :)
    """

    ticketCreated = zenpy_client.tickets.create(
        Ticket(subject="New Ticket Test", description=description, priority="urgent", requester_id=requester_id,
               custom_fields=[{
                   "id": 360043126093,
                   "value": "bali"
               },
                   {
                       "id": 360035587913,
                       "value": "usd"
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
                       "id": 360044350333,
                       "value": "360_amsterdam"
                   },
                   {
                       "id": 360043126413,
                       "value": "date_of_booking"
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
                       "value": "36.8"
                   }
               ]
               )
    )
    print(ticketCreated.to_dict())


def search(idNumber, customFields):
    return next((customField for customField in customFields if customField['id'] == idNumber), {}).get('value')


def checkTicketFields():
    ticketIds = [11057]
    for ticket in zenpy_client.tickets(ids=ticketIds):
        customFields = ticket.custom_fields
        ticketProgress = search(360036150174, customFields)
        city = search(360043126093, customFields)
        currency = search(360035587913, customFields)
        apType = search(360044350833, customFields)
        spName = search(360044350333, customFields)
        startDate = search(360035978714, customFields)
        endDate = search(360035978734, customFields)
        netPrice = search(360035698494, customFields)
        print(ticketProgress, city, currency, apType,ticket.priority)



create_tickets()
