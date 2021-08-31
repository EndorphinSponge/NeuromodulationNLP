# NeuromodulationNLP

NLP-based tool for extracting information from literature on neuromodulation

Relevant function modules
- **global_functions.py** - contains general functions used in rest of modules
- **pipeline_freq_patnumber.py** - pipeline for extracting neuromodulation frequencies with sample size and displaying it, currently only uses "Data.xls" papers
- **pipeline_noun_chunks.py** - pipeline for extracing specified terms and displaying them, currently uses "Embase Data.xls" papers

Relevant data files/folders
- **Data.xls**: Raw data from Embase containing ~400 papers using the Embase search terms DBS and Focal Epilepsy
- **Embase Data.xls**: Combined data from Embase exports containing ~5500 papers using broad search terms to find all papers on neuromodulation in epilepsy
- **Extracted data.xlsx**: Extracted data from "Data.xls" using "pipeline_freq_patnumber.py"
- **Figures**: Folder containing output figures of the results
