import networkx as nx
import pandas as pd
import numpy as np
import os
import pickle

GPLUS_EGO_USERS = [100518419853963396365]

# Store all ego graphs in pickle files as (adj, features) tuples
for ego_user in GPLUS_EGO_USERS:
    edges_dir = './ego_gplus/' + str(ego_user) + '.edges'
    feats_dir = './ego_gplus/' + str(ego_user) + '.feat'
    
    # Read edge-list
    #f = open(edges_dir)
    with open(edges_dir, 'rb')as f:
        g = nx.read_edgelist(f, nodetype=int, encoding='latin1')


    # Add ego user (directly connected to all other nodes)
    g.add_node(ego_user)
    for node in g.nodes():
        if node != ego_user:
            g.add_edge(ego_user, node)

    # read features into dataframe
    df = pd.read_table(feats_dir, sep=' ', header=None, index_col=0)

    # Add features from dataframe to networkx nodes
    for node_index, features_series in df.iterrows():
        # Haven't yet seen node (not in edgelist) --> add it now
        if not g.has_node(node_index):
            g.add_node(node_index)
            g.add_edge(node_index, ego_user)

        g.node[node_index]['features'] = features_series.as_matrix()

    assert nx.is_connected(g)
    
    # Get adjacency matrix in sparse format (sorted by g.nodes())
    adj = nx.adjacency_matrix(g) 

    # Get features matrix (also sorted by g.nodes())
    features = np.zeros((df.shape[0], df.shape[1])) # num nodes, num features
    for i, node in enumerate(g.nodes()):
        features[i,:] = g.node[node]['features']

    # Save adj, features in pickle file
    network_tuple = (adj, features)
    with open("ego_gplus/{0}-adj-feat.pkl".format(ego_user), "wb") as f:
        pickle.dump(network_tuple, f)