# NeuromodulationNLP

NLP-based tool for extracting information from literature on neuromodulation

Architecture: 
- **global_functions.py** module is the container for functions that are variably imported into other modules 
- 3x key pipeline components for extracting **locations, parameters, and sample size** are contained within their respective modules which must be run first to incorporate these pipeline components in the SpaCy language model
- **pipeline2_keywords_terms.py** is the last component to be run which parses the given corpus along with their context, can only be run after the 3x key components are added to the language model 
- **pipeline2_visualization.py** contains a series of code blocks for visualization of data extracted using the constructed pipeline, should be run last after all other components are run


Folders:
- **data**: folder containing datasets and other referenced data containers 
- **figures**: folder for output of generated figures from the visualization pipeline


Datasets: 
- **Data.xls**: Raw data from Embase containing ~400 papers using the Embase search terms DBS and Focal Epilepsy
- **Embase Data.xls**: Combined data from Embase exports containing ~5500 papers using broad search terms to find all papers on neuromodulation in epilepsy
- **Neuromodulation Data.xls**: Combined data from Embase exports containing ~7300 papers using a search to obtain all clinical papers on neuromodulation as per Embase's filters

