from PyPDF2 import PdfFileWriter, PdfFileReader
import glob


def pdf_split1(pdf, folder_path):
    fp = PdfFileReader(open(pdf, 'rb'))
    for i in range(fp.getNumPages()):
        output = PdfFileWriter()
        output.addPage(fp.getPage(i))
        with open(folder_path + "%s.pdf" % i, "wb") as outputStream:
            output.write(outputStream)


def pdf_msm(folder, end_folder):
    pdfs = glob.glob(folder + '*.pdf')
    for pdf in pdfs:
        fp = PdfFileReader(open(pdf, 'rb'))
        file_name = pdf.split('/')[5]
        output = PdfFileWriter()
        output.addPage(fp.getPage(0))
        with open(end_folder+'%s.pdf' % file_name, 'wb') as outputStream:
            output.write(outputStream)


# To split one pdf file

pdf = "/home/so/Downloads/3.3pm/3.3pm.pdf"
folder_path = "/home/so/Downloads/3.3pm/free/"
pdf_split1(pdf, folder_path)

# # To split 2 pdfs file to one - MSM
#     folder = "/home/so/Downloads/test/"
#     end_folder = "/home/so/Downloads/msm/"
#     pdf_msm(folder, end_folder)
