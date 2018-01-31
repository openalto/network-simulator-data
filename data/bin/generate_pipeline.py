#!/usr/bin/env python

from on_demand_eval.pipeline import Action, Match, Rule, Pipeline, ACTION_TYPE, ActionEncoder
from on_demand_eval.flow_space import Match, FlowSpace, Packet

from sfp_eval.correctness.topology import read_topo


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


if __name__ == '__main__':
    import sys
    pl = generate_full_mesh_pipeline(sys.argv[1])

    with open(sys.argv[2], 'w') as pl_db:
        import json
        json.dump(pl.to_dict(), pl_db, cls=ActionEncoder)
