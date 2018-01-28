#!/usr/bin/env python

import csv
import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

BLACKHOLE_3_3 = "results.0.3.0.3.blackhole.csv"
BLACKHOLE_5_5 = "results.0.5.0.5.blackhole.csv"
DEFLECTION_3_3 = "results.0.3.0.3.deflection.csv"
DEFLECTION_5_5 = "results.0.5.0.5.deflection.csv"
BOTH_3_3 = "results.0.3.0.3.both.csv"
BOTH_5_5 = "results.0.5.0.5.both.csv"

MAX_PATH_LEN = 10
flows_range = range(2, MAX_PATH_LEN + 1)


class Result:
    def __init__(self, data=None):
        self.hop_count = list()
        self.loop_count = 0
        self.drop_count = 0
        self.success_volume = 0
        self.fail_volume = 0
        for i in range(0, MAX_PATH_LEN + 1):
            self.hop_count.append(0)
        if data is not None:
            for i in flows_range:
                self.hop_count[i] = int(data[i - 2])
            self.loop_count = int(data[MAX_PATH_LEN - 1])
            self.drop_count = int(data[MAX_PATH_LEN])
            self.success_volume = int(data[MAX_PATH_LEN + 1])
            self.fail_volume = int(data[MAX_PATH_LEN + 2])

    def merge(self, other):
        """
        :type other: Result
        """
        for i in range(0, MAX_PATH_LEN + 1):
            self.hop_count[i] += other.hop_count[i]
        self.loop_count += other.loop_count
        self.drop_count += other.drop_count
        self.success_volume += other.success_volume
        self.fail_volume += other.fail_volume

    def to_dict(self):
        dic = dict()
        dic["hop_count"] = dict()
        for i in flows_range:
            dic["hop_count"][i] = self.hop_count[i]
        dic["loop_count"] = self.loop_count
        dic["drop_count"] = self.drop_count
        dic["success_volume"] = self.success_volume
        dic["fail_volume"] = self.fail_volume
        return dic

    def sum_flows(self):
        return sum(self.hop_count) + self.drop_count + self.loop_count
        # return sum(self.hop_count)

    def cdf(self, hop):
        return sum(self.hop_count[:hop + 1]) / self.sum_flows()

    def success_volume_ratio(self):
        return self.success_volume / (self.success_volume + self.fail_volume)

    def loop_ratio(self):
        return self.loop_count / self.sum_flows()

    def drop_ratio(self):
        return self.drop_count / self.sum_flows()


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

    ax.set_ylabel('Loss ratio')
    ax.set_xlabel("Policy ratio")
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(sorted_ratio_keys)
    # ax.set_ylim([0, 1])

    ax.legend((rects_cgfp_bgp_drop[0], rects_cgfp_bgp_loop[0], rects_cgc_bgp_drop[0], rects_cgc_bgp_loop[0],
               rects_sfp_drop[0], rects_sfp_loop[0]),
              ('CGFG-BGP (drop)', 'CGFG-BGP (loop)', 'CGC-BGP (drop)', 'CGC-BGP (loop)', 'SFP (drop)', 'SFP (loop)'))
    # plt.show()
    fig.set_size_inches(6, 3.8)
    fig.savefig("%s.loss.pdf" % filename)


def judge_policy_ratio(filename):
    ratio = ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
    for i in ratio:
        if i in filename:
            return str(float(i) * 100) + '%'


if __name__ == '__main__':
    folder_path = sys.argv[1]

    # policy_types = ["both", "blackhole", "deflection"]

    # for policy_type in policy_types:
    files = glob.glob(os.path.join(folder_path, "*.csv"))
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
        drop_ratio_dict[ratio]['CGFP-BGP'] = final[filename]['CGFP-BGP'].drop_ratio()
        drop_ratio_dict[ratio]['CGC-BGP'] = final[filename]['CGC-BGP'].drop_ratio()
        drop_ratio_dict[ratio]['SFP'] = final[filename]['SFP'].drop_ratio()
        drop_ratio_dict[ratio]['SFP on CGFP-BGP Reachable Flows'] = final[filename][
            'SFP on CGFP-BGP Reachable Flows'].drop_ratio()
        loop_ratio_dict[ratio] = dict()
        loop_ratio_dict[ratio]['CGFP-BGP'] = final[filename]['CGFP-BGP'].loop_ratio()
        loop_ratio_dict[ratio]['CGC-BGP'] = final[filename]['CGC-BGP'].loop_ratio()
        loop_ratio_dict[ratio]['SFP'] = final[filename]['SFP'].loop_ratio()
        loop_ratio_dict[ratio]['SFP on CGFP-BGP Reachable Flows'] = final[filename][
            'SFP on CGFP-BGP Reachable Flows'].loop_ratio()
    generate_plots(drop_ratio_dict, loop_ratio_dict, 'reachability')
