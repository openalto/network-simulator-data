#!/usr/bin/env thon

import json
from copy import deepcopy
from enum import Enum

from networkx import DiGraph

from on_demand_eval.flow_space import Match, Register, Packet, MatchFailedException, FlowSpace


class ACTION_TYPE(Enum):
    DROP = 0
    ON_DEMAND = -1


class ActionEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is ACTION_TYPE:
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class ActionDecoder(json.JSONDecoder):
    def decode(self, s):
        obj = json.JSONDecoder.decode(self, s)
        if type(obj) == str:
            if obj == 'ACTION_TYPE.DROP':
                return ACTION_TYPE.DROP
            elif obj == 'ACTION_TYPE.ON_DEMAND':
                return ACTION_TYPE.ON_DEMAND
        return obj


class Action():
    """
    Return a table id (int), an AS path (list), or an ACTION_TYPE
    """

    def __init__(self, action=ACTION_TYPE.DROP, vars={}):
        self.action = action
        self.vars = vars

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'action': self.action,
            'vars': self.vars
        }

    @staticmethod
    def decode(obj):
        if type(obj) == str:
            if obj == 'ACTION_TYPE.DROP':
                return ACTION_TYPE.DROP
            elif obj == 'ACTION_TYPE.ON_DEMAND':
                return ACTION_TYPE.ON_DEMAND
        return obj

    @staticmethod
    def from_dict(action_dict):
        return Action(action=Action.decode(action_dict['action']),
                      vars=action_dict['vars'])

    def do(self, register):
        """
        return a int if the action indicate to another table.
        return a list if the action indicate to an as path.
        """
        for var in self.vars.keys():
            register[var] = self.vars[var]
        return self.action

    def __eq__(self, other):
        if other.action == self.action and other.vars == self.vars:
            return True
        return False


class Rule():
    """
    A single rule entry including:

    Priority | Match | Registers | Action
    """

    def __init__(self, priority=0, match=None, action=None, table=None):
        self.priority = priority
        self.match = match or Match()
        self.action = action or Action()
        self.table = table
        self.id = 0

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'priority': self.priority,
            'match': self.match.to_dict(),
            'action': self.action.to_dict(),
            'table_id': self.table
        }

    @staticmethod
    def from_dict(rule_dict):
        return Rule(priority=rule_dict['priority'],
                    match=Match.from_dict(rule_dict['match']),
                    action=Action.from_dict(rule_dict['action']),
                    table=rule_dict['table_id'])

    def get_action(self, register):
        # type: (Register) -> Action
        """
        According to the action, find the final action of the packet,
        """
        return self.action

    def modify_action(self, action):
        # TODO: make self.match read-only
        return Rule(self.priority, self.match, action, self.table)


class Table():
    """
    A priority ordered list of rules.
    """

    def __init__(self, tid=0):
        self.id = tid
        self.rules = []  # type: list[Rule]
        self.next_rid = 0

    def __iter__(self):
        for rule in self.rules:
            yield rule

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'id': self.id,
            'rules': [r.to_dict() for r in self.rules]
        }

    @classmethod
    def from_dict(cls, table_dict):
        tid = table_dict['id']
        table = cls(tid)
        # table.rules = [Rule.from_dict(r) for r in table_dict['rules']]
        for r in table_dict['rules']:
            table.insert(Rule.from_dict(r))
        return table

    def size(self):
        """
        Every table implements a size() function.
        """
        return len(self.rules)

    def match(self, pkt, register, ret_index=False):
        # type: (Packet, Register) -> Rule
        for i in range(len(self.rules)):
            rule = self.rules[i]
            if rule.match.match(pkt, register):
                return (rule, i) if ret_index else rule
        raise MatchFailedException

    def insert(self, rule):
        # type: (Rule) -> bool
        priority = rule.priority
        index = 0
        while index < len(self.rules):
            if self.rules[index].priority <= priority:
                break
            index += 1
        self.rules.insert(index, rule)
        rule.id = self.next_rid
        self.next_rid += 1
        rule.table = self.id
        # for r in self.rules[index+1:]:
        #     r.id += 1
        return index

    def __contains__(self, item):
        # type: (Rule) -> bool
        for rule in self.rules:
            if rule.match == item.match and rule.priority == item.priority:
                return True
        return False

    def index_of(self, item):
        for i in range(len(self.rules)):
            rule = self.rules[i]
            if rule.match == item.match and rule.priority == item.priority:
                return i
        return -1

    def merge(self, other):
        # type: (Table) -> None
        for rule in other:
            idx = self.index_of(rule)
            if idx < 0:
                self.insert(deepcopy(rule))
                # print('Insert new rule', rule)
            elif rule.action.action is not ACTION_TYPE.ON_DEMAND:
                self.rules[idx].action = rule.action
                # print('Overwrite existing rule', rule)


class EfficientTable(DiGraph, Table):
    """
    """
    def __init__(self, tid=0, table=None):
        super(EfficientTable, self).__init__()
        self.id = tid
        self.rules = []
        self.next_rid = 0
        if table:
            self.id = table.id
            self.rules = table.rules

        self.build()

    def build(self):
        for r in self.rules:
            self.add_node(r.id, rule=r)

        for u in range(len(self.rules)):
            for v in range(u+1, len(self.rules)):
                eu = self.rules[u]
                ev = self.rules[v]
                if eu.match.intersect(ev.match) and eu.priority > ev.priority:
                    self.add_edge(eu.id, ev.id)

    def insert(self, rule):
        index = Table.insert(self, rule)
        if index < 0:
            return index
        self.add_node(rule.id, rule=rule)
        for eu in self.rules[:index]:
            if eu.match.intersect(rule.match) and eu.priority > rule.priority:
                if eu.id not in self.nodes():
                    self.add_node(eu.id, rule=eu)
                self.add_edge(eu.id, rule.id)
        for eu in self.rules[index+1:]:
            if eu.match.intersect(rule.match) and eu.priority < rule.priority:
                if eu not in self.nodes():
                    self.add_node(eu.id, rule=eu)
                self.add_edge(rule.id, eu.id)
        return index

    def project(self, flow_space):
        nset = []
        for e in self.nodes():
            rule = self.node[e]['rule']
            if flow_space.intersect(rule.match):
                nset.append(e)
        sub_table = self.subgraph(nset)
        sub_table.id = self.id
        sub_table.rules = self.rules
        return sub_table


class Pipeline():
    """
    Data structure for the generic pipeline.

    A pipeline of tables.
    """

    def __init__(self, layout=1, cls=Table):
        self.tables = []
        self.layout = layout
        if self.layout:
            for i in range(layout):
                self.tables.append(cls(i))

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'layout': self.layout,
            'tables': [t.to_dict() for t in self.tables]
        }

    @staticmethod
    def from_dict(pipeline_dict, cls=Table):
        layout = pipeline_dict['layout']
        pipeline = Pipeline(layout)
        for t in range(layout):
            pipeline.tables[t] = cls.from_dict(pipeline_dict['tables'][t])
        return pipeline

    def size(self):
        """
        Every pipeline abstract data structure should implement a size()
        function to return its own size at least.
        """
        return sum([t.size() for t in self.tables])

    def lookup(self, entry, ret_index=False):
        if type(entry) == Packet:
            return self.lookup_pkt(entry, ret_index)
        elif type(entry) == FlowSpace:
            return self.lookup_space(entry, ret_index)

    def lookup_pkt(self, pkt, ret_index=False):
        """
        Lookup the action of the packet. The result could be a AS path or None.
        """
        register = Register()
        execution = []
        execution_idx = []
        try:
            rule, idx = self.tables[0].match(pkt, register, ret_index=True)
            execution.append(rule)
            execution_idx.append((0, idx))
            action = rule.get_action(register).do(register)
            while True:
                if type(action) in (list, type(None), ACTION_TYPE):  # The action is drop or the action is a as path
                    return (action, execution_idx) if ret_index else (action, execution)
                elif type(action) is int:  # The action is another table
                    rule, idx = self.tables[action].match(pkt, register, ret_index=True)
                    execution.append(rule)
                    execution_idx.append((action, idx))
                    action = rule.get_action(register).do(register)
                else:
                    raise MatchFailedException()
        except MatchFailedException as e:
            # print("Match Failed")
            return (None, execution_idx) if ret_index else (None, execution)

    def lookup_space(self, flow_space, ret_index=False):
        """
        Lookup actions of a flow space.
        """
        raise "Unsupported feature in the current implementation."

    def merge(self, other):
        for i in range(len(other.tables)):
            self.tables[i].merge(other.tables[i])
