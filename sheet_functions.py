import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from apiclient import errors

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/headout1/workSpace/service_account_credentials.json"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
KEY_FILE_LOCATION = '/Users/headout1/workSpace/service_account_credentials.json'

credentials = service_account.Credentials.from_service_account_file(KEY_FILE_LOCATION)

service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

def check_user_files():
    result = []
    page_token = None
    while True:
        param = {}
        if page_token:
            param['pageToken'] = page_token
        files = drive_service.files().list(**param).execute()

        for file in files['files']:
            if file.get('name') == "Master sheet for links":
                print(file)
                result.extend(file)
        page_token = files.get('nextPageToken')
        if not page_token:
            break
    print(result)

def move_sheets(spreadsheetId,folderId):
    # Move the created Spreadsheet to the specific folder.
    drive_service.files().update(fileId=spreadsheetId, addParents=folderId,
                                 removeParents='root').execute()

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

    batch = drive_service.new_batch_http_request()
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': mail,

    }
    batch.add(drive_service.permissions().create(fileId=sheet_id,
                                                 body=user_permission,
                                                 fields='id',
                                                 sendNotificationEmail=False
                                                 ))

    batch.execute()


spreadsheetId = "1cx7Evkh3TAlf2eUGj29qMo36tKRB6RTc7_X0rvjEqac"
mail = "dilshad.davood@headout.com"
folderId = "1nROddFIrWW_oJMHWlY5ttQ5EFHFF8JH_"

# insert_permission(spreadsheetId, mail)

move_sheets(spreadsheetId,folderId)