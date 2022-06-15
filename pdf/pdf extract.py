from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import  TextConverter
from pdfminer.layout import LAParams
import glob,PyPDF2
import pandas as pd

def pdfparser():
    PyPDF2.pdf._override_encryption = True
    pnr = []
    pdfs = glob.glob('/home/so/Downloads/disney/*.pdf')
    for pdf in pdfs:
        try:
            file_name = pdf.split('/')[-1]
            fp = open(pdf, 'rb')
            pdfReader = PyPDF2.PdfFileReader(fp)
            count = pdfReader.numPages
            for i in range(count):
                page = pdfReader.getPage(i)
                data = page.extractText()
                data.insert(0, file_name)
                pnr.append(data)

        except:
            print('encrypted')

    dataframe = pd.DataFrame(pnr)
    return dataframe
if __name__ == '__main__':
    dataframe = pdfparser()
    dataframe.to_csv('/home/so/Downloads/disney.csv')
