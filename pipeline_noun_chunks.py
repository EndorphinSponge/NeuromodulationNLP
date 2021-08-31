# -*- coding: utf-8 -*-

from global_functions import *

#%% Temp

# printNounChunks("Data.xls", 1, nlp2)
# renderParseTreeKeyword(doc, nlp2, "patient", "stimulat")
# ent_list = ["spinal cord", "medulla", "pons", "midbrain", "cerebellum", "thalamus", "cerebrum"]

# df1 = extractNounChunksRoot("Data.xls", "stimulation", "Modality", "AB")
# df2 = extractNounChunksRoot("Data.xls", "area", "Location", "AB")
# df3 = extractNounChunksRoot("Data.xls", "epilepsy", "Condition", "AB")
# df4 = extractNounChunksRoot("Data.xls", "patients", "Patient", "AB")



#%% Processes

# renderParseTree(doc)
# printDepLabels(nlp2)
# print(calcSimilarity(doc, "patients"))
# chunks = getNounChunks(doc)
# deps = getDepLabels(doc, 3)

#%% Graph networkx

def appendChunk(original, chunk):
    return original + ' ' + chunk

def isRelationCandidate(token):
    deps = ["ROOT", "adj", "attr", "agent", "amod"]
    return any(subs in token.dep_ for subs in deps)

def isConstructionCandidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)

def processSubjectObjectPairs(tokens):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        if "punct" in token.dep_:
            continue
        if isRelationCandidate(token):
            relation = appendChunk(relation, token.lemma_)
        if isConstructionCandidate(token):
            if subjectConstruction:
                subjectConstruction = appendChunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = appendChunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = appendChunk(subject, token.text)
            subject = appendChunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = appendChunk(object, token.text)
            object = appendChunk(objectConstruction, object)
            objectConstruction = ''
    print(subject.strip(), ",", relation.strip(), ",", object.strip())
    return (subject.strip(), relation.strip(), object.strip())


def printGraph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='seagreen', alpha=0.9,
            labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.show()

text = importExcelData("data.xls", 1)
sentences = processText(text, nlp2).sents
triples = []
for sentence in sentences:
    triples.append(processSubjectObjectPairs(sentence))

printGraph(triples)

#%% Graph bar

# df1 = extractNounChunksRoot("Embase Data.xls", "stimulation", "Modality", "AB")
df3 = extractNounChunksRoot("Embase Data.xls", "epilepsy", "Condition", "AB")
# graphTermFrequencies(df1, "Modality")
graphTermFrequencies(df3, "Condition")

#%% Test
df = extractNounChunksRoot("Data.xls", "stimulation", "Modality", "AB")
graphTermFrequencies(df, "Modality")
