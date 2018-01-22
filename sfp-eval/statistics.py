#!/usr/bin/env python

import csv
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

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


BLACKHOLE_3_3 = "result.0.5.0.5.blackhole.csv"
BLACKHOLE_5_5 = "result.0.9.0.9.blackhole.csv"
DEFLECTION_3_3 = "result.0.5.0.5.deflection.csv"
DEFLECTION_5_5 = "result.0.9.0.9.deflection.csv"
BOTH_3_3 = "result.0.5.0.5.both.csv"
BOTH_5_5 = "result.0.9.0.9.both.csv"


def generate_plots(data, name, location=None):
    if location is not None:
        plt.subplot(location)
    N = len(flows_range)
    cgfp_bgp = tuple([data['CGFP-BGP'].cdf(i) for i in flows_range])
    cgc_bgp = tuple([data['CGC-BGP'].cdf(i) for i in flows_range])
    sfp = tuple([data['SFP'].cdf(i) for i in flows_range])
    sfp_common = tuple([sum(data['SFP on CGFP-BGP Reachable Flows'].hop_count[:i+1]) / data['CGFP-BGP'].sum_flows() for i in flows_range])
    # sfp_common = tuple([data['SFP on CGFP-BGP Reachable Flows'].cdf(i) for i in flows_range])
    print("======== Debug: %s =======" % name)
    print(data['CGFP-BGP'].sum_flows())
    print(data['CGC-BGP'].sum_flows())
    print(data['SFP'].sum_flows())

    ind = np.arange(N)
    width = 0.2

    fig, ax = plt.subplots()
    rects_cgfp_bgp = ax.bar(ind, cgfp_bgp, width, color='r')
    rects_cgc_bgp = ax.bar(ind + width, cgc_bgp, width, color='y')
    rects_sfp = ax.bar(ind + width * 2, sfp, width, color='b')
    rects_sfp_common = ax.bar(ind + width * 2, sfp_common, width, color='g')

    ax.set_ylabel('CDF')
    ax.set_xlabel("AS path length")
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(tuple(flows_range))
    ax.set_ylim([0, 1])

    ax.legend((rects_cgfp_bgp[0], rects_cgc_bgp[0], rects_sfp[0], rects_sfp_common[0]), ('CGFG-BGP', 'CGC-BGP', 'SFP', 'SFP on CGFP-BGP Reachable Flows'))
    # plt.show()
    fig.set_size_inches(6, 3.8)
    fig.savefig(name+".pdf")


if __name__ == '__main__':
    folder_path = sys.argv[1]

    plots = {}
    location = 231
    final = dict()
    for filename in [f for f in os.listdir() if f.endswith('.csv')]:
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
        generate_plots(final[filename], filename)
