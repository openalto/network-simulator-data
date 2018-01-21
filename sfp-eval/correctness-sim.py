#!/usr/bin/env python

import math
import sys
from ipaddress import ip_address, ip_network

import pytricia
import yaml

import networkx

ip_prefixes = pytricia.PyTricia()


def read_topo(filename, local_policy=None):
    data = yaml.load(open(filename))
    G = networkx.Graph()
    nodes = data["nodes"]
    links = data["links"]
    for n in nodes:
        nid = nodes[n]['id']
        G.add_node(nid, name=n, **nodes[n])
        G.node[nid]['type'] = nodes[n]['type']
        G.node[nid]['ip-prefix'] = nodes[n]['ip-prefix']
        G.node[nid]['routing'] = pytricia.PyTricia()
        G.node[nid]['fine_grained'] = pytricia.PyTricia()
        for prefix in nodes[n]['ip-prefix']:
            ip_prefixes[prefix] = nid
    for l in links:
        G.add_edge(*l)
    return G


bgp_general_policy = networkx.shortest_path


def generate_local_policy(G, **args):
    """
    Generate the local policy for each node in G.

    Args:
        G: graph.
        args: additional arguments to config the generation algorithm.

    Returns:
        The mapping from node id to a local_policy table.
        local_policy_table ::= Trie<prefix, Map<port, next_hop>>
    """
    pass


def local_policy(node):
    """
    local_policy is not a simple prefix based routing.

    For simplicity, assume the format of local_policy for each node is:

    local_policy ::= Trie<prefix, Map<port, next_hop>>
    """
    policies = pytricia.PyTricia()
    # TODO
    return policies


def default_routing_policy(node, dst_ip, dst_port=None, src_ip=None, src_port=None, protocol='tcp', **args):
    """
    Default routing policy for networks.

    Args:
        node: node id for the network.
        dst_ip: destination ip address.
        dst_port: optional.
        src_ip: optional.
        src_port: optional.
        protocol: optional.
        args: additional flow spec.

    Returns:
        The next hop of the give flow spec from this node.
    """
    local_policy = node['local_policy']
    if dst_ip in local_policy:
        local_policy_for_ip = local_policy[dst_ip]
        if dst_port in local_policy_for_ip:
            return local_policy_for_ip[dst_port]
    fg_routing = node['fine_grained']
    if dst_ip in fg_routing:
        fg_routing_for_ip = fg_routing[dst_ip]
        if dst_port in fg_routing_for_ip:
            return fg_routing_for_ip[dst_port]
    if dst_ip in node['routing']:
        return node['routing'][dst_ip]


def fp_bgp_convergence(G):
    """
    False-positive BGP Convergence. node["routing"] is the table of  {ip-prefix -> next hop node}
    """
    paths = bgp_general_policy(G)
    for src in G.node:
        for dst in G.node:
            if src != dst:
                path = paths[src][dst]
                prefixes = G.node[dst]['ip-prefix']
                for hop, next_hop in zip(path[:-1], path[1:]):
                    for prefix in prefixes:
                        hop["routing"][prefix] = next_hop


def all_fg_nodes(G, prefix):
    """
    Let's assume the local_policy is generated from the prefixes of nodes first.
    """
    # FIXME: If the granularity of prefixes in local_policy is different from ones in node, it will conduct error.
    fg_nodes = []
    for node in G.nodes:
        local = local_policy(node)
        if local.get(prefix):
            fg_nodes.append(node)
    return fg_nodes


def correct_bgp_convergence(G):
    """
    Correct BGP Convergence
    """
    for dst in G.nodes:
        prefixes = dst['ip-prefix']
        for prefix in prefixes:
            H = G.copy()
            for node in all_fg_nodes(G, prefix):
                H.remove_node(node)
            paths = networkx.shortest_path(H)
            for src in H.nodes:
                if src != dst:
                    path = paths[src][dst]
                    for hop, next_hop in zip(path[:-1], path[1:]):
                        hop["routing"][prefix] = next_hop


def find_fine_grained_routes(G, prefix_port):
    for prefix in prefix_port.keys():
        ports = prefix_port[prefix]
        for port in ports:
            H = G.copy()
            for node in H.nodes:
                action = local_policy(node)[prefix][port]
                if action is None:
                    H.remove_node(node)
                else:
                    for neig in H.neighbors(node):
                        if action != neig:
                            H.remove_edge(node, neig)
            paths = networkx.shortest_path(H)
            for src in H.nodes:
                dst = H.node[ip_prefixes[prefix]]
                if src != dst:
                    path = paths[src][dst]
                    for hop, next_hop in zip(path[:-1], path[1:]):
                        if prefix not in hop["fine_grained"]:
                            hop["fine_grained"][prefix] = dict()
                        hop["fine_grained"][prefix][port] = next_hop
    paths = networkx.shortest_path(G)
    for src in G.node:
        for dst in G.node:
            if src != dst:
                path = paths[src][dst]
                prefixes = G.node[dst]['ip-prefix']
                for hop, next_hop in zip(path[:-1], path[1:]):
                    for prefix in prefixes:
                        hop["routing"][prefix] = next_hop


def fine_grained_announcement(G):
    G = G.to_directed()
    prefix_port = dict{}
    for node in G.nodes:
        local = local_policy(node)
        for prefix in local:
            ports_actions = local[prefix]
            if prefix not in prefix_port:
                prefix_port[prefix] = set()
            for port in ports_actions:
                prefix_port[prefix].add(port)
    find_fine_grained_routes(G, prefix_port)


def read_flows(filename):
    # [{
    #     "src-ip": "10.0.0.1",
    #     "src-port": 22,
    #     "dst-ip": "10.0.10.1",
    #     "dst-port": 80,
    #     "protocol": "http"
    # }]
    data = yaml.load(open(filename))
    return data


def coarse_grained_correct_bgp(G, F):
    """
    The principle of Correct BGP is very simple:

    For a specific IP p, compute the subgraph G' of G in which every node with local_policy covering p will not show.
    The final path of p is the shortest_path of subgraph G'.

    The Correct BGP MUST guarantee the local_policy NEVER be triggered.
    """
    for flow in F:
        node = G.node[ip_prefixes[flow["src-ip"]]]
        while node is not None:
            bgp = bgp_policy(node=node, src_ip=flow["src-ip"], dst_ip=flow["dst-ip"],
                             src_port=flow["src-port"], dst_port=flow["dst-port"])
            local = local_policy(node=node, src_ip=flow["src-ip"], dst_ip=flow["dst-ip"],
                                 src_port=flow["src-port"], dst_port=flow["dst-port"])
            if bgp == local and bgp is not None:
                node["routing"][]

# def match(ip, prefix):
#     return ip in prefix


# TODO: No need, merge it with routing_policy
# def compute_next_hop(flow, rib):
#     """
#     Compute the next hop of the flow from  RIB.
#
#     Args:
#         flow: flow spec.
#         rib: the RIB table from the Graph node.
#
#     Returns:
#         the next hop. (None if no route.)
#     """
#     for rule in rib:
#         if match(flow['dst-ip'], rule):
#             return rib[rule]
#     return None


def check_path(flow, G, routing_policy=bgp_policy):
    """
    Check the path of a given flow in the topology.

    Args:
        flow: The flow spec to check.
        G: The topology object.

    Returns:
        the AS-PATH length of the route.
        nan - no route
        inf - there is a loop
    """
    loop_remover = {}
    src = ip_prefixes[flow['src_ip']]
    dst = ip_prefixes[flow['dst_ip']]
    d = routing_policy(G.node[src], **flow)
    path_len = 1
    while d:
        loop_remover[d] = loop_remover.get(d, 0) + 1
        # print d, p, loop_remover
        if loop_remover[d] > 1:
            return math.inf
        d = routing_policy(G.node[d], **flow)
        path_len += 1
    if d != dst:
        return math.nan
    return path_len


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("%s topo-filename flow-filename mode" % sys.argv[0])
    topo_filename = sys.argv[1]
    flow_filename = sys.argv[2]
    mode = sys.argv[3]
    if mode == '1':
        mode = 1  # Coarse-grained correct BGP
    elif mode == '2':
        mode = 2  # Coarse-grained BGP with false-positive
    else:
        mode = 3  # fine-grained announcement

    G = read_topo(topo_filename)
    F = read_flows(flow_filename)
