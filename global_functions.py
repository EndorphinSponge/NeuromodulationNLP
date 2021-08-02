# -*- coding: utf-8 -*-

# General
import pandas as pd
import json
import re
import time
import numpy as np
import math

# Spacy
import spacy 
from spacy.lang.en import English # Imports English model 
from spacy.pipeline import EntityRuler # Allows creation of rules for entities 
from spacy import displacy


# Plotting tools
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

# Misc
from word2number import w2n
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"



#%% Model loading TRF
nlp = spacy.load("en_core_web_trf")
#%% Model loading LG
nlp2 = spacy.load("en_core_web_lg")

#%% Diagnostic functions
def getWordIndex(doc: "doc, NLP-processed str", word: str) -> "Obtains the index (with respect to the doc) of first occurence of the word within the doc":
    keyword = word
    keyword_indices = []
    for token in doc:
        if token.text.strip() == keyword:
            keyword_indices.append(token.i)
    return min(keyword_indices)

def calcSimilarity(doc: "doc, NLP-processed str", word: str) -> "Obtains top 5 similar entries in the doc to the word specified":
    similarity_scores = []
    index = getWordIndex(doc, word)
    for token in doc:
        similarity = token.similarity(doc[index])
        similarity_scores.append((token.text, similarity))
    similarity_scores = list(set(similarity_scores)) # Remove duplicate entries 
    similarity_scores.sort(key=lambda tup: tup[1], reverse=True) # Sort list based on second item in tuple 
    return similarity_scores[0:5]

def renderParseTree(doc: "doc, NLP-processed str") -> "Generates HTML rendering of parse tree from given doc":
    html = displacy.render(list(doc.sents), options = {"compact":True}, jupyter=False) # Renders parse tree of sentences in a doc
    with open("Syntactical_tree.html", "w") as file:
        file.write(html)
        
def printDepLabels(model: "NLP model") -> "Prints list of DEP labels in given model":
    for label in model.get_pipe("parser").labels:
        print(label, " -- ", spacy.explain(label))
        
def getNounChunks(doc: "doc, NLP-processed str") -> "Returns noun chunks within docs as a list":
    chunks = []
    for chunk in doc.noun_chunks:
        chunks.append((chunk.text, chunk.label_))
    return chunks

def getDepLabels(doc: "doc, NLP-processed str", sentence: int) -> "Returns DEP labels for each token within a sentence of docs as a list":
    deps = []
    for token in list(doc.sents)[sentence]:
        deps.append((token.text, token.dep_))
    return deps

def getSentencesContaining(doc: "doc, NLP-processed str", *words: "any number of str words") -> "Returns a list of all the sentences containing the specified strings":
    sentences = []
    for sentence in doc.sents:
        if any(word in sentence.text for word in words):
            sentences.append(sentence.text)
    return sentences

def renderParseTreeKeyword(doc: "doc, NLP-processed str", model: "NLP model", *keywords: "Keyword strs to search for") -> "Renders parse tree of sentences within a doc with the specified keywords using the given model":
    sentences = getSentencesContaining(doc, *keywords) # Asterisk needed to unpack keyword arguments, otherwise gets passed as a list 
    text = " ".join(sentences)
    doc = processText(text, model)
    renderParseTree(doc)
    
def printNounChunks(data: "XLS file/path", subset: "int of abstract number", model) -> "Prints noun chunk analysis of an abstract using the given model":
    text = importExcelData(data, subset) # Tested 0-5
    doc = processText(text, model)
    for chunk in doc.noun_chunks:
        print("Root:",chunk.root)
        print("Conjuncts:",chunk.conjuncts)
        print("Environ:", list(chunk.lefts), "<", chunk.text, ">", list(chunk.rights))
        print("")


#%% Pipeline functions 
def importExcelData1(data: "str of Excel file name/filepath",ab_num: "Abstract index to return") -> "Returns str abstract based on imported Excel data":
    raw = pd.read_excel(data, skiprows=1) # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
    raw = raw.dropna (subset = ["AB"])
    # raw = raw.loc[raw["AB"].str.contains("Hz")] # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","AB"]]
    filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again
    return filtered["AB"][ab_num]

def importExcelData2(data: "str of Excel file name/filepath") -> "Returns iterable of str abstracts based on imported Excel data":
    raw = pd.read_excel(data, skiprows=1) # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
    raw = raw.dropna (subset = ["AB"])
    # raw = raw.loc[raw["AB"].str.contains("Hz")] # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","AB"]]
    filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again
    return filtered["AB"]

def importExcelData3(data: "str of Excel file name/filepath") -> "Returns entire processed DF based on imported Excel data":
    raw = pd.read_excel(data, skiprows=1) # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
    raw = raw.dropna (subset = ["AB"])
    # raw = raw.loc[raw["AB"].str.contains("Hz")] # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","AB"]]
    filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again
    return filtered

def processText(text: str, model: "SpaCy NLP model") -> "Returns processed text by taking raw str and processesing it through an NLP model":
    processed_text = model(text)
    return processed_text

def extractNounChunksRoot(data: str, root: str, root_column: "str with label for column for extracted info", column: "extra column to include in output") -> "Returns DF with extracted noun chunks based on root and other additional columns in the original DF":
    st = time.time()
    df = pd.DataFrame(columns = ["ORN", root_column, column]) # Should replace Index with ORN with reference to original DF, need to update import function 
    data = importExcelData3(data)
    for index, row in data.iterrows():
        print(index)
        spans = []
        doc = processText(str(row[column]), nlp2)
        for chunk in doc.noun_chunks:
            if chunk.root.text == root:
                spans.append(chunk.text)
        df = df.append({"ORN": row["ORN"], root_column: spans, column: row[column]}, ignore_index=True)
    ed = time.time()
    print(ed - st)
    return df



def getLabel(doc: "doc, NLP-processed str") -> "Retrieves labels from NLP-processed text and stores ":
    pass

def identifyTriples(labelled: "Labelled str") -> "___ returns labels":
    pass

def graphTermFrequencies(df: "DataFrame", column_name: "Name of column search terms") -> "":
    st = time.time()
    word_list = []
    for index, row in df.iterrows():
        terms = list(set(row[column_name])) # To merge duplicate terms within one entry
        for term in terms:
            word_list.append(term.lower().strip())
    word_counter = Counter(word_list).most_common(25)
    word_df = pd.DataFrame.from_records(word_counter, columns=['Terms', 'Count'])
    word_graph = word_df.plot(kind='bar', x='Terms', fontsize=30, figsize=(40,20))
    ed = time.time()
    print(ed - st)

def graphTriples():
    pass
