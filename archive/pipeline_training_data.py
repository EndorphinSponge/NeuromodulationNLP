# -*- coding: utf-8 -*-

from global_functions import *


#%%

from spacy.matcher import PhraseMatcher;
from spacy.matcher import Matcher;
from spacy.tokens import Span, DocBin;
from spacy.lang.en import English;
import random;


#%% 

nlp4 = spacy.blank("en");
texts = importExcelData2("Data.xls");

matcher = Matcher(nlp4.vocab);
pattern = [[{"IS_DIGIT": True}, {"LOWER": "hz"}]];
matcher.add("FREQUENCY", pattern);

training_data = DocBin();

counter = 1
for doc in nlp4.pipe(texts, batch_size=10):
    print(counter);
    spans = [doc[start:end] for (match_id, start, end) in matcher(doc)];
    doc.ents = [doc.char_span(span.start_char, span.end_char, label = "FREQUENCY", alignment_mode = "contract") for span in spans];
    training_data.add(doc);
    counter += 1;
    
#%%
training_data.to_disk("./data/training_data.spacy");
training_data.to_disk("./data/valid_data.spacy");

#%%



