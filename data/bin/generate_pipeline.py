#!/usr/bin/env python

import sys
import json
import random

from on_demand_eval.pipeline import Action, Match, Rule, Pipeline, ACTION_TYPE, ActionEncoder
from on_demand_eval.flow_space import Match, FlowSpace, Packet

from sfp_eval.correctness.topology import read_topo
from sfp_eval.bin.announcement_sim import read_flows


def generate_full_mesh_pipeline(filename):
    G = read_topo(filename)
    pl = Pipeline()
    tbl0 = pl.tables[0]
    for src in G.ip_prefixes:
        for dst in G.ip_prefixes:
            if src == dst:
                continue
            tbl0.insert(
                Rule(priority=20, match=Match(src_ip=src, dst_ip=dst, dst_port=8444),
                     action=Action(action=ACTION_TYPE.DROP))
            )
            tbl0.insert(
                Rule(priority=10, match=Match(src_ip=src, dst_ip=dst),
                     action=Action(action=['A', 'B', 'C']))
            )

    return pl


def generate_dest_based_pipeline(filename):
    G = read_topo(filename)
    pl = Pipeline()
    tbl0 = pl.tables[0]
    for dst in G.ip_prefixes:
        for p in random.sample(range(50000, 50100), 10):
            tbl0.insert(
                Rule(priority=20, match=Match(dst_ip=dst, dst_port=p),
                     action=Action(action=ACTION_TYPE.DROP))
            )
        tbl0.insert(
            Rule(priority=10, match=Match(dst_ip=dst),
                 action=Action(action=['A', 'B', 'C']))
        )
    return pl


def generate_mesh_on_flows(topo, traffic):
    G = read_topo(topo)
    pl = Pipeline()
    tbl0 = pl.tables[0]
    flows = read_flows(traffic)
    sites = [58, 60, 61, 70, 71]

    rand100_flows = [f for f in random.sample(flows, 100)]
    pairs = set()
    for f in rand100_flows:
        src_site = G.ip_prefixes[f['src_ip']]
        dst_site = G.ip_prefixes[f['dst_ip']]
        pairs.add((src_site,dst_site))
    for src_site, dst_site in pairs:
        for src in G.node[src_site]['ip-prefixes']:
            for dst in G.node[dst_site]['ip-prefixes']:
                if src == dst:
                    continue
                tbl0.insert(
                    Rule(priority=20, match=Match(src_ip=src, dst_ip=dst, dst_port=8444),
                            action=Action(action=ACTION_TYPE.DROP))
                )
                tbl0.insert(
                    Rule(priority=10, match=Match(src_ip=src, dst_ip=dst),
                            action=Action(action=['A', 'B', 'C']))
                )

    with open(sys.argv[-2], 'w') as f:
        json.dump(rand100_flows, f, indent=2, sort_keys=True)

    return pl


if __name__ == '__main__':
    # pl = generate_full_mesh_pipeline(*sys.argv[1:-1])
    # pl = generate_mesh_on_flows(*sys.argv[1:-2])
    pl = generate_dest_based_pipeline(sys.argv[1])

    with open(sys.argv[-1], 'w') as pl_db:
        json.dump(pl.to_dict(), pl_db, cls=ActionEncoder, indent=2, sort_keys=True)
