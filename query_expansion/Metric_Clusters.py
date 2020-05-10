"""
Author: Minal Bonde
"""
import re
import collections
import heapq
import json

import numpy as np
from nltk.corpus import stopwords
from nltk import PorterStemmer
#import pysolr
import pprint

'''

TODO: maybe check for ordered dict and ordered set
TODO: check for results 
TODO: add the words to the original query

'''

class Element:

    def __init__(self, u, v, value):
        self.u = u
        self.v = v
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, obj):
        """self <= obj."""
        return self.value <= obj.value

    def __eq__(self, obj):
        """self == obj."""
        if not isinstance(obj, Element):
            return False
        return self.value == obj.value

    def __ne__(self, obj):
        """self != obj."""
        if not isinstance(obj, Element):
            return True
        return self.value != obj.value

    def __gt__(self, obj):
        """self > obj."""
        return self.value > obj.value

    def __ge__(self, obj):
        """self >= obj."""
        return self.value >= obj.value

    def __repr__(self):
        return '<Element(u="{}", v="{}", value=("{}"))>'.format(self.u, self.v, self.value)

def get_results_from_solr(query, solr):
    results = solr.search('text: "'+query+'"', search_handler="/select", **{
        "wt": "json",
        # "rows": 10
        "rows": 50
    })
    return results

# returns a list of tokens
def tokenize_doc(doc_text, stop_words):
    # doc_text = doc_text.replace('\n', ' ')
    # doc_text = " ".join(re.findall('[a-zA-Z]+', doc_text))
    # tokens = doc_text.split(' ')
    tokens = []
    text = doc_text
    text = re.sub(r'[\n]', ' ', text)
    text = re.sub(r'[,-]', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub('[0-9]', '', text)
    text = text.lower()
    tkns = text.split(' ')
    tokens = [token for token in tkns if token not in stop_words and token != '' and not token.isnumeric()]
    return tokens

# returns a dict containing int as key (token) and dict as value
# the value of the above is a dict containing int key (doc_ids) and int value (term frequency)
# tokens_map[token] = {doc_id1: tf1, doc_id2: tf2, ...}
def get_token_map(docs_list, stop_words):
    pass

# returns a dict, with key as string (stem), value as set containing strings (words)
def make_stem_map(tokens):
    porter_stemmer = PorterStemmer()
    stem_map = {}
    for tokens_this_document in tokens:
        for token in tokens_this_document:
            stem = porter_stemmer.stem(token)
            if stem not in stem_map:
                stem_map[stem] = set()
            stem_map[stem].add(token)
    return stem_map

def print_top_n(normalized_matrix, stems, query, tokens_map, stem_map, top_n=3):
    query = query.lower()
    strings = set()
    for string in query.split(' '):
        strings.add(string)
    elements = np.zeros((len(strings), top_n)).tolist()
    index = 0
    queue = []
    for string in strings:
        queue = []
        i = -1
        porter_stemmer = PorterStemmer()

        if porter_stemmer.stem(string) in stems:
            i = list(stems).index(porter_stemmer.stem(string))

        if i==-1:
            #print('continuing')
            continue

        for j in range(len(normalized_matrix[i])):
            if normalized_matrix[i][j] == 0 \
                or (normalized_matrix[i][j].u in strings and normalized_matrix[i][j].u != string) \
                or (normalized_matrix[i][j].v in strings and normalized_matrix[i][j].v != string):
                #print('continuing 2')
                continue

            if normalized_matrix[i][j].v in tokens_map:
                heapq.heappush(queue, normalized_matrix[i][j])

            else:
                heapq.heappush(queue, \
                    Element(normalized_matrix[i][j].u, \
                        next(iter( stem_map[ normalized_matrix[i][j].v ] )), \
                        normalized_matrix[i][j].value))

            if len(queue) > top_n:
                heapq.heappop(queue)

        for k in range(top_n):
            # for k in range(top_n):
            elements[index][k] = heapq.heappop(queue)
        index+=1
        #print('index', index)

    return elements

def get_metric_clusters(tokens_map, stem_map, query):
    # matrix = [[]]
    # matrix is a 2-d array (square matrix) of size (len(stem_map.keys())) or len(stem_map)
    matrix = np.zeros((len(stem_map), len(stem_map))).tolist()
    stems = stem_map.keys()
    for i, stem_i in enumerate(stems):
        for j, stem_j in enumerate(stems):
            if i==j:
                continue
            
            cuv = 0.0
            i_strings = stem_map[stem_i]
            j_strings = stem_map[stem_j]

            for string1 in i_strings:
                for string2 in j_strings:
                    i_map = tokens_map[string1]
                    j_map = tokens_map[string2]
                    for document_id in i_map:
                        if document_id in j_map:
                            if i_map[document_id] - j_map[document_id] != 0:
                                cuv += 1 / abs( i_map[document_id] - j_map[document_id] )

            matrix[i][j] = Element(stem_i, stem_j, cuv)

    normalized_matrix = np.zeros((len(stem_map), len(stem_map))).tolist()

    for i, stem_i in enumerate(stems):
        for j, stem_j in enumerate(stems):
            if i==j:
                continue

            cuv = 0.0
            if matrix[i][j] != 0:
                cuv = matrix[i][j].value / ( len(stem_map[stem_i]) * len(stem_map[stem_j]) )

            normalized_matrix[i][j] = Element(stem_i, stem_j, cuv)

    # print(normalized_matrix.shape())
    # pprint.pprint(normalized_matrix)
    return print_top_n(normalized_matrix, stems, query, tokens_map, stem_map, top_n=3)
    # pass

def metric_cluster_main(query, solr_results):
    stop_words = set(stopwords.words('english'))
    # query = 'olympic medal'
    # path = 
#    solr = pysolr.Solr('http://localhost:8983/solr/nutch/', always_commit=True, timeout=10)
#    results = get_results_from_solr(query, solr)
#     with open('C:/Users/minal/.spyder-py3/All_Documents.json',encoding="utf8") as file:
#         results = json.load(file)
    #results = solr_results['response']['docs']
    tokens = []
    token_counts = {}
    tokens_map = {}
    # tokens_map = collections.OrderedDict()
    document_ids = []

    for result in solr_results:
        
        document_id = result['digest']
        document_ids.append(document_id)
        tokens_this_document = tokenize_doc(result['content'], stop_words)
        token_counts = collections.Counter(tokens_this_document)
        for token in tokens_this_document:
            if token not in tokens_map:
                tokens_map[token] = {document_id: token_counts[token]}
            elif document_id not in tokens_map[token]:
                tokens_map[token][document_id] = token_counts[token]
            else:
                tokens_map[token][document_id] += token_counts[token]
        tokens.append(tokens_this_document)

    stem_map = make_stem_map(tokens)

    metric_clusters = get_metric_clusters(tokens_map, stem_map, query)
    metric_clusters2 = [elem for cluster in metric_clusters for elem in cluster]
    metric_clusters2.sort(key=lambda x:x.value,reverse=True)
    i=0;
    while(i<3):
        query += ' '+ str(metric_clusters2[i].v)
        i+=1
        
    return query
    #pprint.pprint(list1)