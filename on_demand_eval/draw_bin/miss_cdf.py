#!/usr/bin/env python3
import sys

from on_demand_eval.draw_bin.updates_cdf import analyze_data, draw

import matplotlib.pyplot as plt


def process_data(data):
    cdf_sfp = {}
    cdf_exact = {}
    for node in data:
        # fraction_sfp = data[node]['on_demands'] / data[node]['rules']
        # fraction_exact = data[node]['sum_flows'] / data[node]['rules']
        fraction_sfp = data[node]['on_demands'] / 700000
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


if __name__ == '__main__':
    site_result_folder = sys.argv[1]
    pipeline_folder = sys.argv[2]
    cdf_sfp, cdf_exact = analyze_data(site_result_folder, pipeline_folder, func=process_data)

    fig, ax = draw(cdf_sfp, cdf_exact)

    ax.set_xlabel("# reqeusts / # requests with full RIB")
    ax.set_ylabel("CDF of ASes")

    fig.savefig("maxODI-requests.pdf")
