from pdf2image import convert_from_bytes
from PyPDF2 import PdfFileWriter, PdfFileReader
from PIL import Image
from pyzbar.pyzbar import decode
import io,glob
import pandas as pd

def pdfToImage(input_file):
    inp = PdfFileReader(input_file, "rb")
    page = inp.getPage(0)

    # print(page.cropBox.getLowerLeft())
    # print(page.cropBox.getLowerRight())
    # print(page.cropBox.getUpperLeft())
    # print(page.cropBox.getUpperRight())
    #
    # page.mediaBox.lowerLeft = (0, 600)
    # page.mediaBox.lowerRight = (595, 600)
    # page.mediaBox.upperLeft = (0, 842)
    # page.mediaBox.upperRight = (595, 842)


    wrt = PdfFileWriter()
    wrt.addPage(page)
    r = c
    wrt.write(r)
    images = convert_from_bytes(r.getvalue())
    # images[0].save(input_file[:-4]+".png")
    images[0].save("/home/so/Downloads/1.png")
    r.close()

if __name__ == "__main__":
    pnr = []
    pdfs = glob.glob('/home/so/Downloads/new/*.pdf')
    for pdf in pdfs:
        pdfToImage(pdf)
        im = Image.open('/home/so/Downloads/1.png')
        im_crop = im.crop((500, 300, 1000, 900))
        # im_crop.show()
        data = decode(im_crop)
        file_name = pdf.split('/')[5]
        barcode = (data[0].data).decode("utf-8")
        print(file_name,barcode)
        pnr.append([file_name,barcode])

    dataframe = pd.DataFrame(pnr)
    dataframe.to_csv('/home/so/Downloads/centre.csv')
