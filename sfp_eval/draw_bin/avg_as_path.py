#!/usr/bin/env python

import csv
import glob
import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np

from sfp_eval.draw_bin.flow_loss_stat import Result

colors = ['#003366', '#993300', '#800080']


def file_info(file_path) -> (str, int):
    basename = os.path.basename(file_path)
    scale = basename.split('.')[-3]
    print(scale)
    return int(scale)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s data_folder [output_folder]" % sys.argv[0])
        exit(-1)

    policy_types = ['bh']

    for policy_type in policy_types:

        folder_path = sys.argv[1]
        file_paths = glob.glob(os.path.join(folder_path, "*.%s.csv" % policy_type))

        data_dict = {}  # type: dict[int, dict[str, list[int]]]

        for file_path in file_paths:
            scale = file_info(file_path)
            if scale not in data_dict:
                data_dict[scale] = dict()
            reader = csv.reader(open(file_path), delimiter='\t')
            count = 0
            for line in reader:
                if count % 4 == 3:
                    count += 1
                    continue
                elif count % 4 == 0:
                    name = 'CGFP-BGP'
                elif count % 4 == 1:
                    name = 'CGC-BGP'
                elif count % 4 == 2:
                    name = 'SFP'

                count += 1
                if name not in data_dict[scale]:
                    data_dict[scale][name] = list()
                data_dict[scale][name].append(Result(line).avg_as_path())

        data = {
            "a#CGFP-BGP#3": np.asarray(data_dict[3]['CGFP-BGP']),
            "b#CGC-BGP#3": np.asarray(data_dict[3]['CGC-BGP']),
            "c#SFP#3": np.asarray(data_dict[3]['SFP']),
            "d#CGFP-BGP#3": np.asarray(data_dict[5]['CGFP-BGP']),
            "e#CGC-BGP#3": np.asarray(data_dict[5]['CGC-BGP']),
            "f#SFP#3": np.asarray(data_dict[5]['SFP']),
            "g#CGFP-BGP#3": np.asarray(data_dict[7]['CGFP-BGP']),
            "h#CGC-BGP#3": np.asarray(data_dict[7]['CGC-BGP']),
            "i#SFP#3": np.asarray(data_dict[7]['SFP']),
            "j#CGFP-BGP#3": np.asarray(data_dict[9]['CGFP-BGP']),
            "k#CGC-BGP#3": np.asarray(data_dict[9]['CGC-BGP']),
            "l#SFP#3": np.asarray(data_dict[9]['SFP']),
        }

        names = sorted(data.keys())
        data = [data[name] for name in names]
        show_names = ['', '30%', '', '', '50%', '', '', '70%', '', '', '90%', '']

        fig, ax1 = plt.subplots(figsize=(9, 7))
        ax1.set_xlabel('Policy numbers')
        ax1.set_ylabel('Length of AS path')
        bp = plt.boxplot(data, patch_artist=True)
        plt.setp(bp['boxes'], color='black')
        plt.setp(bp['whiskers'], color='black')
        plt.setp(bp['fliers'], color='red', marker='+')
        plt.setp(ax1, xticklabels=show_names)

        # for patch, color in zip(bp['boxes'], list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in colors))):
        for patch, color in zip(bp['boxes'], colors * 4):
            patch.set(facecolor=color)

        numBoxes = 9
        medians = list(range(numBoxes))

        # legend
        plt.figtext(0.17, 0.310, "CGFP-BGP", color='white', backgroundcolor=colors[0], weight='roman')
        plt.figtext(0.17, 0.245, "CGC-BGP", color='white', backgroundcolor=colors[1], weight='roman')
        plt.figtext(0.171, 0.180, "SFP", color='white', backgroundcolor=colors[2], weight='roman')

        # plt.show()
        fig.set_size_inches(7, 4.8)

        output_filename = "average-as-path.%s.pdf" % policy_type
        if len(sys.argv) > 2:
            output_filename = os.path.join(sys.argv[2], output_filename)
        fig.savefig(output_filename)
