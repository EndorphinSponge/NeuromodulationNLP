# -*- coding: utf-8 -*-

from global_functions import *


#%%

from spacy.matcher import PhraseMatcher, Matcher;
from spacy.tokens import Span, Doc;
from spacy.lang.en import English;
from spacy.language import Language;

#%%

with open("NeuroNames.json", "r", encoding = "utf-8") as f:
    targets_json = json.load(f);
    targets_main = [entry["standardName"] for entry in targets_json];
    targets_syn_groups = [[syn["synonymName"] for syn in entry["synonyms"]] for entry in targets_json if "synonyms" in entry]; 
    targets_syn = set();
    for group in targets_syn_groups:
        targets_syn.update({*group});
    targets_syn = list(targets_syn);
    targets = targets_main + targets_syn;

targets_pattern = list(nlp_trf.tokenizer.pipe(targets));
matcher = PhraseMatcher(nlp_trf.vocab, attr="LOWER"); # Matches based on LOWER attribute to make matches case-insensitive 
matcher.add("TARGETS", targets_pattern);

Doc.set_extension("targets", default = [], force = True); # Force true to avoid having to restart kernel every debug cycle

@Language.component("processTargets")
def processTargets(doc):
    matches = matcher(doc);
    spans = [Span(doc, start, end, label = "TARGET") for (match_id, start, end) in matches];
    doc._.targets = spans;
    print("Processing")
    #FIXME Will have to concatenate nested spans (e.g., thalamus in anterior thalamus)
    #FIXME Add another doc extension to process synonyms, using array of strings instead of spans which are harder to manipulate 
    return doc;



nlp_trf.add_pipe("processTargets");
#%%
nlp_trf.remove_pipe("processTargets");
#%% Test
doc = nlp_trf("We used 1 Hz stimulation to the Anterior Thalamus to suppress seizure activity in the patient who also had injury to his globus pallidus");

#%%
texts = importExcelData2("Data.xls");
for text in texts:
    doc = nlp_trf(text);
    print(doc._.targets);