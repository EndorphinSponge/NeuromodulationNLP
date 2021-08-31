# -*- coding: utf-8 -*-

from global_functions import *

#%% 

data = importExcelData3("Data.xls")

#%% Regex - OLD
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

#%% Regex - Freq & amperage

common = r"muA"

pattern_float = re.compile(r"(?P<main>\d*\.?\d*)[- ]?(?:%s)" % common);
pattern_unc = re.compile(r"(?P<main>\d*\.?\d*)(?: ?(?P<unit>%s))? ?\+/- ?(?P<unc>\d*\.?\d*)[- ]?(?(unit)|(?:%s))" % (common, common));
pattern_list = re.compile(r"(?:(\d*\.?\d*)(?:[- ]?(?:%s))?, ?)+(\d*\.?\d*)[- ]?(?:%s)" % (common, common));
pattern_sublist = re.compile(r"(\d*\.?\d+)");
pattern_range = re.compile(r"(?P<min>\d*\.?\d+) ?(?:\-|\bto\b) ?(?P<max>\d*\.?\d+)[- ]?(?:%s)" % common);
pattern_comparator = re.compile(r"(?P<comparator>[<>]\=?) ?(?P<main>\d*\.?\d*)[- ]?(?:%s)" % common);

#%% Extracting sample size from abstract

def extractSampleSize(text: str, model: "NLP model used to process text") -> "Returns int of sample size for an abstract":
    doc = processText(text, model)
    patients = []
    for chunk in doc.noun_chunks:        
        if ("patient" in str(chunk)) or ("subject" in str(chunk)): # added "subject" to arguments after discovering missing data during extraction
            patients.append(chunk)
    numbers = [0]
    for entry in patients:
        if (str(entry).lower() == "a patient") or \
            (str(entry).lower() == "the patient") or \
            (str(entry).lower() == "a subject") or \
            (str(entry).lower() == "the subject"): # these arguments have to come first, otherwise the second set of conditions will catch them before being processed by these arguments
            numbers.append(1)
        entities = entry.ents
        for word in entities:            
            if ((word.label_ == "CARDINAL") or (word.label_ == "QUANTITY")) and (word.text != ""):
                try: numbers.append(w2n.word_to_num(word.text)) #Sample data has "six6" in entry ORN 19 which can't be parsed, this is to catch similar exceptions
                except ValueError: print("Value error")
                finally: pass
    return max(numbers)

#%%

def extractParameter(text: str, units: str):
    """
        
    Parameters
    ----------
    text : str
        Text to extract from
    units : str
        The units of the parameter to use for regex filtering 

    Returns
    -------
    Dictionary of stimulation parameters separated into lists depending on their reporting format (float, range, comparator)
    """
    common = units;
    pattern_float = re.compile(r"(?P<main>\d*\.?\d*)[- ]?(?:%s)" % common);
    pattern_unc = re.compile(r"(?P<main>\d*\.?\d*)(?: ?(?P<unit>%s))? ?\+/- ?(?P<unc>\d*\.?\d*)[- ]?(?(unit)|(?:%s))" % (common, common));
    pattern_list = re.compile(r"(?:(\d*\.?\d*)(?:[- ]?(?:%s))?, ?)+(\d*\.?\d*)[- ]?(?:%s)" % (common, common));
    pattern_sublist = re.compile(r"(\d*\.?\d+)");
    pattern_range = re.compile(r"(?P<min>\d*\.?\d+) ?(?:\-|\bto\b) ?(?P<max>\d*\.?\d+)[- ]?(?:%s)" % common);
    pattern_comparator = re.compile(r"(?P<comparator>[<>]\=?) ?(?P<main>\d*\.?\d*)[- ]?(?:%s)" % common);
    
    fl = set()
    rg = []
    cp = []    
    matches_float = pattern_float.finditer(text)
    for match in matches_float:
        if (match.group("main") != "" and match.group("main") != "." and float(match.group("main")) < 1500): 
            # Screens for year, typical parameters should not exceed this magnitude (would have used different unit prefix otherwise)
            # Also removes non-valid entries, mainly for voltage parameters since its anchor is only one character (lower threshold for false-positives)
            fl.add(match.group("main"))        
    matches_unc = pattern_unc.finditer(text)
    for match in matches_unc: # Remove matched frequencies with uncertainties since they most likely represent results rather than parameters
        if match.group("unit") != None:
            fl.discard(match.group("main"))
        elif match.group("unit") == None:
            fl.discard(match.group("unc"))   
    matches_list = pattern_list.finditer(text)
    for match in matches_list:
        matches_sublist = pattern_sublist.finditer(match.group(0))
        for submatch in matches_sublist:
            fl.add(submatch.group(0))            
    matches_range = pattern_range.finditer(text)
    for match in matches_range:
        rg.append((match.group("min"), match.group("max"))) 
        fl.discard(match.group("max")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 
    matches_comparator = pattern_comparator.finditer(text)
    for match in matches_comparator:
        cp.append((match.group("comparator"), match.group("main")))
        fl.discard(match.group("main")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 
    fl = list(fl)
    return {"fl": fl, "rg": rg, "cp": cp}


#%% DataFrame generator for frequencies

st = time.time()

parameters = []
df = pd.DataFrame(columns = ["PATIENTS", "FLOAT", "RANGE", "COMPARATOR"])
index = 0
for abstract in data["AB"]: # Abstracts should be in the form of strings since the filtering process only allows strings 
    # parameter = extractParameter(abstract, r"Hz|Hertz|hertz|Hert|hert");
    # parameters.append(parameter);
    # extractParameter function expanded:
    pt = 0
    fl = set()
    rg = []
    cp = []    
    matches_float = pattern_float.finditer(abstract)
    for match in matches_float:
        if (match.group("main") != "" and match.group("main") != "." and float(match.group("main")) < 1500): 
            # Screens for year, typical parameters should not exceed this magnitude (would have used different unit prefix otherwise)
            # Also removes non-valid entries, mainly for voltage parameters since its anchor is only one character (lower threshold for false-positives)
            fl.add(match.group("main"))        
    matches_unc = pattern_unc.finditer(abstract)
    for match in matches_unc: # Remove matched frequencies with uncertainties since they most likely represent results rather than parameters
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
    pt = extractSampleSize(abstract, nlp_sm);
    fl = list(fl)
    # End of extractParameter function
    df = df.append({"PATIENTS": pt, "FLOAT": fl, "RANGE": rg, "COMPARATOR": cp}, ignore_index=True)    
    index += 1
    print(index)

ed = time.time()
print(ed - st)


        
#%% Plot

x = []
y = []
s = []

for (index, row) in df.iterrows():
    if row["FLOAT"] != []:
        for fl in row["FLOAT"]:
            x.append(float(fl))
            y.append(0)
            s.append(row["PATIENTS"]*30)
    if row["RANGE"] != []:
        for (low, high) in row["RANGE"]:
            x.append((float(low)+float(high))/2) # Takes the average of the min and max of the range 
            y.append(0)
            s.append(row["PATIENTS"]*30)
    if row["COMPARATOR"] != []:
        for (op, num) in row["COMPARATOR"]:
            x.append(float(num)) # Takes specified number in the comparator expression, will have to refine later
            y.append(0)
            s.append(row["PATIENTS"]*30)

plot = plt.scatter(x,y,s=s, alpha = 0.15) # Alpha to set transparency, otherwise points are overlapping
# plot = plt.xlim(-10,160) # Manually set axes
plot = plt.ylim(-1,1)
plot = plt.savefig("./figures/"+input("Figure title: ")+".png", bbox_inches='tight', dpi=300) # Save function has to be called before the show() function
plot = plt.show()


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

#%% Data extraction and entry V1
df = pd.DataFrame(columns = ["FLOAT", "RANGE", "COMPARATOR"])

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