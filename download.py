import requests
import pandas as pd

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination)
    print("done")

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    df = pd.read_csv('pena.csv')
    file_ids = df['ticket_data'][:68]
    # print(file_ids)
    for file in file_ids:
        destination = 'pena/{}.pdf'.format(file)
        download_file_from_google_drive(file, destination)

    # #Single testing
    # file = "1-0j81I7KouV9xKyYfUCSi4yVSLUVLv9D"
    # destination = '{}.pdf'.format(file)
    # download_file_from_google_drive(file, destination)