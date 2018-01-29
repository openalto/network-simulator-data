#!/usr/bin/env python

import csv
import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from sfp_eval.draw_bin.flow_loss_stat import Result

MAX_PATH_LEN = 10
flows_range = range(2, MAX_PATH_LEN + 1)


def generate_plots(drop_ratio_dict, loop_ratio_dict, filename):
    N = len(drop_ratio_dict)
    sorted_ratio_keys = sorted(drop_ratio_dict.keys())
    cgfp_bgp_drop = tuple([drop_ratio_dict[i]['CGFP-BGP'] for i in sorted_ratio_keys])
    cgc_bgp_drop = tuple([drop_ratio_dict[i]['CGC-BGP'] for i in sorted_ratio_keys])
    sfp_drop = tuple([drop_ratio_dict[i]['SFP'] for i in sorted_ratio_keys])
    cgfp_bgp_loop = tuple([loop_ratio_dict[i]['CGFP-BGP'] for i in sorted_ratio_keys])
    cgc_bgp_loop = tuple([loop_ratio_dict[i]['CGC-BGP'] for i in sorted_ratio_keys])
    sfp_loop = tuple([loop_ratio_dict[i]['SFP'] for i in sorted_ratio_keys])
    # sfp_common = tuple([data[i]['SFP on CGFP-BGP Reachable Flows'] for i in data.keys()])

    ind = np.arange(N)
    width = 0.1

    fig, ax = plt.subplots()
    rects_cgfp_bgp_drop = ax.bar(ind, cgfp_bgp_drop, width, color='r')
    rects_cgfp_bgp_loop = ax.bar(ind + width, cgfp_bgp_loop, width, color='g')
    rects_cgc_bgp_drop = ax.bar(ind + width * 2, cgc_bgp_drop, width, color='c')
    rects_cgc_bgp_loop = ax.bar(ind + width * 3, cgc_bgp_loop, width, color='y')
    rects_sfp_drop = ax.bar(ind + width * 4, sfp_drop, width, color='m')
    rects_sfp_loop = ax.bar(ind + width * 5, sfp_loop, width, color='b')
    # rects_sfp_common = ax.bar(ind + width * 3, sfp_common, width, color='g')

    ax.set_ylabel('Loss volume ratio')
    ax.set_xlabel("Policy ratio")
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(sorted_ratio_keys)
    # ax.set_ylim([0, 1])

    ax.legend((rects_cgfp_bgp_drop[0], rects_cgfp_bgp_loop[0], rects_cgc_bgp_drop[0], rects_cgc_bgp_loop[0],
               rects_sfp_drop[0], rects_sfp_loop[0]),
              ('CGFG-BGP (drop)', 'CGFG-BGP (loop)', 'CGC-BGP (drop)', 'CGC-BGP (loop)', 'SFP (drop)', 'SFP (loop)'))
    # plt.show()
    fig.set_size_inches(6, 3.8)
    fig.savefig("%s.pdf" % filename)


def judge_policy_ratio(filename):
    ratio = ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
    for i in ratio:
        if i in filename:
            return str(float(i) * 100) + '%'


if __name__ == '__main__':
    folder_path = sys.argv[1]

    policy_types = ["t", "b", "h", 'bh', 'bt']

    for policy_type in policy_types:
        files = glob.glob(os.path.join(folder_path, "*.%s.csv" % policy_type))
        filenames = [os.path.basename(file) for file in files]

        drop_ratio_dict = {}
        loop_ratio_dict = {}
        final = {}
        for filename in filenames:
            ratio = judge_policy_ratio(filename)
            final[filename] = dict()
            final[filename]['CGFP-BGP'] = Result()
            final[filename]['CGC-BGP'] = Result()
            final[filename]['SFP'] = Result()
            final[filename]['SFP on CGFP-BGP Reachable Flows'] = Result()
            count = 0
            with open(os.path.join(folder_path, filename)) as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if count % 4 == 0:
                        obj = final[filename]['CGFP-BGP']  # type: Result
                    elif count % 4 == 1:
                        obj = final[filename]['CGC-BGP']  # type: Result
                    elif count % 4 == 2:
                        obj = final[filename]['SFP']  # type: Result
                    else:
                        obj = final[filename]['SFP on CGFP-BGP Reachable Flows']
                    count += 1
                    obj.merge(Result(row))
            drop_ratio_dict[ratio] = dict()
            drop_ratio_dict[ratio]['CGFP-BGP'] = final[filename]['CGFP-BGP'].drop_volume_ratio()
            drop_ratio_dict[ratio]['CGC-BGP'] = final[filename]['CGC-BGP'].drop_volume_ratio()
            drop_ratio_dict[ratio]['SFP'] = final[filename]['SFP'].drop_volume_ratio()
            drop_ratio_dict[ratio]['SFP on CGFP-BGP Reachable Flows'] = final[filename][
                'SFP on CGFP-BGP Reachable Flows'].drop_volume_ratio()
            loop_ratio_dict[ratio] = dict()
            loop_ratio_dict[ratio]['CGFP-BGP'] = final[filename]['CGFP-BGP'].loop_volume_ratio()
            loop_ratio_dict[ratio]['CGC-BGP'] = final[filename]['CGC-BGP'].loop_volume_ratio()
            loop_ratio_dict[ratio]['SFP'] = final[filename]['SFP'].loop_volume_ratio()
            loop_ratio_dict[ratio]['SFP on CGFP-BGP Reachable Flows'] = final[filename][
                'SFP on CGFP-BGP Reachable Flows'].loop_volume_ratio()
        generate_plots(drop_ratio_dict, loop_ratio_dict, 'loop_drop_volume.%s'% policy_type )
