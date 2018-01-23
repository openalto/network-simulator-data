#!/usr/bin/env python

import os
import sys
import csv
import glob

import numpy as np
import matplotlib.pyplot as plt

BLACKHOLE_3_3 = "result.0.3.0.3.blackhole.csv"
BLACKHOLE_5_5 = "result.0.5.0.5.blackhole.csv"
DEFLECTION_3_3 = "result.0.3.0.3.deflection.csv"
DEFLECTION_5_5 = "result.0.5.0.5.deflection.csv"
BOTH_3_3 = "result.0.3.0.3.both.csv"
BOTH_5_5 = "result.0.5.0.5.both.csv"

MAX_PATH_LEN = 10
flows_range = range(2, MAX_PATH_LEN + 1)

class Result:
    def __init__(self, data=None):
        self.hop_count = list()
        self.loop_count = 0
        self.drop_count = 0
        self.success_volume = 0
        self.fail_volume = 0
        for i in range(0, MAX_PATH_LEN+1):
            self.hop_count.append(0)
        if data is not None:
            for i in flows_range:
                self.hop_count[i] = int(data[i - 2])
            self.loop_count = int(data[MAX_PATH_LEN-1])
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

def generate_plots(data):
        N = len(data)
        cgfp_bgp = tuple([data[i]['CGFP-BGP'] for i in data.keys()])
        cgc_bgp = tuple([data[i]['CGC-BGP'] for i in data.keys()])
        sfp = tuple([data[i]['SFP'] for i in data.keys()])
        # sfp_common = tuple([data[i]['SFP on CGFP-BGP Reachable Flows'] for i in data.keys()])

        ind = np.arange(N)
        width = 0.2

        fig, ax = plt.subplots()
        rects_cgfp_bgp = ax.bar(ind, cgfp_bgp, width, color='r')
        rects_cgc_bgp = ax.bar(ind + width, cgc_bgp, width, color='y')
        rects_sfp = ax.bar(ind + width * 2, sfp, width, color='b')
        # rects_sfp_common = ax.bar(ind + width * 3, sfp_common, width, color='g')

        ax.set_ylabel('Volume ratio')
        ax.set_xlabel("Policy ratio")
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(tuple(data.keys()))
        #ax.set_ylim([0, 1])

        ax.legend((rects_cgfp_bgp[0], rects_cgc_bgp[0], rects_sfp[0]), ('CGFG-BGP', 'CGC-BGP', 'SFP'))
        # plt.show()
        fig.set_size_inches(6, 3.8)
        fig.savefig("result.volume.pdf")

def judge_policy_ratio(filename):
    ratio = ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
    for i in ratio:
        if i in filename:
            return str(float(i)*100)+'%'

if __name__ == '__main__':
    folder_path = sys.argv[1]

    files = glob.glob(os.path.join(folder_path, "*.both.csv"))
    filenames = [os.path.basename(file) for file in files]

    volume_dict = {}
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
        volume_dict[ratio] = dict()
        volume_dict[ratio]['CGFP-BGP'] = final[filename]['CGFP-BGP'].success_volume_ratio()
        volume_dict[ratio]['CGC-BGP'] = final[filename]['CGC-BGP'].success_volume_ratio()
        volume_dict[ratio]['SFP'] = final[filename]['SFP'].success_volume_ratio()
        volume_dict[ratio]['SFP on CGFP-BGP Reachable Flows'] = final[filename]['SFP on CGFP-BGP Reachable Flows'].success_volume_ratio()
    generate_plots(volume_dict)
