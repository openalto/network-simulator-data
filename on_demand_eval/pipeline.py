#!/usr/bin/env thon

from on_demand_eval.flow_space import Match, Register, Packet, MatchFailedException


class Action():
    """
    Return a table id (int), an AS path (list) or a register modification (map).
    """

    def __init__(self, action=None, vars={}):
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


class Rule():
    """
    A single rule entry including:

    Priority | Match | Registers | Action
    """

    def __init__(self, priority=0, match=None, action=None):
        self.priority = priority
        self.match = match or Match()
        self.action = action or Action()

    def get_action(self, register):
        # type: (Register) -> Action
        """
        According to the action, find the final action of the packet,
        """
        return self.action


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
        return True


class Pipeline():
    """
    Data structure for the generic pipeline.

    A pipeline of tables.
    """

    def __init__(self, table=None):
        if table:
            self.tables = [table]
        else:
            self.tables = [Table()]  # type: list[Table]

    def size(self):
        """
        Every pipeline abstract data structure should implement a size()
        function to return its own size at least.
        """
        return sum([t.size() for t in self.tables])

    def lookup(self, pkt):
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
