# -*- coding: utf-8 -*-
# Built-ins
import time
from collections import Counter
import os
from typing import Union, List

# General
import pandas as pd

# Spacy
import spacy 
from spacy.lang.en import English; # Imports English model 
from spacy.pipeline import EntityRuler; # Allows creation of rules for entities 
from spacy import displacy;
from spacy.matcher import PhraseMatcher, Matcher;
from spacy.tokens import Span, Doc;
from spacy.language import Language;



# Plotting tools
import networkx as nx
import matplotlib.pyplot as plt

#%% Diagnostic functions
def getWordIndex(doc: Union[Span, Doc], word: str):
    """
    Obtains the index (with respect to the doc) of first occurence of the word within the doc
    """
    keyword = word
    keyword_indices = []
    for token in doc:
        if token.text.strip() == keyword:
            keyword_indices.append(token.i)
    return min(keyword_indices)

def calcSimilarity(doc: Union[Span, Doc], word: str):
    """
    Obtains top 5 similar entries in the doc to the word specified
    """
    similarity_scores = []
    index = getWordIndex(doc, word)
    for token in doc:
        similarity = token.similarity(doc[index])
        similarity_scores.append((token.text, similarity))
    similarity_scores = list(set(similarity_scores)) # Remove duplicate entries 
    similarity_scores.sort(key=lambda tup: tup[1], reverse=True) # Sort list based on second item in tuple 
    return similarity_scores[0:5]

def renderParseTree(doc: Union[Span, Doc]):
    """
    Generates HTML rendering of parse tree from given doc
    """
    html = displacy.render(list(doc.sents), options = {"compact":True}, jupyter=False) # Renders parse tree of sentences in a doc
    with open("Syntactical_tree.html", "w") as file:
        file.write(html)
        
def printDepLabels(model: Language):
    """
    Prints list of DEP labels in a given spacy language model
    """
    for label in model.get_pipe("parser").labels:
        print(label, " -- ", spacy.explain(label))
        
def getNounChunks(doc: Union[Span, Doc]):
    """
    Returns noun chunks within docs as a list
    """
    chunks = []
    for chunk in doc.noun_chunks:
        chunks.append((chunk.text, chunk.label_))
    return chunks

def getDepLabels(doc: Union[Span, Doc], sentence: int):
    """
    Returns DEP labels for each token within a sentence of docs as a list
    """
    deps = []
    for token in list(doc.sents)[sentence]:
        deps.append((token.text, token.dep_))
    return deps

def getSentencesContaining(doc: Union[Span, Doc], *words: List[str]):
    """
    Returns a list of all the sentences containing the specified strings
    """
    sentences = []
    for sentence in doc.sents:
        if any(word in sentence.text for word in words):
            sentences.append(sentence.text)
    return sentences

def renderParseTreeKeyword(doc: Union[Span, Doc], model: Language, *keywords: List[str]):
    """
    Renders parse tree of sentences within a doc with the specified keywords using the given model
    """
    sentences = getSentencesContaining(doc, *keywords) # Asterisk needed to unpack keyword arguments, otherwise gets passed as a list 
    text = " ".join(sentences)
    doc = processText(text, model)
    renderParseTree(doc)
    
def printNounChunks(data: Union[str, os.PathLike], ab_num: int, model):
    """
    Prints noun chunk analysis of an abstract using the given model
    data: Path to excel file
    subset: Index of abstract within the excel file
    # FIXME
    """
    text = importExcelData1(data, ab_num) # Tested 0-5
    doc = processText(text, model)
    for chunk in doc.noun_chunks:
        print("Root:",chunk.root)
        print("Conjuncts:",chunk.conjuncts)
        print("Environ:", list(chunk.lefts), "<", chunk.text, ">", list(chunk.rights))
        print("")

#%% Pipeline functions 
def importExcelData1(data: Union[str, os.PathLike], ab_num: int, filt: str = None):
    """
    Returns a single str abstract based on imported Excel data filterd using preliminary str filter
    data: Path to Excel file
    ab_num: Index of the specific abstract to extract from the Excel file 
    filt: String filter to apply to abstract #FIXME
    """
    raw = pd.read_excel(data, skiprows=1) # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
    raw = raw.dropna (subset = ["AB"])
    if filt != None:
        raw = raw.loc[raw["AB"].str.contains(filt)] # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","MH","AB"]]
    filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again
    return filtered["AB"][ab_num]

def importExcelData2(data: Union[str, os.PathLike], filt: str = None):
    """
    Returns iterable of str abstracts based on imported Excel data filterd using preliminary str filter
    """
    raw = pd.read_excel(data, skiprows=1) # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
    raw = raw.dropna (subset = ["AB"])    
    if filt != None:
        raw = raw.loc[raw["AB"].str.contains(filt)] # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","MH","AB"]]
    filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again
    return filtered["AB"]

def importExcelData3(data: Union[str, os.PathLike], filt: str = None):
    """
    Returns entire processed DF based on imported Excel data filterd using preliminary str filter
    """
    raw = pd.read_excel(data, skiprows=1); # remember to skip first row which contains copyright info 
    raw = raw.drop_duplicates(subset='TI'); # drop duplicates based on title 
    raw = raw.dropna(subset = ["AB"]);
    raw = raw[raw["AB"].str.contains(r"[A-Za-z]", regex = True) == True]; # Only allow non-empty strings through
    raw = raw[raw["MH"].str.contains(r"[A-Za-z]", regex = True) == True]; # Only allow non-empty strings through
    if filt != None:
        raw = raw.loc[raw["AB"].str.contains(filt)]; # Filters abstracts based on a str
    filtered = raw[["ORN","TI","AU","KW","MH","AB"]];
    filtered = filtered.reset_index(); # to re-index dataframe so it becomes iterable again
    return filtered;

def processText(text: str, model: Language):
    """
    Returns processed text by taking raw str and processesing it through an NLP model
    """
    processed_text = model(text)
    return processed_text

def extractNounChunksRoot(data: Union[str, os.PathLike], root: str, root_column: str, column: str, model):
    """
    Returns DF with extracted noun chunks based on root and other additional columns in the original DF
    root_column: Label for column for output extracted info
    column: Label of a column from the original dataframe to return in the output
    """
    st = time.time()
    df = pd.DataFrame(columns = ["ORN", root_column, column]) # Should replace Index with ORN with reference to original DF, need to update import function 
    data = importExcelData3(data)
    for index, row in data.iterrows():
        print(index)
        spans = []
        doc = processText(str(row[column]), model)
        for chunk in doc.noun_chunks:
            if chunk.root.text == root:
                spans.append(chunk.text)
        df = df.append({"ORN": row["ORN"], root_column: spans, column: row[column]}, ignore_index=True)
    ed = time.time()
    print(ed - st)
    return df


def graphTermFrequencies(df: pd.DataFrame, column_name: str):
    """
    column_name: Name of column search terms
    # FIXME
    """
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



#%% dev
