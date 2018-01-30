#!/usr/bin/env python3

from on_demand_eval.pipeline import *


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


def multitable_test():
    pipeline = Pipeline()
    table0 = pipeline.tables[0]
    table1 = Table()
    pipeline.tables.append(table1)
    table2 = Table()
    pipeline.tables.append(table2)

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

    pkt = Packet(src_ip='202.113.16.128', dst_ip='141.217.1.1', src_port=80, dst_port=80, protocol='tcp')
    print(pipeline.lookup(pkt))

if __name__ == '__main__':
    single_match_test()
    multiple_match_test()
    match_intersection_test()
    multitable_test()
    exit(0)
