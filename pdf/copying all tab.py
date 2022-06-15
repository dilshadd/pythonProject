import pandas as pd
import openpyxl

## -----deleting tabs and saving

# workbook=openpyxl.load_workbook('/home/so/Downloads/1.xlsx')
# workbook.get_sheet_names()
# print(workbook.get_sheet_names())
# std=workbook.get_sheet_by_name('Raw data')
# std2=workbook.get_sheet_by_name('13876')
# std3=workbook.get_sheet_by_name('Sheet68')
# workbook.remove_sheet(std)
# workbook.remove_sheet(std2)
# workbook.remove_sheet(std3)
# workbook.get_sheet_names()
# print(workbook.get_sheet_names())
# workbook.save('/home/so/Downloads/1.xlsx')

# #---Different method to read sheetnames
#
# xl= pd.ExcelFile("/home/so/Downloads/1.xlsx")
# sheetNames = xl.sheet_names
# # Parsing Excel Sheet to DataFrame
# dfs = xl.parse(xl.sheet_names)
# dfs1= pd.DataFrame(sheetNames)



# #-------Combining tabs together
dfs = pd.read_excel('/home/so/Downloads/dil.xlsx', sheet_name=None)
# df2 = pd.read_excel('/home/so/Downloads/dil.xlsx', sheet_name='Sheet1')
# df1 = pd.read_csv('/home/so/Downloads/csv/1.csv')
# df2 = pd.read_csv('/home/so/Downloads/csv/2.csv')
# dfs = [df1,df2]
# dfs = pd.concat(dfs)
dfs = pd.concat([df.assign(name=n) for n,df in dfs.items()])

# # Find the columns where each value is null
# empty_cols = [col for col in dfs.columns if dfs[col].isnull().all()]
# # Drop these columns from the dataframe
# dfs.drop(empty_cols, axis=1,inplace=True)
# dfs.reset_index(drop=True, inplace=True)
#
#
print(dfs)
# dfs.to_csv('/home/so/Downloads/prod2.csv')

##-------Combine sheets
# df1 = pd.read_csv('/home/so/Downloads/pp sheet data/old_done.csv',low_memory=False)
# df2 = pd.read_csv('/home/so/Downloads/pp sheet data/new_done.csv',low_memory=False)
# df3 = pd.read_csv('/home/so/Downloads/pp sheet data/prod2.csv',low_memory=False)
#
#
# dfs= [df1,df2,df3]
# dfs = pd.concat(dfs, keys=['Old_PP','New_PP','prod_2'])
#
# print(dfs)
# dfs.to_csv('/home/so/Downloads/pp sheet data/three.csv')


#------ importinga nd copying for preprocess
# df = pd.read_excel('/home/so/Downloads/three.xlsx', sheet_name='three')
# print(df.columns)
# adult= df.copy()
# child = df.copy()
# senior = df.copy()
# general = df.copy()
# student = df.copy()
# sold = df.copy()
# sold2 = df.copy()
# EUR_adult = df.copy()
#
# adult.dropna(subset = ["Sold - Adult"], inplace=True)
# child.dropna(subset = ["Sold - Child"], inplace=True)
# senior.dropna(subset = ["Sold - Senior"], inplace=True)
# general.dropna(subset = ["Sold - General"], inplace=True)
# student.dropna(subset = ["Sold - Student"], inplace=True)
# sold.dropna(subset = ["Sold"], inplace=True)
# sold2.dropna(subset = ["Sold.1"], inplace=True)
# EUR_adult.dropna(subset = ["Sold - Eur_Adult"], inplace=True)
#
# df= [adult,child,senior,general,student,sold]
# new_df = pd.concat(df, keys=['adult','child','senior','general','student','sold','sold2','EUR_adult'])
#
#
# print(new_df)
# new_df.to_csv('/home/so/Downloads/complete.csv')
