import requests
import json
import pandas as pd

token = "xoxp-2316821691-189244253458-1101782138546-dccc12c6848fdfc64d94be24ca01fbdf"
channel = "C280YFBQD"
thread = "1588533822.055900"
url = "https://slack.com/api/conversations.replies?token=" +token+ "&channel=" +channel+ "&ts=" +thread
payload = {}
headers = {
  'Content-type': 'application/json'
}
all_msgs = []
response = requests.request("GET", url, headers=headers, data = payload)
print(json.loads(response.content)['messages'])

messages = json.loads(response.content)['messages']
data = messages[0]['text']
print(data)

# for msg in messages:
#     data = msg['text']
#     all_msgs.append(data)
# all_messages = pd.DataFrame(all_msgs)
# print (all_messages)

# all_messages.to_csv('/home/so/Downloads/hey.csv')

credentials = GoogleCredentials.get_application_default()
service = build('sheets', 'v4', credentials=credentials)

list = [["valuea1"], ["valuea2"], ["valuea3"]]
resource = {
  "majorDimension": "ROWS",
  "values": list
}
spreadsheetId = "### spreadsheet ID"
range = "Sheet1!A:A";
service.spreadsheets().values().append(
  spreadsheetId=spreadsheetId,
  range=range,
  body=resource,
  valueInputOption="USER_ENTERED"
).execute()