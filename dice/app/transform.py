#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import click
import json
import os
import networkx as nx
import itertools

from .utils import *



# THREE STEPS
#
#
# PRUNE_CONCEPTS >>> 
# From DSL data including concepts and pubs info, prune it using score and frequency 
#
# DSL_TO_NETWORKX >>> 
# From DSL data, create a networkX instance and prune it using min_edge_weight
#
# NETWORKX_TO_DICT >>> 
# Turn the networkx data into a dict structure that can be consumed by the dataviz
#
#


def prune_concepts(concepts_and_pubs, min_score=None, min_freq=None, verbose=True):
    """
    From a complete concepts list, ask the use for threshold values in order to prune it.
    """
    if verbose: click.secho(f"Extracting concepts data...", fg="green")

    if verbose: click.secho(f"Choose your options:", fg="green")
    
    concepts = concepts_and_pubs.drop_duplicates("concept")[['concept', 'frequency', 'score_avg']]
    print_stats_score(concepts)

    if not min_score:
        min_score = click.prompt('> Please enter a *score* threshold\n', \
                            default=concepts.score_avg.mean())

    
    # apply score threshold and continue
    concepts_and_pubs = concepts_and_pubs.query(f"score_avg >= {min_score}")
    concepts = concepts_and_pubs.drop_duplicates("concept")[['concept', 'frequency', 'score_avg']]
    print_stats_freq(concepts)

    if not min_freq:
        min_freq = click.prompt('> Please enter a *frequency* threshold\n', \
                        default=2)

    # print_parameters(min_score, min_freq, min_edge_weight)

    concepts_and_pubs = concepts_and_pubs.query(f"frequency >=  {min_freq}")
    # self.concepts_and_pubs = concepts_and_pubs.query(f"score_avg >= {min_score} & frequency >=  {min_freq}")

    return concepts_and_pubs



def dsl_to_networkx(concepts_and_pubs, min_edge_weight=None, verbose=False):
    """
    """

    if concepts_and_pubs.empty:
        print("Error - run the prune_concepts method first")
        return
    
    if verbose: click.secho(f"Generating network based on thresholds...", fg="green")

    DATA_SUBSET = concepts_and_pubs

    if not min_edge_weight:
        min_edge_weight = click.prompt('> Please enter a *co-occurrence* frequency (= edge weight) threshold', default=2)
    min_edge_weight = int(min_edge_weight)
    
    G = nx.Graph() # networkX instance

    print(f".. adding nodes.. ")
    #
    # build nodes from concepts, including score_avg and frequency
    # -- NOTE: score_bucket indicates if the concepts is above or below the mean_score
    # -- this value is used in the visualization below to color-code nodes
    #
    mean_score = DATA_SUBSET['score_avg'].mean()
    max_freq = DATA_SUBSET['frequency'].max()
    for index, row in DATA_SUBSET.drop_duplicates("concept").iterrows():
        score_bucket = 1 if row['score_avg'] > mean_score else 2
        freq_normalized = 1 + (row['frequency'] / max_freq) * 100
        # add
        G.add_node( row['concept'],
                    frequency=row['frequency'], 
                    freq_normalized=freq_normalized, 
                    score_avg=row['score_avg'], 
                    score_bucket=score_bucket)
    print("Nodes:", len(G.nodes()), "Edges:", len(G.edges()))

    #
    # build edges, based on concepts co-occurrence within pubs
    # -- calculate a 'weight' based on how often two concepts co-occur
    #
    print(f".. adding edges from pubs cooccurrence...")
    pub_ids = DATA_SUBSET.drop_duplicates("id")['id'].to_list()

    for p in pub_ids:
        concepts_for_this_pub = DATA_SUBSET[DATA_SUBSET['id'] == p]['concept'].to_list()
        for group in itertools.combinations(concepts_for_this_pub, 2):  # gen all permutations
            a, b = group[0], group[1]
            try:
                G.edges[a, b]['weight'] = G.edges[a, b]['weight'] + 1 
            except:
                G.add_edge(a, b, weight=1)
                
    print("Nodes:", len(G.nodes()), "Edges:", len(G.edges()))


    #
    # prune network 
    #

    # NEW APPROACH IDEA: for every node, only keep the top 5 (N) edges based on weight
    # so we won't have isolated nodes, and can keep things only based on score/freq

    print(f".. cleaning up edges with weight < {min_edge_weight}...")

    for a, b, w in list(G.edges(data='weight')):
        if w < min_edge_weight:
            G.remove_edge(a, b)
    print("Nodes:", len(G.nodes()), "Edges:", len(G.edges()))

    print(f".. removing isolated nodes...")

    G.remove_nodes_from(list(nx.isolates(G)))
    print("Nodes:", len(G.nodes()), "Edges:", len(G.edges()))

    network_graph =  G

    return network_graph



def networkx_to_dict(ngraph, verbose=True):
    """Turn the networkx data into a dict structure that can be consumed by the dataviz

    Note
    --------
    The network data is extracted as follows

    > xx = G.nodes(data=True)
    > for x in xx:
        print(x[1])
    ('respiratory tract infections', {'frequency': 145, 'freq_normalized': 92.77215189873418, 'score_avg': 0.63237, 'score_bucket': 2, 'size': 10})
    ('acute lung injury', {'frequency': 9, 'freq_normalized': 6.69620253164557, 'score_avg': 0.62226, 'score_bucket': 2, 'size': 10})
    .....


    > yy = G.edges(data=True)
    > for y in yy:
        print(y)
    ('respiratory tract infections', 'MERS-CoV infection', {'weight': 2})
    ('respiratory tract infections', 'lower respiratory tract infections', {'weight': 53})
    ....

    Parameters
    ----------
    ngraph : networkx.Graph
        DSL data turned into a graph

    Returns
    ----------
    tuple 
        A tuple containing two dictionaries ready to be turned into visjs JSON data sources. 
        For example

            nodes =  [
                {'id': 1, 'label': 'Knowledge Graphs'},
                {'id': 2, 'label': 'RDF'},
                {'id': "3 3", 'label': 'Linked Data'}
                ]

            edges = [
                {'from': 1, 'to': "3 3"},
                {'from': 1, 'to': 2},
                {'from': "3 3", 'to': 2}
                ]
    """


    if not ngraph:
        return [], []  # nodes, edges

    NODES = []
    if verbose: click.secho(f"Creating Dict for visjs dataviz.. ", fg="green")
    if verbose: click.secho(f"..nodes.. ", dim=True)

    def safe_id(_id):
        return _id.replace(" ", "_").strip()


    # px.colors.diverging.Temps
    TEST_COLORS = ['rgb(0, 147, 146)',
                    'rgb(57, 177, 133)',
                    'rgb(156, 203, 134)',
                    'rgb(233, 226, 156)',
                    'rgb(238, 180, 121)',
                    'rgb(232, 132, 113)',
                    'rgb(207, 89, 126)']


    for x in ngraph.nodes(data=True):
        # id and label, the same; freqn = size [TBC]
        _id, label, freq, freqn = safe_id(x[0]), x[0].capitalize(), x[1]['frequency'], x[1]['freq_normalized']
        score_avg, score_bucket = x[1]['score_avg'], x[1]['score_bucket']

        temp = {'id': _id, 'label': label, 'group': 1}
        temp['value'] = int(freqn) 
        temp['freq'] = int(freq) 
        temp.update(x[1]) # add all other features too
        # TEST COLORS hardcoded
        temp['color'] = TEST_COLORS[3*score_bucket]
        # HTML titles
        temp['title'] = f"<h4>Concept: {label}</h4><hr>Frequency Norm: {freqn}<br>Frequency: {freq}<br>Score avg: {score_avg}<br>Score bucket: {score_bucket}"
        # temp['title'] = json.dumps(x[1], sort_keys=True, indent=4)  # title = original JSON contents
        NODES.append(temp)

    EDGES = []
    if verbose: click.secho(f"..edges.. ", dim=True)

    for x in ngraph.edges(data=True):
        # id and label, the same
        temp = {'from': safe_id(x[0]), 'to': safe_id(x[1])}
        temp['value'] = int(x[2]['weight']) 
        temp.update(x[2]) # add all other features too
        temp['title'] = f"Strength: {x[2]['weight']}"

        EDGES.append(temp)

    if verbose: click.secho(f"Done")
    return NODES, EDGES











def test_run_and_save_local():
    """Save JSON files locally
    """

    # BREAKS

    # with open("testdata/nodes-test.json", 'r') as fp:
    #     nodes = json.load(fp)
    # with open("testdata/edges-test.json", 'r') as fp:
    #     edges = json.load(fp)

    df = pd.read_json("testdata/dsl_dataframe.json")

    nodes, edges = networkx_to_dict(dsl_to_networkx(prune_concepts(df, min_score=0.5, min_freq=3), min_edge_weight=3))

    import json

    json.dumps(nodes, )




# if __name__ == "__main__":
#     test_run()
    
