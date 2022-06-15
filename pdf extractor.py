from tika import parser
import os
from csv import DictWriter
field_names = ['file_name', 'date', 'confirmation_number']
path = 'reina'  #Folder path
files = [file for file in os.listdir(path)]
for file in files:
    full_path = os.path.join(path, file)
    file_data = parser.from_file(filename=full_path)
    confirmation_number = file_data['content'].split("N° ")[1].split(" ")[0o00]  #for 13012
    print(file)
    print(confirmation_number)
    dict_data = dict(file_name=str(file), confirmation_number=str(confirmation_number))
    with open('parantheon.csv', 'a') as f_object:  #File Name
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)
        dictwriter_object.writerow(dict_data)
        f_object.close()