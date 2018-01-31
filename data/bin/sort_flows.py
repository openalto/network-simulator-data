#!/usr/bin/env python3
import json
import sys

import os

from sfp_eval.bin.announcement_sim import read_flows
from sfp_eval.correctness.topology import read_topo

import networkx


def class_flows_src(flows, topo):
    # type: (list[dict[str, str|int]], networkx.Graph) -> dict[int, list[dict[str, str|int]]]
    src_flows = {}
    for node in topo.nodes:
        src_flows[node] = list()
    for flow in flows:
        src_ip = flow["src_ip"]
        node = topo.ip_prefixes[src_ip]
        src_flows[node].append(flow)
    return src_flows


if __name__ == '__main__':
    flows_filepath = sys.argv[1]
    topo_filepath = sys.argv[2]
    output_folder = sys.argv[3]

    flows = read_flows(flows_filepath)
    topo = read_topo(topo_filepath)
    src_flows = class_flows_src(flows, topo)

    for i in src_flows.keys():
        json.dump(src_flows[i], open(os.path.join(output_folder, 'flows-%d.json'%i), 'w'), indent=2, sort_keys=True)
