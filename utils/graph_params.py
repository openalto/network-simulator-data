#!/usr/bin/env python

import networkx

import numpy as np

def avg_multihoming(G):
    path = np.array([[len([p for p in networkx.shortest_paths.all_shortest_paths(G, s, d)])
                      for s in G.nodes()] for d in G.nodes()])
    return np.average(path.flatten())

def avg_degree(G):
    return np.average(G.degree(G.nodes()).values())
