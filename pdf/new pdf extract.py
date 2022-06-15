import requests, PyPDF2, io, os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import pandas as pd
import textract



pnr = []

def vatican(pdf_content,url):
    for page in PDFPage.get_pages(pdf_content, check_extractable=False):
        # Create a PDF interpreter object.
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        data = retstr.getvalue()
        split = data.split('Headout UK Ltd\n\n')
        split2 = split[1].split('\n\nCode')
        pnr.append([url, split2[0]])
        break


# def Arc(pdf_content,url):
#     for page in PDFPage.get_pages(pdf_content, check_extractable=False):
#         # Create a PDF interpreter object.
#         rsrcmgr = PDFResourceManager()
#         retstr = io.StringIO()
#         codec = 'utf-8'
#         laparams = LAParams()
#         device = TextConverter(rsrcmgr, retstr,codec=codec, laparams=laparams)
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#         interpreter.process_page(page)
#         data = retstr.getvalue()
#         split = data.split('')
#         split2 = split[1].split('\n')
#         pnr.append([url, split2[0]])

def Disney(pdf_content,url):
    for page in PDFPage.get_pages(pdf_content, check_extractable=False):
        # Create a PDF interpreter object.
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr,codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        data = retstr.getvalue()
        split = data.split()
        split.insert(0,url)
        # split2 = split[1].split('\n')
        pnr.append(split)

def textExtraction(pdf_content,url):
    text = textract.process(pdf_content)
    print(text)


def pdfparser(links):
    for i in links:
        url = "https://drive.google.com/uc?id="+i+"&export=download"
        try:
            response = requests.get(url)
            my_raw_data = response.content

            pdf_content = io.BytesIO(my_raw_data)
            try:
                pdf_reader = PyPDF2.PdfFileReader(pdf_content)

                if pdf_reader.isEncrypted:
                    try:
                        pdf_reader.decrypt('')
                        print('File Decrypted (PyPDF2)')
                    except:
                        command = "cp " + url + " temp.pdf; qpdf --password='' --decrypt temp.pdf " + url
                        os.system(command)
                        print('File Decrypted (qpdf)')
                        # re-open the decrypted file
                        response = requests.get(command)
                        my_raw_data = response.content
                        pdf_content = io.BytesIO(my_raw_data)
                        pdf_reader = PyPDF2.PdfFileReader(pdf_content)
                else:
                    print('File Not Encrypted')

                # vatican(pdf_content,url)
                # Arc(pdf_content,url)
                textExtraction(pdf_content, url)


            except AssertionError as error:
                print(error)
                pnr.append([url,'1'])
        except AssertionError as error:
            print(error)
            pnr.append([url, '2'])
    dataframe = pd.DataFrame(pnr)
    print(dataframe)
    return dataframe


if __name__ == '__main__':
# Link should be in this format "https://drive.google.com/uc?id=PDFLINKID&export=download" under header "url"
    filename = '/Users/headout1/workSpace/pythonProject/centre.csv'
    download_file_path = filename.replace('.csv','_PNR.csv')
    df = pd.read_csv(filename)
    links = df['ticket_data'][1:3]
    dataframe = pdfparser(links)

    dataframe.to_csv(download_file_path)