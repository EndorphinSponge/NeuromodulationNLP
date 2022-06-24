#%% Imports
# Built-ins
import os


os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# General
import pandas as pd
import numpy as np

# Spacy
import spacy 
from spacy.lang.en import English # Imports English model 
from spacy.pipeline import EntityRuler # Allows creation of rules for entities 
from spacy import displacy
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens import Span, Doc
from spacy.language import Language

from global_functions import importExcelData3
from postprocessing import processKeywords
from visualization import Visualizer

#%% Model selection - load required model by commenting in/out lines, documentation on models available on spaCy website
# NLP = spacy.load("en_core_web_trf") # Loads in model as an object which can be used as a function to analyze other strings 
NLP = spacy.load("en_core_web_lg") # Loads in model as an object which can be used as a function to analyze other strings 
# NLP = spacy.load("en_core_web_sm")

#%% Import data
if __name__ == "__main__":
    # ============= CHANGE DATA SOURCE BELOW ===============
    # texts = importExcelData3("data/Demo data.xls")
    texts = importExcelData3("data/Data.xls")
    # texts = importExcelData3("data/Embase Data.xls")
    # texts = importExcelData3("data/Neuromodulation Data.xls")

    docs = [(texts["AB"][index], {"mh":texts["MH"][index]}) for index in texts.index] # Zip together abstracts with MH (as part of dict item)

    #%% Pipeline components + Execution

    # Each import statement runs component module while adds their respective component to the NLP object 
    import component_parameters
    NLP.add_pipe("extractParameters")
    import component_sample_size
    NLP.add_pipe("extractSampleSize")
    import component_location
    NLP.add_pipe("extractTargets")

    # Pipeline execution 
    docs = list(NLP.pipe(docs, as_tuples=True))

    for doc, context in docs:
        print(doc._.get("frequency"))


    #%% Postprocessing 
    docs = processKeywords(docs)

    #%% Visualization (Outputs figures in ./figures directory)
    vis = Visualizer(docs)
    vis.visHeatmap("frequency", "Frequency (HZ)")
    vis.visHeatmap("voltage", "Voltage (V)")
    vis.visHeatmap("amperage", "Amperage (mA)")
    vis.visBargraph("targets_text", "Location of interest")
    vis.visBargraph("targets_text", "Location of interest", by_pts=True)
    vis.visBargraph("modality", "Modality of neuromodulation")
    vis.visBargraph("modality", "Modality of neuromodulation", by_pts=True)
    vis.visBargraph("disease_broad", "Epilepsy type (broad)")
    vis.visBargraph("disease_broad", "Epilepsy type (broad)", by_pts=True)
    vis.visBargraph("disease_narrow", "Epilepsy type (narrow)")
    vis.visBargraph("disease_narrow", "Epilepsy type (narrow)", by_pts=True)
    vis.visPyvis()


# %%
