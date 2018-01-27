#!/usr/bin/env python

import csv
import glob
import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np

name_dict = {'odl': 'OpenDaylight', 'onos': 'ONOS', 'ryu': 'RYU'}
colors = ['#003366', '#993300', '#800080']


def file_info(file_path) -> (str, int):
    basename = os.path.basename(file_path)
    scale = basename.split('.')[-2]
    controller = basename.split('.')[0]
    return controller, int(scale)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s data_folder [output_folder]" % sys.argv[0])
        exit(-1)

    folder_path = sys.argv[1]
    file_paths = glob.glob(os.path.join(folder_path, "*.csv"))

    data_dict = {}  # type: dict{str, np.array} # Scale#controller -> latencies

    for file_path in file_paths:
        latencies = []
        controller, scale = file_info(file_path)
        reader = csv.reader(open(file_path), delimiter=' ')
        for line in reader:
            latencies.append((float(line[1]) - float(line[0])) * 1000)
        data_dict[str(scale) + "#" + str(controller)] = np.array(latencies)

    names = sorted(data_dict.keys())
    data = [data_dict[name] for name in names]
    show_names = ['', '10', '', '', '15', '', '', '20', '']

    fig, ax1 = plt.subplots(figsize=(9, 7))
    ax1.set_xlabel('Network scale')
    ax1.set_ylabel('Overhead latency(ms)')
    bp = plt.boxplot(data, patch_artist=True)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')
    plt.setp(ax1, xticklabels=show_names)

    # for patch, color in zip(bp['boxes'], list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in colors))):
    for patch, color in zip(bp['boxes'], colors * 3):
        patch.set(facecolor=color)

    numBoxes = 9
    medians = list(range(numBoxes))

    # legend
    plt.figtext(0.17, 0.810, "OpenDaylight", color='white', backgroundcolor=colors[0], weight='roman')
    plt.figtext(0.17, 0.765, "ONOS", color='white', backgroundcolor=colors[1], weight='roman')
    plt.figtext(0.171, 0.720, "RYU", color='white', backgroundcolor=colors[2], weight='roman')

    # plt.show()
    fig.set_size_inches(6, 3.8)

    output_filename = "reactive-ouverhead.pdf"
    if len(sys.argv) > 2:
        output_filename = os.path.join(sys.argv[2], output_filename)
    fig.savefig(output_filename)
