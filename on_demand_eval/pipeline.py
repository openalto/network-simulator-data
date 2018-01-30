#!/usr/bin/env python


class Match():
    """
    A header field map. Each header field includes a prefix value.
    """

    def __init__(self):
        pass

    def intersect(self):
        pass

    def compare(self):
        pass

    def to_header_space(self):
        pass

    def to_dict(self):
        pass


class Rule():
    """
    A single rule entry: Match -> Action
    """

    def __init__(self):
        pass


class Table():
    """
    A priority ordered list of rules.
    """

    def __init__(self):
        pass

    def size(self):
        """
        Every table implements a size() function.
        """
        return 0


class Pipeline():
    """
    Data structure for the generic pipeline.

    A pipeline of tables.
    """

    def __init__(self):
        self.tables = []

    def size(self):
        """
        Every pipeline abstract data structure should implement a size()
        function to return its own size at least.
        """
        return sum([t.size() for t in self.tables])
