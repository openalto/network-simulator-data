#!/usr/bin/env python

from copy import deepcopy

from on_demand_eval.pipeline import Pipeline, Action, ACTION_TYPE
from on_demand_eval.rule_dg import RuleDependencyGraph
from on_demand_eval.flow_space import FlowSpace


class SFPSpeaker():
    """
    An implementation of SFP speaker.
    """
    def __init__(self):
        self.subs = {}

    def config_pipeline(self, pipeline):
        self.pipeline = pipeline

    def receive_sub(self, flow_space, peer):
        self.subs[peer] = flow_space

    def max_odi(self, pkt_query, peer):
        flow_space = self.subs.get(peer, FlowSpace())

        _, execution_idx = self.pipeline.lookup(pkt_query, ret_index=True)
        odi_pipeline = Pipeline(self.pipeline.layout)

        for t, i in execution_idx:
            table = self.pipeline.tables[t]
            odi_table = odi_pipeline.tables[t]
            odi_table.insert(deepcopy(table.rules[i]))
            rDAG = RuleDependencyGraph(table, flow_space)
            for j in rDAG.predecessors(i):
                if j != i:
                    od_rule = table.rules[j]
                    odi_table.insert(od_rule.modify_action(
                        Action(action=ACTION_TYPE.ON_DEMAND)))
        return odi_pipeline
