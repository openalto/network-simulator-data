#!/usr/bin/env python3

import csv
import sys

import matplotlib.pyplot as plt
import networkx

from sfp_eval.utils import graph_params


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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s filename" % sys.argv[0])
        exit(1)

    filename = sys.argv[1]

    nodes = {}  # type: dict{int, Node}
    links = []  # type: list{tuple{int, int}}

    G = read_topo(filename)

    pos = networkx.spring_layout(G)

    # networkx.draw_shell(G)
    networkx.draw_random(G)
    # networkx.draw-bin(G, pos, node_size=15, node_color='r', font_size=8, font_weight='bold')
    plt.tight_layout()
    plt.show()

    print("Avg degree: %f" % graph_params.avg_degree(G))
    print("Avg mutlihoming: %f" % graph_params.avg_multihoming(G))
