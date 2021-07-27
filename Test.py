# -*- coding: utf-8 -*-

# import pandas as pd
# import numpy as np
# import math
import spacy 
import textacy
from spacy import displacy
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

#%% Extracting nouns

nouns = []
for token in sentence1:
    if token.pos_ == "NOUN":
        nouns.append(token)
    print(type(token))
        

#%% Extracting noun chunks with patient mention
chunks = list(doc.noun_chunks)
patients = []
for chunk in chunks:
    if "patient" in str(chunk):
        patients.append(chunk)
print(str(patients))

#%% Extracting number info from noun chunks 

for entry in patients:
    entry = entry.ents
    for word in entry:
        if word.label_ == ("CARDINAL" or "QUANTITY"):
            print(w2n.word_to_num(word.text))


#%% Lemmatization demo 
for token in sentence1:
    if token.pos_ == "VERB":
        print(token, token.lemma_)
        
#%% Displaying syntactical tree 
html_dep = displacy.render(sentence1, jupyter=False, style="dep")
html_ent = displacy.render(doc, jupyter=False, style="ent")

with open("Syntactical_tree.html", "w") as file: 
    file.writelines(html_dep)
    
#%% Test

a = "apples grapes"
b = "apples"
c = "grapes"
d = "pears"
e = "potatoes"