#!/usr/bin/env python3

# import csv
import sys

# from sfp_eval.draw_bin.flow_loss_stat import Result

import numpy as np
import matplotlib.pyplot as plt


def generate_plots(data, filename):
    N = 3
    # drop_cgfp_vec= [0.11501636056812128, 0.20516286710563422, 0.23843457787048516]
    # drop_cgc_vec= [0.6183041409470778, 0.6493825060540817, 0.6777975228622714]
    # drop_sfp_vec= [0, 0, 0]
    drop_cbgp_flow= 100*np.array([112558, 144199, 213338])/223403
    drop_fbgp_flow= 100*np.array([0, 0, 0])
    drop_sfp_flow= 100*np.array([0, 0, 0])
    drop_cbgp_vol= 100*np.array([372723424501441, 476423418691906, 693306747619368])/726039461241118
    drop_fbgp_vol= 100*np.array([0, 0, 0])
    drop_sfp_vol= 100*np.array([0, 0, 0])
    # drop_vol_vec = (data['CGFP-BGP'].drop_volume_ratio(), data['CGC-BGP'].drop_volume_ratio(), data['SFP'].drop_volume_ratio())

    ind = np.arange(N)
    width = 0.1

    # plt.rc('font', family='sans-serif', weight='bold', size=10)
    fig, ax = plt.subplots()

    fig.subplots_adjust(bottom=0.15)

    rect1 = ax.bar(ind, drop_cbgp_flow, width, color='r', label='C-BGP (Flows)')
    # rect3 = ax.bar(ind+2*width, drop_fbgp_flow, width, color='c', label='F-BGP (Flows)')
    rect5 = ax.bar(ind+2*width, drop_sfp_flow, width, color='m', label='SFP (Flows)')
    rect2 = ax.bar(ind+width, drop_cbgp_vol, width, color='g', label='C-BGP (Volume)')
    # rect4 = ax.bar(ind+3*width, drop_fbgp_vol, width, color='y', label='F-BGP (Volume)')
    rect6 = ax.bar(ind+3*width, drop_sfp_vol, width, color='b', label='SFP (Volume)')

    ax.set_ylabel('Fraction of failed flows/volume (%)', fontsize=14)
    # ax.set_title('Loss when deflect traffic between neighboring peers')
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('1', '3', '5'))
    # ax.set_xlabel('number of peers applied the deflection policies')
    ax.set_xlabel('Number of networks applied the fine-grained block policies', fontsize=14)

    # ax.legend((rect1[0], rect2[0], rect3[0]), ("F-BGP" ,"C-BGP", "SFP"))
    ax.legend(ncol=2)
    # plt.show()

    fig.set_size_inches(6.4, 3.8)
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
