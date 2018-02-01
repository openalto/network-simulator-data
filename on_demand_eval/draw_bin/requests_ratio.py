#!/usr/bin/env python

import sys

import matplotlib.pyplot as plt

from on_demand_eval.draw_bin.updates_cdf import analyze_data


def process_data(data):
    cdf = {}
    for node in data:
        fraction = data[node]['on_demands'] / data[node]['sum_flows']
        # fraction = data[node]['sum_flows'] / data[node]['on_demands']
        cdf[fraction] = cdf.get(fraction, 0) + 1
    i = 0

    keys = sorted(cdf.keys())
    for key in keys:
        cdf[key], i = (cdf[key] + i, i + cdf[key])
    for key in keys:
        cdf[key] = (cdf[key] / i)

    return cdf


def draw(cdf):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.subplots_adjust(bottom=0.15)
    keys = sorted(cdf.keys())
    X_SFP = [x for x in keys]
    Y_SFP = [cdf[x] for x in keys]

    plt.ylim((0, 1))
    # plt.xlim(1)
    # ax.set_xscale('log')
    sfp_line, = plt.plot(X_SFP, Y_SFP, color='r')
    # exact_line, = plt.plot(X_EXACT, Y_EXACT, color='b')

    return fig, ax


if __name__ == '__main__':
    site_result_folder = sys.argv[1]
    pipeline_folder = sys.argv[2]
    cdf = analyze_data(site_result_folder, pipeline_folder, func=process_data)

    fig, ax = draw(cdf)

    ax.set_xlabel("# reqeusts of maxODI / # requests of ExactMatch", fontsize=14)
    ax.set_ylabel("CDF of ASes", fontsize=14)

    # plt.show()

    fig.savefig("request-maxODI-ExactMatch.pdf")
