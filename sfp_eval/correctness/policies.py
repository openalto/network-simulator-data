import math
import random

import networkx
from pytricia import PyTricia

DEFAULT_SERVICE_TYPES = {21: 0.1, 80: 0.1, 2801: 0.2, 8444: 0.3, 8445: 0.3}


def generate_local_policies(G, **kwargs):
    # TODO
    return generate_random_policy(G, **kwargs)


def generate_random_policy(G,
                           random_type='r',
                           service_types=DEFAULT_SERVICE_TYPES,
                           network_ratio=0.5,
                           prefix_ratio=0.2,
                           policy_place='transit',
                           policy_type='both',
                           triangle=None,
                           **kwargs):
    """
    Randomly setup black-hole or deflection policies in transit network

    Args:
        G: Topology
        service_types: supported service port distribution.
        network_ratio: how many networks is selected. default 0.5
        prefix_ratio: how many prefix is seleted. default: 0.2
        policy_place: transit, edge or both. default: 'transit'
        policy_type: blackhole, deflection or both. default: 'both'
        args: additional arguments.

    Returns:
        Topology with generated local policies.
    """
    if 'r' in random_type:
        generate_fully_random_policy(G,
                                     service_types=service_types,
                                     network_ratio=network_ratio,
                                     prefix_ratio=prefix_ratio,
                                     policy_place=policy_place,
                                     policy_type=policy_type,
                                     **kwargs)
    if 't' in random_type and triangle:
        generate_triangle_based_random_policy(G,
                                              triangle=triangle,
                                              service_types=service_types,
                                              network_ratio=network_ratio,
                                              prefix_ratio=prefix_ratio,
                                              policy_type=policy_type,
                                              **kwargs)
    if 'b' in random_type:
        generate_funny_block_policy(G,
                                    service_types=service_types,
                                    network_ratio=network_ratio,
                                    prefix_ratio=prefix_ratio,
                                    policy_type=policy_type,
                                    **kwargs)
    if 'h' in random_type and triangle:
        block_half_policy(G,
                          triangle=triangle,
                          service_types=service_types,
                          network_ratio=network_ratio,
                          prefix_ratio=prefix_ratio,
                          policy_type=policy_type,
                          **kwargs)
    return G


def block_half_policy(G,
                      triangle,
                      service_types=DEFAULT_SERVICE_TYPES,
                      network_ratio=0.5,
                      prefix_ratio=0.2,
                      policy_type='both',
                      **kwargs):
    for tr in random.sample(triangle, math.ceil(len(triangle) * float(network_ratio))):
        peer1, peer2, dests = tr
        for dest in dests:
            node_prefixes = G.node[dest]['ip-prefixes']
            for prefix in random.sample(
                    node_prefixes, math.ceil(
                        len(node_prefixes) * float(prefix_ratio))):
                peer = random.choice([peer1, peer2])
                G.node[peer]['local_policy'][prefix] = {
                    port: None for port in random.sample(service_types.keys(),
                                                         random.randint(1, 4))
                }
        # print(peer, dict(G.node[peer]['local_policy']))
    return G


def generate_funny_block_policy(G,
                                service_types=DEFAULT_SERVICE_TYPES,
                                network_ratio=0.5,
                                prefix_ratio=0.2,
                                policy_type='both',
                                **kwargs):
    magic_ratio = 3  # Magic!
    funny_ports = [p for p in range(1, 65536) if p not in DEFAULT_SERVICE_TYPES.keys()]
    # funny_ports = [21, 80, 22, 23, 24, 25, 32, 44, 98]
    edge_networks = [
        n for n in G.nodes() if G.node[n].get('type', '') == 'edge'
    ]
    transit_networks = [
        n for n in G.nodes() if G.node[n].get('type', '') == 'transit' and n != 1
    ]
    for d in random.sample(transit_networks, math.ceil(len(transit_networks) *
                                                       float(network_ratio) / magic_ratio)):
        # print(d)
        if 'local_policy' not in G.node[d]:
            G.node[d]['local_policy'] = PyTricia()
        local_policy = G.node[d]['local_policy']
        for dest in random.sample([n for n in edge_networks if n != d],
                                  math.ceil(len(edge_networks) * float(network_ratio))):
            node_prefixes = G.node[dest]['ip-prefixes']
            for prefix in random.sample(
                    node_prefixes, math.ceil(
                        len(node_prefixes) * float(prefix_ratio))):
                local_policy[prefix] = {
                    port: None
                    for port in random.sample(funny_ports,
                                              random.randint(1, 4))
                }
    return G


def generate_fully_random_policy(G,
                                 service_types=DEFAULT_SERVICE_TYPES,
                                 network_ratio=0.5,
                                 prefix_ratio=0.2,
                                 policy_place='transit',
                                 policy_type='both',
                                 **kwargs):
    edge_networks = [
        n for n in G.nodes() if G.node[n].get('type', '') == 'edge'
    ]
    transit_networks = [
        n for n in G.nodes() if G.node[n].get('type', '') == 'transit'
    ]
    if policy_place == 'transit':
        policy_networks = transit_networks
    elif policy_place == 'edge':
        policy_networks = edge_networks
    else:
        policy_networks = G.nodes()
    for d in policy_networks:
        if 'local_policy' not in G.node[d]:
            G.node[d]['local_policy'] = PyTricia()
        local_policy = G.node[d]['local_policy']
        for dest in random.sample([n for n in edge_networks if n != d],
                                  math.ceil(
                                      len(edge_networks) * float(network_ratio))):
            node_prefixes = G.node[dest]['ip-prefixes']
            for prefix in random.sample(
                    node_prefixes, math.ceil(
                        len(node_prefixes) * float(prefix_ratio))):
                local_policy[prefix] = {
                    port: gen_single_policy(G, d, dest, policy_type)
                    for port in random.sample(service_types.keys(),
                                              random.randint(1, 4))
                }
    return G


def generate_triangle_based_random_policy(G,
                                          triangle,
                                          service_types=DEFAULT_SERVICE_TYPES,
                                          network_ratio=0.5,
                                          prefix_ratio=0.2,
                                          policy_type='both',
                                          **kwargs):
    for tr in random.sample(triangle, math.ceil(len(triangle) * float(network_ratio))):
        peer1, peer2, dests = tr
        for dest in dests:
            node_prefixes = G.node[dest]['ip-prefixes']
            for prefix in random.sample(
                    node_prefixes, math.ceil(
                        len(node_prefixes) * float(prefix_ratio))):
                G.node[peer1]['local_policy'][prefix] = {
                    port: peer2 for port in random.sample(service_types.keys(),
                                                          random.randint(1, 4))
                }
                G.node[peer2]['local_policy'][prefix] = {
                    port: peer1 for port in random.sample(service_types.keys(),
                                                          random.randint(1, 4))
                }
    return G


def gen_single_policy(G, d, dest, policy_type):
    if policy_type == 'both':
        return random.choice([None, random_deflection(G, d, dest)])
    elif policy_type == 'deflection':
        return random_deflection(G, d, dest)
    return None


def random_deflection(G, d, dest):
    next_hop = networkx.shortest_path(G, d, dest)[1]
    subG = G.copy()
    subG.remove_edge(d, next_hop)
    if dest not in networkx.descendants(subG, d):
        return None
    else:
        # return networkx.shortest_path(subG, d, dest)[1]
        return random.choice([x for x in subG.neighbors(d)])


def manual_policy(G):
    # for prefix in G.node[59]['ip-prefixes']:
    #     G.node[29]['local_policy'][prefix] = {8444: 30, 8445: 30, 21: 30, 80: 30, 2801: 30}
    #     G.node[30]['local_policy'][prefix] = {8444: 29, 8445: 29, 21: 29, 80: 29, 2801: 29}
    # for prefix in (G.node[51]['ip-prefixes'] + G.node[52]['ip-prefixes'] + G.node[53]['ip-prefixes'] +
    #                G.node[54]['ip-prefixes'] + list(G.node[55]['ip-prefixes']) + list(G.node[56]['ip-prefixes'])):
    # G.node[24]['local_policy'][prefix] = {8444: 27, 8445: 27, 21: 27, 80: 27, 2801: 27}
    # G.node[24]['local_policy'][prefix] = {81: None}
    policies = {24: {'81.180.86.0/24': {21: None, 80: None}, '144.16.112.0/24': {21: None, 2801: None},
                     '193.12.15.0/24': {80: None, 21: None},
                     '193.199.48.0/23': {80: None, 2801: None, 21: None, 8445: None}},
                23: {'90.34.192.0/21': {8445: None, 2801: None, 21: None, 80: None}, '90.34.200.0/24': {21: None},
                     '90.169.98.0/24': {8445: None, 21: None, 80: None, 2801: None},
                     '90.169.160.0/21': {21: None, 8444: None, 2801: None},
                     '145.100.32.0/22': {8444: None, 2801: None, 80: None, 21: None}},
                48: {'159.93.39.0/24': {2801: None}, '194.85.66.0/24': {80: None, 8444: None, 8445: None, 21: None},
                     '194.190.165.0/24': {80: None, 21: None, 8445: None},
                     '213.135.54.0/26': {8444: None, 80: None, 21: None, 8445: None}
                     }}
    for n in policies:
        for prefix in policies[n]:
            G.node[n]['local_policy'][prefix] = policies[n][prefix]
