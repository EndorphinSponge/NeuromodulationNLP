# -*- coding: utf-8 -*-

from global_functions import *

# Test statement

#%%

from spacy.matcher import PhraseMatcher;
from spacy.tokens import Span;
from spacy.lang.en import English;


#%% Text processing on single entry

text = "Limited data are available regarding the electrophysiology of status dystonicus (SD). We report simultaneous microelectrode recordings (MERs) from the globus pallidus internus (GPi) of a patient with SD who was treated with bilateral deep brain stimulation (DBS). Mean neuronal discharge rate was of 30.1 +/- 10.9 Hz and 38.5 Hz +/- 11.1 Hz for the right and left GPi, respectively. On the right side, neuronal electrical activity was completely abolished at the target point, whereas the mean burst index values showed a predominance of bursting and irregular activity along trajectories on both sides. Our data are in line with previous findings of pallidal irregular hypoactivity as a potential electrophysiological marker of dystonia and thus SD, but further electrophysiological studies are needed to confirm our results.Copyright © 2020, Springer-Verlag GmbH Austria, part of Springer Nature."
text2 = "You should go call the minister, tell him to make a call to the mayor, and disband his group";
doc = processText(text2, nlp2);
matcher = PhraseMatcher(nlp2.vocab);
pattern = nlp2("call");
matcher.add("test", None, pattern);
matcher.add(d)

matches = matcher(doc);
print(matches);
    
#%% Test

span = Span(doc, 11, 16, label="GPE");
nlp3 = English();
print(nlp3.pipeline);

#%%

for doc in collection:
    
