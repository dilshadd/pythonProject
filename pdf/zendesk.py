from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket
import datetime
import pandas as pd

creds = {
    'email': 'parag.j@headout.com',
    'password': 'Headout@123',
    'subdomain': 'headout'
}

# creds = {
#     'email': 'viraaj@headout.com',
#     'token': 'BWKRETavF5Yuj8HTnFaekh5XIyxt0csPLoIuXOdU',
#     'subdomain': 'headoutfin'
# }

# Default
zenpy_client = Zenpy(proactive_ratelimit=100, **creds)
#
for new_ticket in zenpy_client.tickets(ids=[5022620]):
    print(new_ticket)
    new_ticket.status = 'new'
    ticket_audit = zenpy_client.tickets.update(new_ticket)
#
# requester = zenpy_client.search(type='user', email="dilshad.davood@headout.com")
# if len(requester) > 0:
#     requester_id = requester[0:1][0].id
#     url = "https://docs.google.com/spreadsheets/d/13Fl19VWSSTZhgqMSgyDYpriH4QpR_qyaF2KQpePxarI"
#     description = f"""
#     Dear Partner,
#     I hope you and your team are doing well.
#
#     Please find the report for the period Oct 01, 2021 - Oct 31, 2021.
#
#     Sheet link : {url}
#
#     Let me know if this matches your records or if there are any discrepancies so that we can look into it and process payment accordingly.
#
#     Please get back to us on the same within 30 days of the report being sent, for any discrepancies or approval of payment per our report - We will initiate an auto-payment and close the loop on this invoice in case we don't hear back from you in the next 30 days.
#     Looking forward to hearing from you. :)
#     """
#
#     job_status = zenpy_client.tickets.create(
#         Ticket(subject="New Ticket Test", description=description, requester_id=requester_id,
#                custom_fields=[{
#                    "id": 360043126093,
#                    "value": "BALI"
#                },
#                    {
#                        "id": 360035587913,
#                        "value": "USD"
#                    },
#                    {
#                        "id": 360036150174,
#                        "value": "Vendor_Pending"
#                    },
#                    {
#                        "id": 360044350833,
#                        "value": "Regula_AP"
#                    },
#                    {
#                        "id": 360044350333,
#                        "value": "360_Amsterdam"
#                    },
#                    {
#                        "id": 360035978714,
#                        "value": "2021-10-01"
#                    },
#                    {
#                        "id": 360035978734,
#                        "value": "2021-10-31"
#                    },
#                    {
#                        "id": 360035698494,
#                        "value": "36.8"
#                    }
#                ]
#                )
#     )



# metrics = zenpy_client.ticket_metrics()
#
# def printOne(ticket):
#     print(ticket)
#     for metric in metrics:
#         print(metric)
#         if(ticket == metric.ticket_id):
#             print(metric.full_resolution_time_in_minutes)
#             return


# ticketIds = []
# yesterday = datetime.datetime.now() - datetime.timedelta(days=32)
# today = datetime.datetime.now()
# for ticket in zenpy_client.search(tags="payables", type='ticket', minus='negated'):
#     ticketIds.append([ticket.id, ticket.tags, ticket.status, ticket.created_at, ticket.assignee_id,ticket.via.channel,ticket.due_at])
# print(ticketIds)
#
# dataframe = pd.DataFrame(ticketIds)
# dataframe.to_csv('/Users/headout1/payables.csv')


# ticketIds.sort(reverse = True)

# for ticketId in ticketIds:
# printOne(ticketId)
# if(ticket.assignee_id):
#     print(ticket.id,ticket.tags,ticket.status,ticket.created_at,zenpy_client.users(id=ticket.assignee_id).name)
# else:
#     print(ticket.id, ticket.tags, ticket.status, ticket.created_at, ticket.assignee_id)

# ticketArrays = []
# for ticket in ticketIds:
#     ticketID = zenpy_client.tickets.metrics(ticket=ticket)
#     ticketArray = [ticketID.created_at,ticketID.initially_assigned_at,ticketID.assignee_stations,ticketID.reopens,
#                    ticketID.first_resolution_time_in_minutes,ticketID.solved_at,ticketID.full_resolution_time_in_minutes]
#     ticketArrays.append(ticketArray)
#
# print(ticketIds)


# ticket metrics search

# ticketID = zenpy_client.tickets.metrics(ticket=2653133)
#
# ticketArray = [ticketID.created_at,ticketID.initially_assigned_at,ticketID.assignee_stations,ticketID.reopens,
#                    ticketID.updated_at,ticketID.solved_at,ticketID.agent_wait_time_in_minutes]
#
# print(ticketArray)

# using with ticket Ids

# ticketdata = []
# ticketIds = []
# for ticket in zenpy_client.tickets(ids =ticketIds ):
#     ticketdata.append([ticket.id, zenpy_client.users(id=ticket.assignee_id).name])
# print(ticketdata)
#


# getting attachments from tickets

# attachment = zenpy_client.attachments(ticket=1655701)
# print(attachment.id,attachment.file_name,attachment.content_url,attachment.content_type)
# ticketdata = []
# ticketIds = []
# for ticket in ticketIds:
#     comments = zenpy_client.tickets.comments(ticket=ticket)
#     commentArray = comments[:]
#     for comment in commentArray:
#         if comment.attachments:
#             for attachment in comment.attachments:
#                 ticketdata.append([ticket, attachment.content_url])
#                 print(attachment.content_url)

# dataframe = pd.DataFrame(ticketdata)
# dataframe.to_csv('/home/so/Downloads/ticketData.csv')
