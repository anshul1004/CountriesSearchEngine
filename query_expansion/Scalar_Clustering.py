"""
Author: Minal Bonde
"""
import json
import numpy as np
import re
from nltk.corpus import stopwords
# import pysolr

# def get_results_from_solr(query, solr):
#     results = solr.search('text: "'+query+'"', search_handler="/select", **{
#         "wt": "json",
#         # "rows": 10
#         "rows": 2
#     })
#     return results

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

def Create_Scalar_Clustering(results, Query_String ):
    Query = Query_String.split(" ")
    #with open(json_file, encoding="utf8") as file:
    #   res = json.load(file)

    #docs = results['response']['docs']
    URL_Lists = []
    Documents_terms = []
    doc_dict = {}

    # for doc in docs:
    #     URL_Lists.append(doc['url'])

    for doc_no, doc in enumerate(results):
    #     Documents_List.append(doc['content'].replace("\n", " "))
        Documents_terms.extend(doc['content'].replace("\n", " ").split(" "))
        doc_dict[doc_no] = doc['content'].replace("\n", " ").split(" ")
    # Doc_Terms = list(set(Documents_terms))
    Doc_Terms = []
    for term in Documents_terms:
        if term not in Doc_Terms:
            Doc_Terms.append(term)

    # Creating a vocabulary
    # Query = ["Olympic", "Medal"]
    Vocab_dict = {}
    AllDoc_vector = np.zeros(len(Doc_Terms))
    for i, term in enumerate(Doc_Terms):
        Vocab_dict[i] = term
    from collections import Counter
    count_dict  = Counter(Documents_terms)

    Relevant_Docs=[]
    NonRelevant_Docs=[]
    count_relevant_docs = 8
    for i, doc in doc_dict.items():
        if i < count_relevant_docs:
            Relevant_Docs.append(doc)
        else:
            NonRelevant_Docs.append(doc)

    # Vector_Relevant
    AllDoc_vector = np.zeros(len(Doc_Terms))
    Vector_Relevant = []
    for docs in Relevant_Docs:
        rel_vec = np.zeros(len(Doc_Terms))
        for term in docs:
            count = docs.count(term) 
            rel_vec[Doc_Terms.index(term)] = count
        Vector_Relevant.append(rel_vec)

    M1 = np.array(Vector_Relevant)
    M1 = M1.transpose()
    Correlation_Matrix = np.matmul(M1, M1.transpose())
    shape_M = Correlation_Matrix.shape
	
    for i in range(shape_M[0]):
        for j in range(shape_M[1]):
            if Correlation_Matrix[i][j]!=0:
                Correlation_Matrix[i][j] =  Correlation_Matrix[i][j]/( Correlation_Matrix[i][j]+ Correlation_Matrix[i][i]+ Correlation_Matrix[j][j])
    # Correlation_Matrix        

    CM = Correlation_Matrix
    indices_query = []
    for q in Query:
        indices_query.append(Doc_Terms.index(q))
    # indices_query

    for i in indices_query:
        max_cos = 0
        max_index = 0
        for j in range(shape_M[1]):
            if i==j:
                continue
            cos = np.dot(CM[i], CM[j]) / (np.sqrt(np.dot(CM[i],CM[i])) * np.sqrt(np.dot(CM[j],CM[j])))
            if np.isnan(cos):
                continue

            # print(cos)
            if cos > max_cos:
                max_cos = cos
                max_index = j
        # print(max_cos)
        Query.append(Doc_Terms[max_index])
        # print("similar term for",Doc_Terms[i], "is:",  Doc_Terms[max_index])
    return " ".join(Query)
                



def scalar_main(query, solr_results):
    # execute only if run as a script
    stop_words = set(stopwords.words('english'))
    # query = 'Michael Phelps'
    # solr = pysolr.Solr('http://localhost:8983/solr/nutch/', always_commit=True, timeout=10)
    # results = get_results_from_solr(query, solr)
    # tokens = []
    # token_counts = {}
    # tokens_map = {}
    # tokens_map = collections.OrderedDict()
    # document_ids = []

    # for result in results:
    #     document_id = result['digest']
    #     document_ids.append(document_id)
    #     tokens_this_document = tokenize_doc(result['content'], stop_words)
    #     token_counts = collections.Counter(tokens_this_document)
    #     for token in tokens_this_document:
    #         if token not in tokens_map:
    #             tokens_map[token] = {document_id: token_counts[token]}
    #         elif document_id not in tokens_map[token]:
    #             tokens_map[token][document_id] = token_counts[token]
    #         else:
    #             tokens_map[token][document_id] += token_counts[token]
    #     tokens.append(tokens_this_document)


    #json_file  = r"All_Documents.json"
    Query_String = "Olympic medal"
    Expanded_Query  = Create_Scalar_Clustering(solr_results, query)
    return Expanded_Query

		
	