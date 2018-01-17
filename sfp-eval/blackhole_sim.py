#!/usr/bin/env python

from random import randint, sample

import networkx

SERVICE_TYPES = 7
MAX_BLOCK_TYPES = 2

def read_topo():
    """
    Read inter-domain network topology
    """
    # TODO:
    G = networkx.Graph()
    return G

def set_random_policy(G):
    """
    Randomly setup black-hole policies in transit network
    """
    for d in G.nodes():
        if G.node[d].get('type', '') == 'transit':
            G.node[d]['block'] = [randint(0, SERVICE_TYPES)
                                  for i in range(randint(0, MAX_BLOCK_TYPES))]

def gen_random_flow(G, flow_num=2000):
    return [(sample(G.nodes(), 2), randint(0, SERVICE_TYPES)) for i in range(flow_num)]

def check_reachability(G, flows):
    paths = networkx.shortest_path(G)
    cnt = 0
    for f in flows:
        p = paths[f[0][0]][f[0][1]]
        block = False
        for d in p:
            if f[1] in G.node[d].get('block', []):
                block = True
                break
        if not block:
            cnt += 1
    print len(flows), cnt, 1 - float(cnt)/len(flows)
