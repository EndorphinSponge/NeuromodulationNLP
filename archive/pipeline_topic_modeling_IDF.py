# -*- coding: utf-8 -*-

from global_functions import *

#%%

import string 
import glob


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.decomposition import PCA 

from nltk.corpus import stopwords


#%% Keyword identification 
st = time.time()
# data = importExcelData2("Embase Data.xls") # Imports series of abstracts
data = importExcelData2("TBIExport.xls") # Imports series of abstracts 

def cleanText(text: str) -> \
    "Returns cleaned str stripped of stopwords":
    stops = stopwords.words("english")
    words = text.split()
    cleaned = []
    for word in words: # Removes stopwords 
        if word not in stops:
            cleaned.append(word)
    cleaned = " ".join(cleaned) # Rejoins split document after removing stopwords 
    cleaned = cleaned.translate(str.maketrans("","", string.punctuation)) # Removes punctuation
    # Specific phrases to remove
    cleaned = cleaned.replace("rights reserved","")
    cleaned = cleaned.replace("et al","")
    # 
    while "  " in cleaned: # Replaces double spaces with single spaces 
        cleaned = cleaned.replace("  ", " ")        
    return cleaned

corpora = []
for abstract in data:
    if type(abstract) == str:
        corpora.append(cleanText(abstract))

vectorizer = TfidfVectorizer(
    lowercase = True,
    max_features = 100,
    max_df = 0.8,
    min_df = 5,
    ngram_range = (2,4),
    stop_words = "english") # List of parameters for a standard run, actual documentation on scikit learn 

vectors = vectorizer.fit_transform(corpora)
feature_names = vectorizer.get_feature_names()
dense = vectors.todense()
dense_list = dense.tolist()

keyword_list = []

for abstract in dense_list: # Iterates through list of abstract to get lists of keywords from each abstract
    x = 0
    keywords = []
    for word in abstract: # Iterates through abstracts and appends features to list 
        if word > 0: # Checks if word length is > 0
            keywords.append(feature_names[x])
        x += 1 
    keyword_list.append(keywords) 

# print(keyword_list)
ed = time.time()
print(ed - st)

#%% Clustering 
cluster_num = 5

model = KMeans(n_clusters = cluster_num, init = "k-means++", max_iter = 1000, n_init = 20) # Look up actual documentation on scikit 
model.fit(vectors)

order_centroids = model.cluster_centers_.argsort()[:, ::-1] # Don't forget the underscore after "centers"
terms = vectorizer.get_feature_names()

with open ("IDF Results.txt", "w", encoding = "utf-8") as file: 
    for cluster in range(cluster_num):
        file.write(f"Cluster #{cluster}")
        file.write("\n")
        for index in order_centroids[cluster, :10]:
            file.write(f"{terms[index]}")
            file.write("\n")
        file.write("\n")
        file.write("\n")

#%% Clustering display 

kmean_indices = model.fit_predict(vectors)
pca = PCA(n_components=2)
scatter_points = pca.fit_transform(vectors.toarray())
colors = ["r", "b", "c", "y", "m"]
x = [p[0] for p in scatter_points]
y = [p[1] for p in scatter_points]
fig, ax = plt.subplots(figsize=(50,50))
ax.scatter(x, y, s = 100,c=[colors[i] for i in kmean_indices])

# Can annotate each point using titles/authors or other points according to function 

# plt.savefig("IDF Scatterplot.png")
plt.savefig("IDF Scatterplot TBI.png")



