"""
Author: Anshul Pardhi
"""
import json
import time
import fastcluster
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import ward, dendrogram

start_time = time.time()

# Open SOLR Index JSON file (Get your SOLR response JSON file here, file too large to upload to GitHub)
f = open('solr_index_full_data.json', encoding="ISO-8859-1")
data = json.load(f)
f.close()

document_list = []
url_list = []

# Parse text content from indexed json
for outer_index in data:
    if outer_index == "response":
        response_val = data[outer_index]
        for curr_key in response_val:
            if curr_key == "docs":
                site_info = response_val[curr_key]
                for site_dict in site_info:
                    for site_key in site_dict:
                        if site_key == "url":
                            url_list.append(site_dict[site_key])
                        if site_key == "content":
                            content = site_dict[site_key]
                            document_list.append(content)
print("Time taken for parsing JSON: ", time.time() - start_time)

# Use TF-IDF Vectorizer to vectorize document text inputs
vectorizer = TfidfVectorizer(max_df=0.6, min_df=0.1, stop_words='english', use_idf=True)
X = vectorizer.fit_transform(document_list)
print("Time taken for vectorizing inputs: ", time.time() - start_time)

# Apply flat clustering (K-means)
km = KMeans(n_clusters=11, init='k-means++', max_iter=100, n_init=1)
km.fit(X)
# print("Time taken for applying flat clustering: ", time.time() - start_time)

# Store K-means clustering results in a file
id_series = pd.Series(url_list)
cluster_series = pd.Series(km.labels_)
results = (pd.concat([id_series,cluster_series], axis=1))
results.columns = ['id', 'cluster']
results.to_csv("clustering_f.txt", sep=',', columns=['id', 'cluster'], header=False, index=False, encoding='utf-8')
print("Time taken for storing results of flat clustering: ", time.time() - start_time)

# Apply Hierarchical Clustering (Single link)
dist = 1 - cosine_similarity(X)
print("Time taken for computing cosine similarity: ", time.time() - start_time)

agg_d = fastcluster.linkage(dist, method='single', metric='euclidean')
print("Time taken for single linkage: ", time.time() - start_time)

fig, ax = plt.subplots()
ax = dendrogram(fastcluster.single(agg_d), orientation="right", labels=url_list)
print("Time taken for applying hierarchical clustering: ", time.time() - start_time)

# Get labels
for key in ax:
    if key == "ivl":
        hc_key = ax[key]
    if key == "color_list":
        hc_dict = dict([(y,x+1) for x,y in enumerate(sorted(set(ax[key])))])
        hc_value = [hc_dict[x] for x in ax[key]]
print("Time taken for getting labels: ", time.time() - start_time)

# Store hierarchical clustering results in a file
hc_cluster_series = pd.Series(hc_value)
hc_id_series = pd.Series(hc_key)
hc_results = (pd.concat([hc_id_series, hc_cluster_series], axis=1))
hc_results.columns = ['id', 'cluster']
hc_results.to_csv("clustering_h8.txt", sep=',', columns=['id', 'cluster'], header=False, index=False, encoding='utf-8')

print("Time taken for storing results of hierarchical clustering: ", time.time() - start_time)