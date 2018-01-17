#!/usr/bin/env python
"""
Simulation for the correctness of BGP announcement in fine-grained networks.
"""

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

def set_random_block_policy(G):
    """
    Randomly setup black-hole policies in transit network
    """
    for d in G.nodes():
        if G.node[d].get('type', '') == 'transit':
            G.node[d]['block'] = [randint(0, SERVICE_TYPES)
                                  for i in range(randint(0, MAX_BLOCK_TYPES))]

def set_random_policy(G):
    """
    Randomly setup black-hole or deflection policies in transit network
    """
    edge_networks = [n for n in G.nodes() if G.node[n].get('type', '') == 'edge']
    transit_networks = [n for n in G.nodes() if G.node[n].get('type', '') == 'transit']
    for d in transit_networks:
        G.node[d]['policy'] = {randint(0, SERVICE_TYPES):
                               {dest: sample([None, random_deflection(G, d, dest)], 1)
                                for dest in sample(edge_networks,
                                                   randint(0, len(edge_networks)))}
                               for i in sample(range(MAX_BLOCK_TYPES),
                                               randint(0, MAX_BLOCK_TYPES))}

def random_deflection(G, d, dest):
    next_hop = networkx.shortest_path(G, d, dest)[1]
    subG = G.copy()
    subG.remove_edge(d, next_hop)
    if dest not in networkx.descendants(subG, d):
        return None
    else:
        return networkx.shortest_path(subG, d, dest)[1]

def gen_random_flow(G, flow_num=2000):
    return [(sample(G.nodes(), 2), randint(0, SERVICE_TYPES)) for i in range(flow_num)]

def check_reachability(G, flows):
    paths = networkx.shortest_path(G)
    drop_cnt = 0
    loop_cnt = 0
    for f in flows:
        result = check_path(f, paths, G)
        if result == 1:
            drop_cnt += 1
        elif result == 2:
            loop_cnt += 1
        # block = False
        # for d in p:
        #     if f[1] in G.node[d].get('block', []):
        #         block = True
        #         break
        # if not block:
        #     cnt += 1
    print len(flows), drop_cnt, loop_cnt, 1 - float(drop_cnt + loop_cnt)/len(flows)

def check_path(f, paths, G):
    loop_remover = {}
    pair = f[0]
    src = pair[0]
    dst = pair[1]
    srv = f[1]
    p = paths[src][dst]
    d = p.pop(0)
    while not p:
        loop_remover[d] = loop_remover.get(d, 0) + 1
        if loop_remover[d] > 1:
            return 2
        policy = G.node[d].get('policy', {})
        if srv in policy:
            if dst in policy[srv]:
                d = policy[srv][dst]
                if d:
                    p = paths[d][dst][1:]
                else:
                    p = []
            else:
                d = p.pop(0)
    if d != dst:
        return 1
    return 0

if __name__ == '__main__':
    G = read_topo()
    set_random_policy(G)
    flows = gen_random_flow(G)
    check_reachability(G, flows)
