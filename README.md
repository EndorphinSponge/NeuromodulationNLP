# NeuromodulationNLP

NLP-based tool for extracting information from literature on neuromodulation

Architecture: 
- **main_spacy.py** module is the entry point of the tool, can change the data source of abstracts within this module as indicated by the in-line commments. Can be run as-is as long as all the dependencies are installed
- **global_functions.py** module is the container for functions that are variably imported into other modules 
- 3x key NLP pipeline components for extracting **locations, parameters, and sample size** are contained within their respective modules which are run within the main_spacy.py module to incorporate these pipeline components in the SpaCy language model
- **postprocessing.py** runs after all the NLP model components to parse keyword info imported along with each abstract to embed information about stimulation modality and disease type for each abstract which can be used for visualization
- **pipeline2_visualization.py** contains a visualization object that takes the processed container of abstracts (after being processed by the NLP pipeline and postprocessing step) which is used in main_spacy.py to generate a variety of visualization of the extracted data

Folders:
- **data**: folder containing datasets and other referenced data containers 
- **figures**: folder for output of generated figures from the visualization pipeline


Datasets: 
- **Data.xls**: Raw data from Embase containing ~400 papers using the Embase search terms DBS and Focal Epilepsy
- **Embase Data.xls**: Combined data from Embase exports containing ~5500 papers using broad search terms to find all papers on neuromodulation in epilepsy
- **Neuromodulation Data.xls**: Combined data from Embase exports containing ~7300 papers using a search to obtain all clinical papers on neuromodulation as per Embase's filters

