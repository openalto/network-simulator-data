#!/usr/bin/env python

from on_demand_eval.pipeline import Pipeline, ACTION_TYPE
from on_demand_eval.rule_dg import RuleDependencyGraph


def MaxODI(pipeline, pkt_query, flow_space):
    """
    Return maximum on-demand dissemination information for input flow space.
    """
    execution = pipeline.lookup(pkt_query)
    odi_pipeline = Pipeline(pipeline.layout())
    rule_set = set()
    for e in execution:
        odi_pipeline.insert(e)
        table = pipeline.tables[e.table]
        rule_dg = RuleDependencyGraph(table, flow_space)
        for ep in rule_dg.predecessors(e):
            if ep is not e:
                rule_set.add(ep)
    for ep in rule_set:
        odi_pipeline.tables[ep.table].insert(ep.modify_action(ACTION_TYPE.ON_DEMAND))
    return odi_pipeline
