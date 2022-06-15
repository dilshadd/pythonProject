# coding=utf-8
import glob
import textract
import pandas as pd


def pdfExtract(path):
    ticketData = []
    for pdf in glob.glob(path):
        name = pdf.split('/')[-1].replace(".pdf", "")
        text = textract.process(pdf).decode()
        # print(text)
        try:
            split1 = text.split("N° ")[1]
            reservation = split1.split("\n")[0]
        except:
            #USE for second type
            split1 = text.split("N° ")[1]
            reservation = split1.split("\n")[0]

        print(name)
        ticketData.append([name, reservation])
    df = pd.DataFrame(ticketData)
    df.to_csv("pena.csv")


if __name__ == '__main__':
    pdfExtract('pena/*')

# Testing

# text = textract.process('bmg.pdf')
# split1 = text.split("Cancellations are non refundable.")[1]
# split2 = split1.split("OPERATED")[0]
# ticketId = split2.replace("\n","")
# ticketId2 = ticketId.replace(" ","")
# print(ticketId2)


# BMG
#     split1 = text.split("Cancellations are non refundable.")[1]
#     split2 = split1.split("OPERATED")[0]
#     ticketId = split2.replace("\n","")
#     ticketId2 = ticketId.replace(" ","")
#     print(ticketId2)
# Dupai Park
#         split1 = text.split("\n")
#         print(split1)
#         # split2 =  split1[1].split("ABSEA")
#         # PNR = split2[0]
#         # split3 = split2[1].split("https://www.dubaiparksandresorts.com/en/terms-conditions.")
#         # ticketId = split3[1].replace("\x0c","")
