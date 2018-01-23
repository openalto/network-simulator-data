#!/usr/bin/env python

import numpy as np
from networkx import all_shortest_paths


def avg_multihoming(G):
    path = np.array([[len([p for p in all_shortest_paths(G, s, d)])
                      for s in G.nodes() if s != d]
                     for d in G.nodes()])
    return np.average(path.flatten())


def avg_degree(G):
    return np.average([G.degree(n) for n in G.nodes()])
