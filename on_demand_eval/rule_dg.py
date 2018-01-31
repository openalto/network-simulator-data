#!/usr/bin/env python

from networkx import DiGraph
from on_demand_eval.pipeline import Table


class EfficientTable(DiGraph, Table):
    """
    """
    def __init__(self, tid=0, table=None):
        super(EfficientTable, self).__init__()
        self.id = tid
        if table:
            self.id = table.id
            self.rules = table.rules

        self.build()

    def build(self):
        for u in range(len(self.rules)):
            self.add_node(u)

        for u in range(len(self.rules)):
            for v in range(u+1, len(self.rules)):
                eu = self.rules[u]
                ev = self.rules[v]
                if eu.match.intersect(ev.match) and eu.priority > ev.priority:
                    self.add_edge(u, v)

    def insert(self, rule):
        priority = rule.priority
        index = 0
        while index < len(self.rules):
            if self.rules[index].priority <= priority:
                break
            index += 1
        self.rules.insert(index, rule)
        self.add_node(index)
        rule.table = self.id
        for u in range(len(self.rules)):
            if u == v:
                continue
            eu = self.rules[u]
            if eu.match.intersect(rule.match):
                if eu.priority > rule.priority:
                    self.add_edge(u, index)
                elif eu.priority < rule.priority:
                    self.add_edge(index, u)

    def project(self, flow_space):
        nset = []
        for e in self.nodes():
            if flow_space.intersect(rule.match):
                nset.append(e)
        sub_table = self.subgraph(nset)
        sub_table.id = self.id
        sub_table.rules = self.rules
        return sub_table


class RuleDependencyGraph(DiGraph):
    """
    Data structure for the rule dependency graph.

    Given a rule dependency graph $G^D(T_i, X)$, each node $v$ represents a
    rule in table $T_i$ whose match space has a non-empty intersection with the
    on-demand domain space $X$. Given two nodes $v$ and $u$, there exists a
    directed edge $(u, v)$ in this graph if:

    (1) their match spaces have a non-empty intersection; and
    (2) $u$ has a higher priority than $v$.
    """

    def __init__(self, table, flow_space):
        super(RuleDependencyGraph, self).__init__()
        self.raw_table = table
        self.flow_space = flow_space
        self.table = Table()
        self.build()

    def build(self):
        for rule in self.raw_table:
            if self.flow_space.intersect(rule.match):
                self.table.insert(rule)

        for u in range(len(self.table.rules)):
            self.add_node(u)

        for u in range(len(self.table.rules)):
            for v in range(len(self.table.rules)):
                if u == v:
                    continue
                eu = self.table.rules[u]
                ev = self.table.rules[v]
                if eu.match.intersect(ev.match) and eu.priority > ev.priority:
                    self.add_edge(u, v)
