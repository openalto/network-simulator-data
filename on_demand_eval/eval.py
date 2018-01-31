#!/usr/bin/env python
import os
from random import sample

from on_demand_eval.flow_space import Match, FlowSpace, Packet
from on_demand_eval.pipeline import Action, Rule, Pipeline, ACTION_TYPE
from on_demand_eval.speaker import SFPSpeaker
from sfp_eval.bin.announcement_sim import read_flows

import csv

RANDOM_PORT_DIST = {p: 0.005 for p in range(50200, 50400)}


def max_odi_test(pipeline_db, traffic_db, par=(1, 2), output_folder='.'):
    """
    Input parameters:
        pipeline_db: the file stores the whole pipeline of Speaker B
        traffic_db:  the file stores the trace data of real traffic
    """

    output_path = os.path.join(output_folder, '%d_%d_odi.csv'%(par[0], par[1]))
    writer = csv.writer(open(output_path, 'w'), delimiter='\t')

    SpeakerA = SFPSpeaker('10.0.1.1')
    SpeakerB = SFPSpeaker('10.0.2.1')
    SpeakerB.config_pipeline_from_file(pipeline_db)

    flows = read_flows(traffic_db, port_dist=RANDOM_PORT_DIST)
    flows.sort(key=lambda d: d['start_time'])

    # Step 1:
    #   Speaker A request a flow space from Speaker B;
    #   Speaker B returns ON_DEMAND action for the whole flow space.
    flow_space = FlowSpace(matches={Match()})
    SpeakerB.receive_sub(flow_space, SpeakerA.peer)
    all_on_demand = Pipeline(layout=SpeakerB.pipeline.layout)
    all_on_demand.tables[0].insert(
        Rule(priority=0, match=Match(), action=Action(action=ACTION_TYPE.ON_DEMAND))
    )
    SpeakerA.config_pipeline(all_on_demand)

    # Step 2:
    #   Follow the time order of traffic trace data;
    print('Sending traffic...')
    cnt = 0
    miss_cnt = 0
    sum_volume = 0
    ondemand_volume = 0
    for f in flows:
        cnt += 1
        pkt = Packet(src_port=54321, protocol='TCP', **f)
        action, executions = SpeakerA.pipeline.lookup(pkt)
        sum_volume += f["volume"]

        #   Speaker A query packet p from Speaker B,
        #   if A's pipeline return ON_DEMAND for packet p.
        # print(action)
        # print(executions)
        if action is ACTION_TYPE.ON_DEMAND:
            ondemand_volume += f["volume"]
            miss_cnt += 1
            # Step 3:
            #   Speaker B run max_odi alg and return new pipeline to Speaker A;
            #   Speaker A merge the new pipeline into its own pipeline.
            # TODO: record miss hint
            updated_pipeline = SpeakerB.max_odi(pkt, SpeakerA.peer)
            # TODO: record exchanged message size
            # print('Packet miss: %s; Exchange message size: %d; Miss/Total: %d/%d'
            #       % (pkt, updated_pipeline.size(), miss_cnt, cnt))
            writer.writerow([pkt.src_ip, pkt.dst_ip, pkt.src_port, pkt.dst_port, pkt.protocol, updated_pipeline.size(), miss_cnt, cnt, ondemand_volume, sum_volume])
            SpeakerA.pipeline.merge(updated_pipeline)
            # print(SpeakerA.pipeline)
        # Step 4:
        #   Repeat Step 2
    writer.writerow([miss_cnt, cnt, ondemand_volume, sum_volume])


if __name__ == '__main__':
    import sys

    pipeline_db = sys.argv[1]
    traffic_db = sys.argv[2]
    max_odi_test(pipeline_db, traffic_db)
