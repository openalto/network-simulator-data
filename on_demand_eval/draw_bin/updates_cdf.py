#!/usr/bin/env python
import csv
import json
import os
import sys
from glob import glob

import matplotlib
import matplotlib.pyplot as plt


class OnDemandData(object):
    def __init__(self, line=None):
        if line is None:
            self.src_ip = "0.0.0.0",
            self.dst_ip = "0.0.0.0",
            self.src_port = 0,
            self.dst_port = 0,
            self.protocol = "TCP",
            self.updates = 0,
            self.miss_num = 0,
            self.sum_num = 0
            self.miss_vol = 0,
            self.sum_vol = 0
        else:
            self.src_ip = line[0]
            self.dst_ip = line[1]
            self.src_port = int(line[2])
            self.dst_port = int(line[3])
            self.protocol = line[4]
            self.updates = int(line[5])
            self.miss_num = int(line[6])
            self.sum_num = int(line[7])
            self.miss_vol = int(line[8])
            self.sum_vol = int(line[9])


def get_srcs_updates_and_ondemands(srcs_data):
    srcs_updates_and_ondemands = {}
    for src in srcs_data.keys():
        sum_updates = 0
        for on_demand in srcs_data[src]['data']:
            if on_demand is None:
                continue
            sum_updates += on_demand.updates
        srcs_updates_and_ondemands[src] = {
            "updates": sum_updates,
            "on_demands": srcs_data[src]["sum_on_demands"],
            "rules": srcs_data[src]["rule_num"],
            "sum_flows": srcs_data[src]["sum_flows"]
        }
        results = dict()
        for src in srcs_updates_and_ondemands:
            if srcs_updates_and_ondemands[src]['updates'] != 0:
                results[src] = srcs_updates_and_ondemands[src]
    return results


def pipeline_rule_number(pipeline_file_path):
    obj = json.load(open(pipeline_file_path))
    return sum([len(table["rules"]) for table in obj["tables"]])


def analyze_data(ondemands_folder, pipelines_folder, func):
    srcs_data = {}

    filepaths = glob(os.path.join(ondemands_folder, "*.csv"))
    basenames = [os.path.basename(filepath) for filepath in filepaths]

    for basename in basenames:
        src = int(basename.split('_')[0])
        if src in srcs_data:
            continue

        dst = int(basename.split('_')[1])
        dst_pipeline_path = os.path.join(pipelines_folder, "pipeline-%d.json" % dst)
        srcs_data[src] = {
            "data": [None],
            "sum_flows": 0,
            "sum_on_demands": 0,
            "on_demand_vol": 0,
            "sum_vol": 0,
            "rule_num": pipeline_rule_number(dst_pipeline_path)
        }

        reader = csv.reader(open(os.path.join(ondemands_folder, basename)), delimiter='\t')
        for line in reader:
            if len(line) > 4:
                srcs_data[src]["data"].append(OnDemandData(line))
            else:
                srcs_data[src]["sum_on_demands"] = int(line[0])
                srcs_data[src]["sum_flows"] = int(line[1])
                srcs_data[src]["on_demand_vol"] = int(line[2])
                srcs_data[src]["sum_vol"] = int(line[3])

    return func(get_srcs_updates_and_ondemands(srcs_data))


def process_data(data):
    cdf_sfp = {}
    cdf_exact = {}
    for node in data:
        # fraction_sfp = data[node]['updates'] / data[node]['rules']
        # fraction_exact = data[node]['sum_flows'] / data[node]['rules']
        fraction_sfp = data[node]['updates'] / 700000
        fraction_exact = data[node]['sum_flows'] / 700000
        cdf_sfp[fraction_sfp] = cdf_sfp.get(fraction_sfp, 0) + 1
        cdf_exact[fraction_exact] = cdf_exact.get(fraction_exact, 0) + 1
    i = 0
    j = 0
    keys = sorted(cdf_sfp.keys())
    for key in keys:
        cdf_sfp[key], i = (cdf_sfp[key] + i, i + cdf_sfp[key])
    for key in keys:
        cdf_sfp[key] = (cdf_sfp[key] / i)

    keys = sorted(cdf_exact.keys())
    for key in keys:
        cdf_exact[key], j = (cdf_exact[key] + j, j + cdf_exact[key])
    for key in keys:
        cdf_exact[key] = (cdf_exact[key] / j)

    return cdf_sfp, cdf_exact


def cdf_to_array(cdf):
    arr = []
    for key in cdf:
        for i in range(len(cdf)):
            arr.append(key)
    return arr


def draw(cdf_sfp, cdf_exact):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    fig.subplots_adjust(bottom=0.15)
    keys = sorted(cdf_sfp.keys())
    X_SFP = [x for x in keys]
    Y_SFP = [cdf_sfp[x] for x in keys]

    keys = sorted(cdf_exact.keys())
    X_EXACT = [x for x in keys]
    Y_EXACT = [cdf_exact[x] for x in keys]
    plt.ylim((0, 1))
    # plt.xlim(1)
    ax.set_xscale('log')
    sfp_line, = plt.plot(X_SFP, Y_SFP, color='r')
    exact_line, = plt.plot(X_EXACT, Y_EXACT, color='b')
    # matplotlib.rc("font", size=22)

    ax.legend([sfp_line, exact_line], ["maxODI", "ExactMatch"])

    return fig, ax


if __name__ == '__main__':
    site_result_folder = sys.argv[1]
    pipeline_folder = sys.argv[2]
    cdf_sfp, cdf_exact = analyze_data(site_result_folder, pipeline_folder, func=process_data)

    fig, ax = draw(cdf_sfp, cdf_exact)

    ax.set_xlabel("# rules / # rules with full RIB", fontsize=12)
    ax.set_ylabel("CDF of ASes", fontsize=12)

    plt.show()

    # fig.savefig("maxODI-rules.pdf")
