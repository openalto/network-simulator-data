import csv

import networkx


class Node:
    def __init__(self, id=0, x=0, y=0, data_tuple=None):
        if data_tuple:
            self.id = data_tuple[0]
            self.x = data_tuple[1]
            self.y = data_tuple[2]
        else:
            self.id = id
            self.x = x
            self.y = y


def read_topo(filename):
    nodes = {}  # type: dict{int, Node}
    links = []  # type: list{tuple{int, int}}

    with open(filename) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) == 3:
                nodes[row[0]] = Node(data_tuple=tuple(row))
            elif len(row) == 2:
                links.append(tuple(row))

    G = networkx.Graph()
    G.add_nodes_from(nodes.keys())
    G.add_edges_from(links)
    return G
