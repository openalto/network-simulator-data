#!/usr/bin/env python3

import csv
import sys

from sfp_eval.draw_bin.flow_loss_stat import Result

import numpy as np
import matplotlib.pyplot as plt


def generate_plots(data, filename):
    N = 3
    drop_flow_vec= (data['CGFP-BGP'].fail_flow_ratio(), data['CGC-BGP'].fail_flow_ratio(), data['SFP'].fail_flow_ratio())
    drop_vol_vec = (data['CGFP-BGP'].drop_volume_ratio(), data['CGC-BGP'].drop_volume_ratio(), data['SFP'].drop_volume_ratio())

    ind = np.arange(N)
    width = 0.2

    fig, ax = plt.subplots()

    rect1 = ax.bar(ind, drop_flow_vec, width, color='r')
    rect2 = ax.bar(ind+width, drop_vol_vec, width, color='b')

    ax.set_ylabel('Loss ratio')
    ax.set_title('Loss when block a single unused port')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(('CGFP-BGP', 'CGC-BGP', 'SFP'))

    ax.legend((rect1[0], rect2[0]), ("Flow loss ratio" ,"Volume loss ratio"))
    # plt.show()

    fig.set_size_inches(6, 3.8)
    fig.savefig(filename)

if __name__ == '__main__':
    filename = sys.argv[1]

    final = {
        'CGFP-BGP': Result(),
        'CGC-BGP': Result(),
        'SFP': Result(),
        'SFP on CGC-BGP Reachable Flows': Result()
    }

    with open(filename) as f:
        reader = csv.reader(f, delimiter='\t')
        count = 0
        for row in reader:
            if count % 4 == 0:
                obj = final['CGFP-BGP']  # type: Result
            elif count % 4 == 1:
                obj = final['CGC-BGP']  # type: Result
            elif count % 4 == 2:
                obj = final['SFP']  # type: Result
            else:
                obj = final['SFP on CGC-BGP Reachable Flows']
            count += 1
            obj.merge(Result(row))
    generate_plots(final, filename+".pdf")
