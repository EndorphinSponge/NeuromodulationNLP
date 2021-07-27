import pandas
import numpy
from collections import Counter

data = pandas.read_excel('Data.xls', skiprows=1) # remember to skip first row which contains copyright info 
data = data.drop_duplicates(subset='TI')

'''Author data'''

# author_list = data['AU'].str.split('\\n\\n')
# # print(author_list.describe(include=numpy.object).transpose())
# author_list_flat = []
# for sublist in author_list:
#     for item in sublist:
#         author_list_flat.append(item)

# author_list_counter = Counter(author_list_flat).most_common(50)
# print(author_list_counter)

# author_freq = pandas.DataFrame.from_records(author_list_counter, columns=['Authors', 'Count'])
# author_freq.plot(kind='bar', x='Authors', fontsize=30, figsize=(40,20))

'''Label data'''

keyword_list_flat = []
for sublist in data['KW'].str.split('\\n\\n'):
    if type(sublist) == list:
        for item in sublist:
            keyword_list_flat.append(item)

keyword_list_counter = Counter(keyword_list_flat).most_common(50)
keyword_freq = pandas.DataFrame.from_records(keyword_list_counter, columns=['Keywords', 'Count']).plot(kind='bar', x='Keywords', fontsize=30, figsize=(40,20))

mesh_list_flat = []
for sublist in data['MH'].str.split('\\n\\n'):
    if type(sublist) == list:
        for item in sublist:
            mesh_list_flat.append(item)

mesh_list_counter = Counter(mesh_list_flat).most_common(50)
mesh_freq = pandas.DataFrame.from_records(mesh_list_counter, columns=['Keywords', 'Count']).plot(kind='bar', x='Keywords', fontsize=30, figsize=(40,20))


pb_list_flat = []
for sublist in data['PB'].str.split('\\n\\n'):
    if type(sublist) == list:
        for item in sublist:
            pb_list_flat.append(item)

pb_list_counter = Counter(pb_list_flat).most_common(50)
pb_freq = pandas.DataFrame.from_records(pb_list_counter, columns=['Keywords', 'Count']).plot(kind='bar', x='Keywords', fontsize=30, figsize=(40,20))


#%% Misc
# authors_titles = data[['TI', 'AU']]
# print(authors_titles.describe(include=numpy.object).transpose())


# print(data.columns)

# columns = data.columns.tolist()
# print(columns.index('OD'))
# column_index = data.columns.tolist().index('OD') # this combines the above two statements

# print(data['OD'])
# print(data[['OD', 'TI']])
# print(data.iloc[0:4]) # returns specific location, can also put a range 
# print(data.iloc[2, columns.index('AB')]) # using index function, can find specific field for a given entry
# print(data.loc[~data['OD'].str.contains('human')]) # to find entries with human in OD column
# print(data.loc[~data['OD'].str.contains('human')]['TI']) # prints the titles of the entries found above
# data.loc[data['DB'] == 'Embase', 'DB'] = 'EM' # changes all instances of Embase in DB column to EM


# for index, row in data.iterrows():
#     print(index, row['OD']) # reads through only OD column for each row
    