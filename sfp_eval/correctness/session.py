#!/usr/bin/env python{}{}
# from sfp_eval.correctness.flow import read_flows
from sfp_eval.bin.announcement_sim import read_flows
from sfp_eval.correctness.advertise import initiate_ribs, fp_bgp_advertise, correct_bgp_advertise, sfp_advertise
from sfp_eval.correctness.advertise import report_rib, report_local_policy, read_local_rib
from sfp_eval.correctness.policies import generate_local_policies
from sfp_eval.correctness.policies import manual_policy
from sfp_eval.correctness.route import check_reachability
from sfp_eval.correctness.topology import read_topo


def session_start(topo_filepath,
                  flow_filepath,
                  algorithm_type='1',
                  **kwargs):

    G = read_topo(topo_filepath)
    F = read_flows(flow_filepath)
    # ASRelationsReader(relationship_filepath).augment_to_topology(G)
    generate_local_policies(G, **kwargs)
    # manual_policy(G)

    # dump_topo(G, 'results.yaml')

    if '1' in algorithm_type:
        print("CGFP-BGP Evaluation")
        # cgfp_bgp_eval(G.copy(), F)
        H = G.copy()
        H.ip_prefixes = G.ip_prefixes
        initiate_ribs(H)
        for i in range(20):
            fp_bgp_advertise(H)
        # print('============================== RIB ============================')
        # report_rib(H, 29)
        # report_rib(H, 30)
        # print('============================== LOCAL ============================')
        # report_local_policy(H, 29)
        # report_local_policy(H, 30)
        check_reachability(H, F)
        del H
    if '2' in algorithm_type:
        print("CGC-BGP Evaluation")
        # cgc_bgp_eval(G.copy(), F)
        H = G.copy()
        H.ip_prefixes = G.ip_prefixes
        initiate_ribs(H)
        for i in range(10):
            correct_bgp_advertise(H)
        check_reachability(H, F)
        del H
    if '3' in algorithm_type:
        print("SFP Evaluation")
        # fg_sfp_eval(G.copy(), F)
        H = G.copy()
        H.ip_prefixes = G.ip_prefixes
        report_rib(G, 29)
        initiate_ribs(H)
        report_rib(H, 29)
        for i in range(10):
            sfp_advertise(H)
        # print('============================== RIB ============================')
        # report_rib(H)
        # report_rib(H, 29)
        # report_rib(H, 30)
        # report_rib(H, 59)
        # print('============================== Adj-RIBs-In ============================')
        # report_rib(H, 29, table='adj-ribs-in', neigh=30)
        # report_rib(H, 30, table='adj-ribs-in', neigh=29)
        # print('============================== AS 29 Read Local ============================')
        # print(read_local_rib(H, 29, '128.211.128.0/19', 80))
        # print('============================== AS 30 Read Local ============================')
        # print(read_local_rib(H, 30, '128.211.128.0/19', 80))
        # print('============================== LOCAL ============================')
        # report_local_policy(H)
        check_reachability(H, F)
        del H
    if '4' in algorithm_type:
        pass
