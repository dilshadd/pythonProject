import pandas as pd
from urllib.request import Request, urlopen
import requests

def download(df):
    for i in range(df.shape[0]):
        url = df['url'][i]
        id = df['ID'][i]
        print(id)
        req = Request(url)
        r = requests.get(url)

        with open("/Users/headout1/workSpace/pythonProject/%s.pdf" %id, "wb") as code:
            code.write(r.content)

if __name__ == '__main__':
    filename = '/Users/headout1/workSpace/pythonProject/centre.csv'
    df = pd.read_csv(filename)
    download(df)