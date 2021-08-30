# -*- coding: utf-8 -*-

from global_functions import *

#%%

from spacy.matcher import PhraseMatcher, Matcher;
from spacy.tokens import Span, Doc;
from spacy.lang.en import English;
from spacy.language import Language;

#%%

with open("data/NeuroNames.json", "r", encoding = "utf-8") as f:
    targets_json = json.load(f);
    targets_main = set([entry["standardName"] for entry in targets_json]);
    targets_syn_groups = [{syn["synonymName"] for syn in entry["synonyms"] if (syn["synonymLanguage"] == "English" or syn["synonymLanguage"] == "Latin")} for entry in targets_json if "synonyms" in entry]; # Filter to only get English and Latin names
    targets_syn_dict = {entry["standardName"]:{syn["synonymName"] for syn in entry["synonyms"] if (syn["synonymLanguage"] == "English" or syn["synonymLanguage"] == "Latin")} for entry in targets_json if "synonyms" in entry}; # Used to map synonyms to their standard names
    targets_syn = set();
    for group in targets_syn_groups:
        targets_syn.update(group); # Unpack synonym groups into targets
    targets = set.union(targets_main, targets_syn);
    # Remove extraneous entries
    targets.discard("");
    targets.discard("brain");
    targets.discard("nervous system");
    targets.discard("central nervous system");
    targets.discard("40"); # Is a synonym for area PF
    
# JSON Internal modifications:
    # "temporal cortex (rodent)" renamed to "temporal cortex" as it had temporal lobe as its synonym which was common 

targets_pattern = list(nlp_sm.tokenizer.pipe(targets));
matcher = PhraseMatcher(nlp_sm.vocab, attr="LOWER"); # Matches based on LOWER attribute to make matches case-insensitive 
matcher.add("TARGETS", targets_pattern);

Doc.set_extension("targets_spans", default = [], force = True); # Force true to avoid having to restart kernel every debug cycle
Doc.set_extension("targets_text", default = [], force = True);

@Language.component("extractTargets")
def extractTargets(doc):
    matches = matcher(doc);
    spans = [Span(doc, start, end, label = "TARGET") for (match_id, start, end) in matches];
    doc._.targets_spans = spans;
    texts = [*{*[span.text for span in spans]}];
    for i in range(len(texts)): # Replace any synonyms with their standard terms
        for standard_term in targets_syn_dict:
            if texts[i].lower() in targets_syn_dict[standard_term]: # Need lower function since span text is exported without being lowered despite being filtered without case consideration
                texts[i] = standard_term;
    texts = {*texts}; # FIXME New edits, run again
    texts.discard("");
    texts.discard("brain");
    targets.discard("nervous system");
    targets.discard("central nervous system");
    doc._.targets_text = [*texts]; # To get rid of any new duplicate terms
    print(doc._.targets_text);
    #FIXME Will have to concatenate nested spans (e.g., thalamus in anterior thalamus)
    #FIXME Add another doc extension to process synonyms, using array of strings instead of spans which are harder to manipulate 
    return doc;


nlp_sm.add_pipe("extractTargets");
