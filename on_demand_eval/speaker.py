#!/usr/bin/env python

import io
import json
from copy import deepcopy

from on_demand_eval.pipeline import Pipeline, Action, ACTION_TYPE, Table, EfficientTable
from on_demand_eval.pipeline import ActionEncoder, ActionDecoder
from on_demand_eval.rule_dg import RuleDependencyGraph
from on_demand_eval.flow_space import FlowSpace


class SFPSpeaker():
    """
    An implementation of SFP speaker.
    """
    def __init__(self, peer='0.0.0.0'):
        self.subs = {}
        self.peer = peer

    def config_pipeline(self, pipeline):
        self.pipeline = pipeline

    def config_pipeline_from_file(self, filename, table_cls=EfficientTable):
        if isinstance(filename, io.IOBase):
            self.pipeline = Pipeline.from_dict(json.load(filename, cls=ActionDecoder), cls=table_cls)
            return self.pipeline
        with open(filename, 'r') as f:
            self.pipeline = Pipeline.from_dict(json.load(f, cls=ActionDecoder), cls=table_cls)

    def dump_pipeline(self):
        print(json.dumps(self.pipeline, cls=ActionEncoder))

    def dump_pipeline_to_file(self, filename):
        if isinstance(filename, io.IOBase):
            json.dump(self.pipeline, filename, cls=ActionEncoder)
            return
        with open(filename, 'w') as f:
            json.dump(self.pipeline, f, cls=ActionEncoder)

    def receive_sub(self, flow_space, peer):
        self.subs[peer] = flow_space

    def max_odi(self, pkt_query, peer):
        flow_space = self.subs.get(peer, FlowSpace())

        _, execution_idx = self.pipeline.lookup(pkt_query, ret_index=True)
        odi_pipeline = Pipeline(self.pipeline.layout)

        for t, i in execution_idx:
            table = self.pipeline.tables[t]
            rule = table.rules[i]
            odi_table = odi_pipeline.tables[t]
            odi_table.insert(deepcopy(rule))
            rDAG = table.project(flow_space)
            for j in rDAG.predecessors(rule.id):
                od_rule = rDAG.node[j]['rule']
                odi_table.insert(od_rule.modify_action(
                    Action(action=ACTION_TYPE.ON_DEMAND)))
        return odi_pipeline
