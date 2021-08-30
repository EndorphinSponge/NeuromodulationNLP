# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 11:50:40 2021

@author: steve
"""

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
    
#%% Packing results into dictionary 

azip = zip(range(50), pt_tracker)
adict = {index+1:item for (index, item) in azip}



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
        

