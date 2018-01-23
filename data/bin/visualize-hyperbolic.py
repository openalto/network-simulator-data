#!/usr/bin/env python3

import sys

import matplotlib.pyplot as plt
import networkx

from sfp_eval.utils import graph_params, hyperbolics_reader

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s filename" % sys.argv[0])
        exit(1)

    filename = sys.argv[1]

    G = hyperbolics_reader.read_topo(filename)

    pos = networkx.spring_layout(G)

    # networkx.draw_shell(G)
    networkx.draw_random(G)
    # networkx.draw-bin(G, pos, node_size=15, node_color='r', font_size=8, font_weight='bold')
    plt.tight_layout()
    plt.show()

    print("Avg degree: %f" % graph_params.avg_degree(G))
    print("Avg mutlihoming: %f" % graph_params.avg_multihoming(G))
