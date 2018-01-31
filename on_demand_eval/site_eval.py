#!/usr/bin/env python
import os
import sys
from multiprocessing import Pool

from on_demand_eval.eval import max_odi_test
from sfp_eval.correctness.topology import read_topo


def all_edge_neighbors(topo):
    # type: (netowrkx.Graph) -> dict[int, list[int]]
    neighbors = {}
    for node in G.nodes():
        if G.nodes[node]['type'] != 'edge':
            continue
        neighbors[node] = [i for i in G.neighbors(node)]
    return neighbors


def run_eval(arg):
    node = arg[0]
    neighbor = arg[1]
    flows_folder = arg[2]
    pipeline_folder = arg[3]
    output_folder = arg[4]

    print("%d -> %d" % (node, neighbor))

    traffic_db = os.path.join(flows_folder, 'flows-%d.json' % node)
    pipelines_db = os.path.join(pipeline_folder, 'pipeline-%d.json' % neighbor)
    max_odi_test(pipelines_db, traffic_db, par=(node, neighbor), output_folder=output_folder)
    return True


def generate_arguments(peers, flows_folder, pipeline_folder, output_folder):
    result = []
    for peer in peers:
        result.append((peer[0], peer[1], flows_folder, pipeline_folder, output_folder))
    return result


if __name__ == '__main__':
    topo_filepath = sys.argv[1]
    pipeline_folderpath = sys.argv[2]
    flows_folderpath = sys.argv[3]
    output_folder = sys.argv[4]

    G = read_topo(topo_filepath)

    edge_neighbors = all_edge_neighbors(G)

    peers = []

    for node in G.nodes():
        if G.nodes[node]["type"] != 'edge':
            continue
        neighbors = edge_neighbors[node]

        for neighbor in neighbors:
            peers.append((node, neighbor))

    args = generate_arguments(peers, flows_folderpath, pipeline_folderpath, output_folder)

    results = Pool(6).imap_unordered(run_eval, args)

    for result in results:
        print(result)
