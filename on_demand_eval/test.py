#!/usr/bin/env python3

from on_demand_eval.pipeline import *
from on_demand_eval.flow_space import FlowSpace
from on_demand_eval.speaker import SFPSpeaker


def single_match_test():
    pipeline = Pipeline()
    table = pipeline.tables[0]
    match = Match(src_ip='10.0.0.0/24', dst_ip='10.0.1.0/24')
    action = Action(action=[1, 10])
    table.insert(Rule(priority=3, match=match, action=action))
    packet1 = Packet('10.0.0.1', '10.0.1.2', 80, 443, 'TCP')
    packet2 = Packet('10.0.3.3', '10.0.1.2', 80, 443, 'TCP')
    print(pipeline.lookup(packet1))
    print(pipeline.lookup(packet2))


def multiple_match_test():
    pipeline = Pipeline()
    table = pipeline.tables[0]

    table.insert(
        Rule(priority=3, match=Match(src_ip='10.0.0.0/24', dst_ip='10.0.1.0/24'), action=Action(action=[1, 10])))

    table.insert(
        Rule(priority=2, match=Match(src_ip='10.0.0.0/24', dst_ip='10.0.1.0/24'), action=Action(action=[1, 20])))

    table.insert(
        Rule(priority=2, match=Match(src_ip='10.0.3.0/24', dst_ip='10.0.1.0/24'), action=Action(action=[1, 30])))

    table.insert(
        Rule(priority=3, match=Match(src_ip='10.0.3.0/24', dst_ip='10.0.1.0/24'), action=Action(action=[1, 40])))
    packet1 = Packet('10.0.0.1', '10.0.1.2', 80, 443, 'TCP')
    packet2 = Packet('10.0.2.1', '10.0.1.2', 80, 443, 'TCP')
    packet3 = Packet('10.0.3.3', '10.0.1.2', 80, 443, 'TCP')
    packet4 = Packet('10.0.2.1', '10.0.3.2', 80, 443, 'TCP')

    print(pipeline.lookup(packet1))
    print(pipeline.lookup(packet2))
    print(pipeline.lookup(packet3))
    print(pipeline.lookup(packet4))


def match_intersection_test():
    match1 = Match(src_ip='10.0.0.0/24')
    match2 = Match(dst_ip='10.0.0.0/24')
    match3 = match1.intersect(match2)
    print(match3)


def build_example_pipeline(cls=Table):
    pipeline = Pipeline(layout=3, cls=cls)
    table0 = pipeline.tables[0]
    table1 = pipeline.tables[1]
    table2 = pipeline.tables[2]

    table0.insert(
        Rule(priority=2, match=Match(src_ip='202.113.17.0/25'), action=Action(1, vars={"var1": 2}))
    )
    table0.insert(
        Rule(priority=2, match=Match(src_ip='202.113.16.0/25'), action=Action(1, vars={"var1": 1}))
    )
    table0.insert(
        Rule(priority=1, match=Match(src_ip='202.113.16.0/24'), action=Action(1, vars={"var1": 2}))
    )

    table1.insert(
        Rule(priority=2, match=Match(dst_ip='141.217.1.0/25'), action=Action(2, vars={'var2': 1}))
    )

    table1.insert(
        Rule(priority=1, match=Match(dst_ip='141.217.1.0/24'), action=Action(2, vars={'var2': 2}))
    )

    table2.insert(
        Rule(priority=1, match=Match(register_checker={"var1": 1, "var2": 1}), action=Action(['P1', 'D']))
    )
    table2.insert(
        Rule(priority=1, match=Match(register_checker={"var1": 1, "var2": 2}), action=Action(['P1', 'P2', 'C', 'D']))
    )
    table2.insert(
        Rule(priority=1, match=Match(register_checker={"var1": 2, "var2": 1}), action=Action(['P1', 'C', 'D']))
    )
    table2.insert(
        Rule(priority=1, match=Match(register_checker={"var1": 2, "var2": 2}), action=Action(['P1', 'D']))
    )

    return pipeline


def multitable_test():
    pipeline = build_example_pipeline()

    pkt = Packet(src_ip='202.113.16.128', dst_ip='141.217.1.1', src_port=80, dst_port=80, protocol='tcp')
    print(pkt)
    print(pipeline.lookup(pkt))


def max_odi_test():
    speaker = SFPSpeaker()

    speaker.config_pipeline(build_example_pipeline(cls=EfficientTable))

    flow_space = FlowSpace(matches={Match(src_ip='202.113.16.0/24'), Match(dst_ip='141.217.1.0/25')})
    peer = '10.0.0.1'
    speaker.receive_sub(flow_space, peer)

    pkt = Packet(src_ip='202.113.16.128', dst_ip='141.217.1.1', src_port=80, dst_port=80, protocol='tcp')
    print(pkt)
    odi = speaker.max_odi(pkt, peer)
    print(odi)
    return odi


def config_dump_test():
    print('SFP Speaker Pipeline Config/Dump Test:')
    speaker = SFPSpeaker()

    pipeline = max_odi_test()
    speaker.config_pipeline(pipeline)
    # pipeline_s = speaker.dump_pipeline()
    import json
    pipeline_s = json.dumps(speaker.pipeline.to_dict(), cls=ActionEncoder)
    print('Dump current pipeline to string:')
    print(pipeline_s)

    from io import StringIO
    pipeline_f = StringIO(pipeline_s)
    speaker.config_pipeline_from_file(pipeline_f)
    print('Config pipeline from an IO stream:')
    print(speaker.pipeline)


if __name__ == '__main__':
    single_match_test()
    multiple_match_test()
    match_intersection_test()
    multitable_test()
    max_odi_test()
    config_dump_test()
    exit(0)
