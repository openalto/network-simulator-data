#!/usr/bin/env python{}{}
# from sfp_eval.correctness.flow import read_flows
from sfp_eval.bin.announcement_sim import read_flows
# from sfp_eval.correctness.policies import generate_local_policies
from sfp_eval.correctness.topology import read_topo, dump_topo, ASRelationsReader
from sfp_eval.correctness.advertise import initiate_ribs, common_advertise
from sfp_eval.correctness.route import check_reachability


def session_start(topo_filepath,
                  flow_filepath,
                  # relationship_filepath = "~/Downloads/20180101.as-rel2.txt",
                  algorithm_type='1',
                  **kwargs):
    G = read_topo(topo_filepath)
    F = read_flows(flow_filepath)
    # ASRelationsReader(relationship_filepath).augment_to_topology(G)
    # generate_local_policies(G, **kwargs)

    print(len(G.edges))
    # dump_topo(G, 'results.yaml')

    if '1' in algorithm_type:
        # cgfp_bgp_eval(G.copy(), F)
        initiate_ribs(G)
        for i in range(10):
            common_advertise(G)
        check_reachability(G, F)
    if '2' in algorithm_type:
        # cgc_bgp_eval(G.copy(), F)
        pass
    if '3' in algorithm_type:
        # fg_sfp_eval(G.copy(), F)
        pass
    if '4' in algorithm_type:
        pass
