import os
import pandas as pd

file_name = input("File name (without extension)")

cwd = os.path.abspath('') 
files = os.listdir(cwd) 

df = pd.DataFrame()
for file in files:
    if file.endswith(".xls"):
        df = df.append(pd.read_excel(file), ignore_index=True)


df.to_excel(file_name+".xls")
