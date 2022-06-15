import textract,glob
import pandas as pd
pnr = []
pdfs = glob.glob('/home/so/Downloads/disney/*.pdf')
for pdf in pdfs:
    file_name = pdf.split('/')[-1]
    print(file_name)
    text= textract.process(pdf)
    data = text.decode("utf-8")
    split1 = data.split('Certain exclusions apply.Please see the calendar below for details.')
    print(len(split1))
    ids = []
    for i in range(1,len(split1)):
        split2 = split1[i].split('CnC')
        id = split2[0:1]
        ids.extend(id)
    ids.insert(0, file_name)
    pnr.append(ids)
dataframe = pd.DataFrame(pnr)
dataframe.to_csv('/home/so/Downloads/disney.csv')