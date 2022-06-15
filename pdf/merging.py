from PyPDF2 import PdfFileReader,PdfFileMerger
import glob

folder_path1 = '/home/so/Downloads/1pm/free'
folder_path2 = '/home/so/Downloads/1pm/pp'
end_folder = '/home/so/Downloads/1pm'

pdfs1 = glob.glob(folder_path1+'/*.pdf')
pdfs2 = glob.glob(folder_path2+'/*.pdf')
pdfname = []

for pdf in pdfs2:
    file_name = pdf.split('/')[6]
    pdfname.append(file_name)
print(pdfname)

i = 0
for pdf1 in pdfs1:
    merger = PdfFileMerger()
    fp1 = PdfFileReader(open(pdf1, 'rb'))
    fp2 = PdfFileReader(open(folder_path2+'/%s' % pdfname[i], 'rb'))
    merger.append(fp1)
    merger.append(fp2)
    merger.write(end_folder+"/%s.pdf" %pdfname[i])
    i = i + 1