# -*- coding: utf-8 -*-

from global_functions import *

#%%

from spacy.matcher import PhraseMatcher, Matcher;
from spacy.tokens import Span, Doc;
from spacy.lang.en import English;
from spacy.language import Language;

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
        if (match.group("main") not in ["", ".", " ", " .", ". "] and float(match.group("main")) < 1500): 
            # Screens for year, typical parameters should not exceed this magnitude (would have used different unit prefix otherwise)
            # Also removes non-valid entries, mainly for voltage parameters since its anchor is only one character (lower threshold for false-positives)
            fl.add(match.group("main"));
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
            if submatch.group(0) not in ["", ".", " ", " .", ". "]:
                fl.add(submatch.group(0))            
    matches_range = pattern_range.finditer(text)
    for match in matches_range:
        if match.group("min") not in ["", ".", " ", " .", ". "] and match.group("max") not in ["", ".", " ", " .", ". "]:
            rg.append((match.group("min"), match.group("max"))) 
            fl.discard(match.group("max")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 
    matches_comparator = pattern_comparator.finditer(text)
    for match in matches_comparator:
        if match.group("comparator") not in ["", ".", " ", " .", ". "] and match.group("main") not in ["", ".", " ", " .", ". "]:
            cp.append((match.group("comparator"), match.group("main")))
            fl.discard(match.group("main")) # Discard method here to remove same entries from FLOAT column to make columns mutually exclusive 
    fl = list(fl)
    return {"fl": fl, "rg": rg, "cp": cp}

# Component
Doc.set_extension("frequency", default = None, force = True); # Force true to avoid having to restart kernel every debug cycle
Doc.set_extension("voltage", default = None, force = True);
Doc.set_extension("amperage", default = None, force = True);


@Language.component("extractParameters")
def extractParameters(doc):
    # Frequency parsing - Only in range of Hz, mHz and kHz units not found, probably not within physiological range
    # doc._.frequency = extractParameter(doc.text, r"Hz|Hertz|hertz|Hert|hert");
    doc._.frequency = extractParameter(doc.text, r"Hz\b|Hertz\b|hertz\b|Hert\b|hert\b"); # Word boundary delimiters are safer but more false positives
    # Voltage parsing - Only in range of V, mV and kV units not found    
    doc._.voltage = extractParameter(doc.text, r"V\b");    
    # Amperage parsing - Found in ranges of mA and muA, will parse separately and converge numbers to mA since it is more common
    # dict_mA = extractParameter(doc.text, r"mA");
    # dict_muA = extractParameter(doc.text, r"muA");
    dict_mA = extractParameter(doc.text, r"mA\b"); # Word boundary delimiters are safer but more false positives
    dict_muA = extractParameter(doc.text, r"muA\b");
    if dict_muA["fl"] != []:
        for fl in dict_muA["fl"]:
            dict_mA["fl"].append(float(fl)/1000);
    if dict_muA["rg"] != []:
        for (low, high) in dict_muA["rg"]:
            dict_mA["rg"].append((float(low)/1000, float(high)/1000)); 
    if dict_muA["cp"] != []:
        for (op, num) in dict_muA["cp"]:
            dict_mA["cp"].append((op, float(num)/1000));
    doc._.amperage = dict_mA;
    print("Freq:", doc._.frequency, "Voltage:", doc._.voltage, "Amperage", doc._.amperage);
    return doc;


nlp_sm.add_pipe("extractParameters");
#%%
# nlp_sm.remove_pipe("extractParameters"); # Run optionally to disable pipe 

#%%

doc = nlp_sm("Thalamus is a location. Lobules 4-5 is also a location");
print(doc._.targets_text);