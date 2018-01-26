import math
import random
from pytricia import PyTricia
import networkx

DEFAULT_SERVICE_TYPES = {21: 0.1, 80: 0.1, 2801: 0.2, 8444: 0.3, 8445: 0.3}


def generate_local_policies(G, **kwargs):
    # TODO
    return generate_random_policy(G, **kwargs)


def generate_random_policy(G,
                           service_types=DEFAULT_SERVICE_TYPES,
                           network_ratio=0.5,
                           prefix_ratio=0.2,
                           policy_place='transit',
                           policy_type='both',
                           **args):
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
    for prefix in G.node[25]['ip-prefixes']:
        G.node[29]['local_policy'][prefix] = {8444: 30, 8445: 30, 21: 30, 80: 30, 2801: 30}
        G.node[30]['local_policy'][prefix] = {8444: 29, 8445: 29, 21: 29, 80: 29, 2801: 29}
