#!/usr/bin/env python

import os
import json

from on_demand_eval.pipeline import Action, Match, Rule, Pipeline, ACTION_TYPE, ActionEncoder
from on_demand_eval.flow_space import Match, FlowSpace, Packet


def convert_to_pipeline(filename, dirname):
    with open(filename) as f:
        ribs = json.load(f)

    for n in ribs:
        rib = ribs[n]
        pl = Pipeline()
        tbl0 = pl.tables[0]
        for prefix in rib:
            prefix_actions = rib[prefix]
            for port in prefix_actions:
                action = prefix_actions[port]
                if action:
                    act = Action(action=['A', 'B', 'C'])
                else:
                    act = Action(action=ACTION_TYPE.DROP)
                if port > 0:
                    rule = Rule(priority=20, match=Match(dst_ip=prefix, dst_port=port),
                                action=act)
                else:
                    rule = Rule(priority=10, match=Match(dst_ip=prefix),
                                action=act)
                tbl0.insert(rule)
            if port not in prefix_actions:
                tbl0.insert(
                    Rule(priority=10, match=Match(dst_ip=prefix),
                         action=act)
                )
        with open(os.path.join(dirname, 'pipeline-%d' % n)) as f:
            json.dump(pl.to_dict(), f)


if __name__ == '__main__':
    import sys
    convert_to_pipeline(sys.argv[1], sys.argv[2])
