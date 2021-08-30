# -*- coding: utf-8 -*-

from global_functions import *


#%%

from spacy.matcher import PhraseMatcher;
from spacy.tokens import Span;
from spacy.lang.en import English;
import networkx as nx;
from pyvis.network import Network;

#%% Pyvis - Screening by node size

edges = Counter();
nodes_modalities = Counter();
nodes_locations = Counter();
nodes_diseases = Counter();
# nodes_parameters = Counter();
for (doc, context) in docs:
    node_list = set();
    # Modality
    for modality in doc._.modality:
        modality = modality.lower().strip();
        nodes_modalities[modality] += 1;
        node_list.add(modality);
    
    # Location 
    for location in doc._.targets_text:
        location = location.lower().strip();
        nodes_locations[location] += 1;
        node_list.add(location);
    # Diseases - narrow
    for disease in doc._.disease_narrow:
        disease = disease.lower().strip();
        nodes_diseases[disease] += 1;
        node_list.add(disease);
    
    # Parameters
    
    node_list = [*node_list];
    for (i, node_start) in enumerate(node_list):
        for (j, node_end) in enumerate(node_list[i+1:]):
            edges[(node_start, node_end)] += 1;
            edges[(node_end, node_start)] += 1;

net = Network();

for modality in nodes_modalities:
    net.add_node(modality, color = "red", size = math.log(nodes_modalities[modality], 2), mass = math.log(nodes_modalities[modality], 2)); # Need to scale down in order to match sizes of locations
    
for location in nodes_locations:
    if nodes_locations[location] >= 10: # Only add the node if there is 10 or more hits 
        net.add_node(location, color = "green", size = math.log(nodes_locations[location], 2), mass = math.log(nodes_modalities[modality], 2));
        
for disease in nodes_diseases:
    if nodes_diseases[disease] >= 10: # Only add the node if there is 10 or more hits 
        net.add_node(disease, color = "blue", size = math.log(nodes_diseases[disease], 2), mass = math.log(nodes_modalities[modality], 2));
    
for (node1, node2) in edges:
    if (nodes_locations[node1] >= 10 or nodes_modalities[node1] >= 10 or nodes_diseases[node1] >= 10) \
        and (nodes_locations[node2] >= 10 or nodes_modalities[node2] >= 10 or nodes_diseases[node2] >= 10):
        # Need to check nodes in both sets of counters
        net.add_edge(node1, node2, width = math.log(edges[(node1, node2)],4)); # Width needs to be scaled

net.toggle_physics(True);
net.force_atlas_2based(damping = 1, gravity = -20, central_gravity = 0.05, spring_length = 65);
net.show_buttons(filter_=['physics']);
net.show("Network.html");
