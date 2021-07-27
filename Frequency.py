# -*- coding: utf-8 -*-
import re
import pandas as pd

#%% Raw data 
raw = pd.read_excel('Data.xls', skiprows=1) # remember to skip first row which contains copyright info 
raw = raw.drop_duplicates(subset='TI') # drop duplicates based on title 
raw = raw.dropna (subset = ["AB"])
raw = raw.loc[raw["AB"].str.contains("Hz")]
filtered = raw[["ORN","TI","AU","KW","AB"]]
filtered = filtered.reset_index() # to re-index dataframe so it becomes iterable again


#%% Regex

# text = "Limited data are available regarding the electrophysiology of status dystonicus (SD). We report simultaneous microelectrode recordings (MERs) from the globus pallidus internus (GPi) of a patient with SD who was treated with bilateral deep brain stimulation (DBS). Mean neuronal discharge rate was of 30.1 +/- 10.9 Hz and 38.5 Hz +/- 11.1 Hz for the right and left GPi, respectively. On the right side, neuronal electrical activity was completely abolished at the target point, whereas the mean burst index values showed a predominance of bursting and irregular activity along trajectories on both sides. Our data are in line with previous findings of pallidal irregular hypoactivity as a potential electrophysiological marker of dystonia and thus SD, but further electrophysiological studies are needed to confirm our results.Copyright © 2020, Springer-Verlag GmbH Austria, part of Springer Nature."
# text = "It is commonly assumed that interictal spikes (ISs) in focal epilepsies set off a period of inhibition that transiently reduces tissue excitability. Post-spike inhibition was described in experimental models but was never demonstrated in the human epileptic cortex. In the present study post-spike excitability was retrospectively evaluated on intracerebral stereo- electroencephalographic recordings performed in the epileptogenic cortex of five patients suffering from drug-resistant focal epilepsy secondary to Taylor-type neocortical dysplasias. Patients typically presented with highly periodic interictal spiking activity at 2.33 +/- 0.87 Hz (mean +/- SD) in the dysplastic region. During the stereo-electroencephalographic procedure, low-frequency stimulation at 1 Hz was systematically performed for diagnostic purposes to identify the epileptogenic zone. The probability of evoking an IS during the interspike period in response to 1-Hz stimuli delivered close to the ictal-onset zone was examined. Stimuli that occurred early after a spontaneous IS (within 70% of the inter-IS period) had a very low probability of generating a further IS. On the contrary, stimuli delivered during the late inter-IS period had the highest probability of evoking a further IS. The generation of stimulus-evoked ISs is occluded for several hundred milliseconds after the occurrence of a preceding spike discharge. As previously shown in animal models, these findings suggest that, during focal, periodic interictal spiking, human neocortical excitability is phasically controlled by post-spike inhibition. © Federation of European Neuroscience Societies."
# text = "red 101Hz red 13Hz red yellow 20Hz, 20 +/- 2Hz, 10Hz+/-1, 200 +/- 10Hz"
text = "something something something something 100, 200, 300Hz"

pattern = re.compile(r"(?:(\d*\.?\d*)(?:[- ]?(?:Hz|Hertz|hertz|Hert|hert))?, ?)+(\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)")

pattern_float = re.compile(r"(?P<main>\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)") # V1: Has overlap with other filters and includes non-stimulation frequencies, negative lookbehind assertion doesn't seem to work well for ruling these out, hence will need subsequent steps to merge and screen
pattern_unc = re.compile(r"(?P<main>\d*\.?\d*)(?: ?(?P<unit>Hz|Hertz|hertz|Hert|hert))? ?\+/- ?(?P<unc>\d*\.?\d*)[- ]?(?(unit)|(?:Hz|Hertz|hertz|Hert|hert))") # V2: Implemented a better pipeline so that main and uncertainty values end up in same group regardless of where unit is placed
pattern_list = re.compile(r"(?:(\d*\.?\d*)(?:[- ]?(?:Hz|Hertz|hertz|Hert|hert))?, ?)+(\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)") # V2: Will have to iterate through this to all parameters
pattern_sublist = re.compile(r"(\d*\.?\d+)") #V2: Corrected ambiguous matching 
pattern_range = re.compile(r"(?P<min>\d*\.?\d+) ?\- ?(?P<max>\d*\.?\d+)[- ]?(?:Hz|Hertz|hertz|Hert|hert)") #V2: Fixed issue where any numeric with a dash nearby was being registered as a range; asterisks on all numeric terms made entire groupings optional, hence dashes without preceding or not followed by numbers were matched
pattern_comparator = re.compile(r"(?P<comparator>[<>]\=?) ?(?P<main>\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)") #V2: Added groupings to extract comparator and frequency in isolation of each other 

# Conditions should be mutually exclusive based on processing that occurs during data extraction and entry cell 



#%% Data extraction and entry 
df = pd.DataFrame(columns = ["FLOAT", "RANGE", "COMPARATOR"])
row = 0
for abstract in filtered["AB"]: # Abstracts should be in the form of strings since the filtering process only allows strings 
    fl = set()
    rg = []
    cp = []
    
    matches_float = pattern_float.finditer(abstract)
    for match in matches_float:
        fl.add(match.group("main"))        
    matches_unc = pattern_unc.finditer(abstract)
    for match in matches_unc:
        if match.group("unit") != None:
            fl.discard(match.group("main"))
        elif match.group("unit") == None:
            fl.discard(match.group("unc"))   
    matches_list = pattern_list.finditer(abstract)
    for match in matches_list:
        matches_sublist = pattern_sublist.finditer(match.group(0))
        for submatch in matches_sublist:
            fl.add(submatch.group(0))        
    
    matches_range = pattern_range.finditer(abstract)
    for match in matches_range:
        rg.append((match.group("min"), match.group("max"))) 
        fl.discard(match.group("max")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 

    
    matches_comparator = pattern_comparator.finditer(abstract)
    for match in matches_comparator:
        cp.append((match.group("comparator"), match.group("main")))
        fl.discard(match.group("main")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 
    df = df.append({"FLOAT":fl, "RANGE":rg, "COMPARATOR":cp}, ignore_index=True)
    
    row += 1


#%% Debug
matches = pattern.finditer(text)

for match in matches:
    matches_sublist = pattern_sublist.finditer(match.group(0))
    print(match.group(0), type(match.group(0)))
    # print(match.group("main"), match.group("unc"))
    # print(f"{match.group(1)} - {match.group(2)}") # To print ranges 
    # print(match.groups())
    # print(list(matches_sublist), type(matches_sublist))

    
    for number in matches_sublist:
        print(number.group(0))
    
    
#%% Archive
# pattern_unc = re.compile(r"(?:(\d*\.?\d*)(?: ?(?:Hz|Hertz|hertz|Hert|hert))? ?\+/- ?(\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert))|(?:(\d*\.?\d*)(?: ?(?:Hz|Hertz|hertz|Hert|hert)) ?\+/- ?(\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)?)") # V1: Assumes that stimulation parameters will not have +/- uncertainty as they are set by the experimenter 
# pattern_list = re.compile(r'((\d*\.?\d*)(?:[- ]?Hz)?, ?)+(\d*\.?\d*)[- ]?Hz') # V1: MVP
# pattern_sublist = re.compile(r"(\d*\.?\d*)") #V1: Created to parse frequency parameters from list
# pattern_range = re.compile(r"(?P<min>\d*\.?\d*) ?\- ?(?P<max>\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)") #V1: No errors so far
# pattern_comparator = re.compile(r'[<>]\=? ?(\d*\.?\d*)[- ]?(?:Hz|Hertz|hertz|Hert|hert)') V1: No errors so far 