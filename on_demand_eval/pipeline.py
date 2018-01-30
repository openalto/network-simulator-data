#!/usr/bin/env thon
from copy import deepcopy
from enum import Enum

from on_demand_eval.flow_space import Match, Register, Packet, MatchFailedException, FlowSpace


class ACTION_TYPE(Enum):
    DROP = 0
    ON_DEMAND = -1


class Action():
    """
    Return a table id (int), an AS path (list), or an ACTION_TYPE
    """

    def __init__(self, action=ACTION_TYPE.DROP, vars={}):
        self.action = action
        self.vars = vars

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

    def __init__(self):
        self.id = 0
        self.rules = []  # type: list[Rule]

    def __iter__(self):
        for rule in self.rules:
            yield rule

    def size(self):
        """
        Every table implements a size() function.
        """
        return len(self.rules)

    def match(self, pkt, register):
        # type: (Packet, Register) -> Rule
        for rule in self.rules:
            if rule.match.match(pkt, register):
                return rule
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
        rule.table = self.id
        return True

    def __contains__(self, item):
        # type: (Rule) -> bool
        for rule in self.rules:
            if rule.action == item.action and rule.match == item.match and rule.priority == item.priority:
                return True
        return False

    def merge(self, other):
        # type: (Table) -> None
        for rule in other:
            if rule in self:
                self.insert(deepcopy(rule))


class Pipeline():
    """
    Data structure for the generic pipeline.

    A pipeline of tables.
    """

    def __init__(self, layout=1):
        self.tables = []
        if layout:
            for i in range(layout):
                self.tables.append(Table())

    def layout(self):
        return len(self.tables)

    def size(self):
        """
        Every pipeline abstract data structure should implement a size()
        function to return its own size at least.
        """
        return sum([t.size() for t in self.tables])

    def lookup(self, entry):
        if type(entry) == Packet:
            return self.lookup_pkt(entry)
        elif type(entry) == FlowSpace:
            return self.lookup_space(entry)

    def lookup_pkt(self, pkt):
        """
        Lookup the action of the packet. The result could be a AS path or None.
        """
        register = Register()
        execution = []
        try:
            rule = self.tables[0].match(pkt, register)
            execution.append(rule)
            action = rule.get_action(register).do(register)
            while True:
                if action is None or type(action) == list:  # The action is drop or the action is a as path
                    return action, execution
                elif type(action) == int:  # The action is another table
                    rule = self.tables[action].match(pkt, register)
                    execution.append(rule)
                    action = rule.get_action(register).do(register)
        except MatchFailedException as e:
            print("Match Failed")
            return None, execution

    def lookup_space(self, flow_space):
        """
        Lookup actions of a flow space.
        """
        pass

    def merge(self, other):
        for i in range(other.tables):
            self.tables[i].merge(other.tables[i])
