# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import math
import spacy
from spacy.lang.en import English
import time
from word2number import w2n



#%% Raw data 
raw = pd.read_excel('Data.xls', skiprows=1) # remember to skip first row which contains copyright info 
raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
raw = raw.dropna (subset = ["AB"])
raw = raw.loc[raw["AB"].str.contains("Hz")]
filtered = raw[["ORN","TI","AU","KW","AB"]]
filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again


#%% Model loading
nlp = spacy.load("en_core_web_trf") #loads in model as an object which can be used as a function to analyze other strings 

#%% Text processing on single entry
doc = nlp(filtered["AB"][0])
sentences = list(doc.sents)
sentence1 = sentences[0]
sentence2 = sentences[1]

#%% Text processing sequentially 
start_time = time.time()
pt_tracker = []
freq_tracker = []
for doc in filtered["AB"]:
    doc = nlp(doc)
    patients = []
    freq = []
    for chunk in list(doc.noun_chunks):        
        if ("patient" in str(chunk)) or ("subject" in str(chunk)): # added "subject" to arguments after discovering missing data during extraction
            patients.append(chunk)
        if "Hz" in str(chunk): 
            freq.append(chunk)
    pt_tracker.append(patients)
    freq_tracker.append(freq)    
end_time = time.time()
print(end_time - start_time)

#%% Printing report

row = 1 
for entry in pt_tracker:
    if entry == []: #to print only indices with empty containers 
        print(row, entry)
    row += 1

#%% Packing results into dictionary 

azip = zip(range(50), pt_tracker)
adict = {index+1:item for (index, item) in azip}

#%% Extracting number info from noun chunks 
patient_num = []
for patients in pt_tracker:
    numbers = []
    for entry in patients:
        if (str(entry).lower() == "a patient") or \
            (str(entry).lower() == "the patient") or \
            (str(entry).lower() == "a subject") or \
            (str(entry).lower() == "the subject"): # these arguments have to come first, otherwise the second set of conditions will catch them before being processed by these arguments
            numbers.append(1)
        entry = entry.ents
        for word in entry:            
            if ((word.label_ == "CARDINAL") or (word.label_ == "QUANTITY")) and (word.text != ""):
                try: numbers.append(w2n.word_to_num(word.text)) #Sample data has "six6" in entry ORN 19 which can't be parsed, this is to catch similar exceptions
                except ValueError: pass
                finally: pass            
    patient_num.append(numbers)
patient_max = []
for study in patient_num:
    if study != []:
        patient_max.append(max(study))
    else: patient_max.append([])
        

#%% Extracing frequency data
freq_num = []
for frequencies in freq_tracker:
    freq_list = []
    for entry in frequencies:
        entry = entry.ents
        for word in entry:  
            # print(word.label_, word.text)
            if (word.label_ == "CARDINAL") or\
                (word.label_ == "QUANTITY") or\
                (word.label_ == "PERCENT"):
                freq_list.append(word.text)    
    freq_num.append(freq_list)















#%% Test

tokenizer = English().tokenizer
# mask = np.column_stack([abstract.str.contains(" Hz ") for abstract in data["AB"]])
 

#%% Filter - Alternate method

# df = pd.DataFrame(columns = ["TI", "KW", "AB"])
# a = 0
# for abstract in data["AB"]:
#     if (type(abstract) == str) and ("Hz" in abstract):
#         df = df.append({
#             "TI":data["TI"][a],
#             "KW":data["KW"][a],
#             "AB":data["AB"][a]
#             },ignore_index=True)
#     a += 1
        
#%% Length Tester

# length = []
# for abstract in data["AB"]:
#     if (type(abstract) == str):
#         length.append(1)
#     print(len(length))
        



