#!/usr/bin/env python3

# import csv
import sys

# from sfp_eval.draw_bin.flow_loss_stat import Result

import numpy as np
import matplotlib.pyplot as plt
import matplotlib


def generate_plots(data, filename):
    N = 3
    # drop_cgfp_vec= [0.11501636056812128, 0.20516286710563422, 0.23843457787048516]
    # drop_cgc_vec= [0.6183041409470778, 0.6493825060540817, 0.6777975228622714]
    # drop_sfp_vec= [0, 0, 0]
    drop_cbgp_flow= 100*np.array([138131, 145074, 151422])/223403
    drop_fbgp_flow= 100*np.array([25695, 45834, 53267])/223403
    drop_sfp_flow= 100*np.array([0, 0, 0])
    drop_cbgp_vol= 100*np.array([450102615736681, 472176346090333, 496473179631100])/726039461241118
    drop_fbgp_vol= 100*np.array([84374190755121, 148334478099756, 176072119596606])/726039461241118
    drop_sfp_vol= 100*np.array([0, 0, 0])
    # drop_vol_vec = (data['CGFP-BGP'].drop_volume_ratio(), data['CGC-BGP'].drop_volume_ratio(), data['SFP'].drop_volume_ratio())

    matplotlib.rc('font', size=16)

    ind = np.arange(N)
    width = 0.1

    plt.axes([0, 0, N, 50])
    # plt.rc('font', family='sans-serif', weight='bold', size=10)
    fig, ax = plt.subplots()

    fig.subplots_adjust(bottom=0.15)
    fig.subplots_adjust(left=0.15)

    ax.set_ylim([0, 50])
    # rect1 = ax.bar(ind, drop_cbgp_flow, width, color='r', label='C-BGP (Flows)')
    rect3 = ax.bar(ind, drop_fbgp_flow, width, color='r', label='F-BGP (Flows)')
    rect5 = ax.bar(ind+2*width, drop_sfp_flow, width, color='m', label='SFP (Flows)')
    # rect2 = ax.bar(ind+width, drop_cbgp_vol, width, color='g', label='C-BGP (Volume)')
    rect4 = ax.bar(ind+width, drop_fbgp_vol, width, color='g', label='F-BGP (Volume)')
    rect6 = ax.bar(ind+3*width, drop_sfp_vol, width, color='b', label='SFP (Volume)')

    # ax.set_ylim([0, 100])
    ax.set_ylabel('Fraction of failed flows/volume (%)', fontsize=16)
    # ax.set_title('Loss when deflect traffic between neighboring peers')
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('1', '2', '3'))
    # ax.set_xlabel('number of peers applied the deflection policies')
    ax.set_xlabel('Number of pair of peers in deflection', fontsize=16)

    # ax.legend((rect1[0], rect2[0], rect3[0]), ("F-BGP" ,"C-BGP", "SFP"))
    ax.legend(ncol=1)
    # plt.show()

    fig.set_size_inches(4.5, 4.5)
    fig.savefig(filename)

if __name__ == '__main__':
    filename = sys.argv[1]

    # final = {i: {
    #     'CGFP-BGP': Result(),
    #     'CGC-BGP': Result(),
    #     'SFP': Result(),
    #     'SFP on CGC-BGP Reachable Flows': Result()
    # } for i in [1, 3, 5]}
    final = {}

    # for i in [1, 3, 5]:
    #     with open(filename + '-%d.csv' % i) as f:
    #         reader = csv.reader(f, delimiter='\t')
    #         count = 0
    #         for row in reader:
    #             if count % 4 == 0:
    #                 obj = final[i]['CGFP-BGP']  # type: Result
    #             elif count % 4 == 1:
    #                 obj = final[i]['CGC-BGP']  # type: Result
    #             elif count % 4 == 2:
    #                 obj = final[i]['SFP']  # type: Result
    #             else:
    #                 obj = final[i]['SFP on CGC-BGP Reachable Flows']
    #             count += 1
    #             obj.merge(Result(row))
    generate_plots(final, filename+".pdf")
