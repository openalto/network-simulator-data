#!/usr/bin/env python

from networkx.shortest_paths import all_shortest_paths

import numpy as np

def avg_multihoming(G):
    path = np.array([[len([p for p in all_shortest_paths(G, s, d)])
                      for s in G.nodes() if s != d]
                     for d in G.nodes()])
    return np.average(path.flatten())

def avg_degree(G):
    return np.average([G.degree(n) for n in G.nodes()])
