#!/usr/bin/env python
from sfp_eval.correctness.flow import read_flows
from sfp_eval.correctness.policies import generate_local_policies
from sfp_eval.correctness.topology import (ASRelationsReader, dump_topo,
                                           read_topo)


def session_start(topo_filepath,
                  flow_filepath,
                  relations_filepath,
                  policy_type='1'):
    G = read_topo(topo_filepath)
    #F = read_flows(flow_filepath)
    relations_reader = ASRelationsReader(relations_filepath)
    G = relations_reader.augment_to_topology(G)

    dump_topo(G, "result.yaml")

    # for node in G.nodes:
    #     print("node_id: %d, peers: %s, providers: %s, customers: %s" %
    #           (node, G.nodes[node]["peers"], G.nodes[node]["providers"], G.nodes[node]["customers"]))
    #local_policies = generate_local_policies(G)
