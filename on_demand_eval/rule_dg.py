#!/usr/bin/env python


class RuleDependencyGraph():
    """
    Data structure for the rule dependency graph.

    Given a rule dependency graph $G^D(T_i, X)$, each node $v$ represents a
    rule in table $T_i$ whose match space has a non-empty intersection with the
    on-demand domain space $X$. Given two nodes $v$ and $u$, there exists a
    directed edge $(v, u)$ in this graph if:

    (1) their match spaces have a non-empty intersection; and
    (2) $v$ has a higher priority than $u$.
    """

    def __init__(self):
        pass
