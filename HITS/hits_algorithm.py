"""
Author: Ruchi Singh
"""
import networkx as nx
import json
from collections import OrderedDict

G = nx.Graph()

hub_score_file = open("HITS/precomputed_scores/hubs_score_1", 'w')
authority_score_file = open("HITS/precomputed_scores/authority_score_1", 'w')


def networkx_algo(outlinks_webgraph):
    G = nx.Graph()
    g_list = list()
    for key in outlinks_webgraph:
        values = outlinks_webgraph[key]
        for i in values:
            tuple_edge = (key,i)
            g_list.append(tuple_edge)
    G.add_edges_from(g_list)
    hubs, authorities = nx.hits(G, max_iter=1000, normalized=True)


    # hubs_urls = sorted(hubs, key=hubs.get, reverse=True)
    # print(hubs_urls)
    #
    # authorities_urls = sorted(authorities, key=authorities.get, reverse=True)
    # print(authorities_urls)

    json_dict_authority = json.dumps(authorities)
    authority_score_file.write(json_dict_authority)
    authority_score_file.close()

    json_dict_hubs = json.dumps(hubs)
    hub_score_file.write(json_dict_hubs)
    hub_score_file.close()

    # print("Hub Scores: ", hubs)
    # print("Authority Scores: ", authorities)

def get_webgraph_inlinks():
    inlinks_file = open("crawldb/inlinks_webgraph", 'r').readlines()

    webgraph_inlink = dict()
    d_value = []

    for line in inlinks_file:
        if line != "" and line != "\n":
            if "Inlinks" in line:
                link_url = line.split("\t")
                d_key = link_url[0]
            elif "fromUrl" in line:
                l = line.split(" ")
                d_value.append(l[2])
        else:
            webgraph_inlink[d_key] = d_value
            d_value = []
    return webgraph_inlink


def get_webgraph_outlinks(inlink_webgraph):
    webgraph_outlink = dict()

    for key in inlink_webgraph:
        values = inlink_webgraph[key]
        for i in values:
            if i not in webgraph_outlink:
                webgraph_outlink[i] = []
                webgraph_outlink[i].append(key)
            else:
                webgraph_outlink[i].append(key)
    return webgraph_outlink


if __name__=="__main__":
    inlinks = get_webgraph_inlinks()
    outlinks = get_webgraph_outlinks(inlinks)
    networkx_algo(outlinks)






