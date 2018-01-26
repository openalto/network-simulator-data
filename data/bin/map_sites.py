#!/usr/bin/env python

import sys
import ipaddress
import json
import random

import numpy as np
from scipy.stats import gaussian_kde
import stringdist
import yaml
from matplotlib import pyplot as plt


def random_ip(prefixes):
    prefix_list = [ipaddress.ip_network(p) for p in prefixes]
    nums = [p.num_addresses - 1 for p in prefix_list]
    n = random.randint(0, sum(nums) - 1)
    for i in range(len(nums)):
        if n >= nums[i]:
            n -= nums[i]
        else:
            break
    ip = next(prefix_list[i].hosts()) + n
    return ip.exploded


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: %s simple-flows topology ip-flows [flow-stat]" % sys.argv[0])
        sys.exit(0)
    with open(sys.argv[1], 'r') as sf:
        flows = json.load(sf)
        sites = {fl[0] for fl in flows}
        sites.update({fl[1] for fl in flows})

        with open(sys.argv[2], 'r') as lt:
            topo = yaml.load(lt)
            nets = [n for n in topo['nodes'] if topo['nodes'][n]['type'] == 'edge']

            site_map = {}
            for s in sites:
                dists = np.array([stringdist.rdlevenshtein_norm(s, n) for n in nets])
                i = dists.argmin()
                site_map[s] = nets[i]

            traffic_flows = [{'src_ip': random_ip(topo['nodes'][site_map[fl[0]]]['ip-prefixes']),
                              'dst_ip': random_ip(topo['nodes'][site_map[fl[1]]]['ip-prefixes']),
                              'start_time': fl[2],
                              'end_time': fl[3],
                              'volume': fl[4]} for fl in flows]

            if len(sys.argv) > 4:
                src_sites = [topo['nodes'][site_map[fl[0]]]['id'] for fl in flows]
                dst_sites = [topo['nodes'][site_map[fl[1]]]['id'] for fl in flows]
                density = np.vstack([src_sites, dst_sites])
                z = gaussian_kde(density)(density)
                plt.figure(figsize=(20, 10), dpi=600)
                plt.xticks(sorted([topo['nodes'][n]['id'] for n in nets]))
                plt.yticks(sorted([topo['nodes'][n]['id'] for n in nets]))
                plt.scatter(src_sites, dst_sites, c=z, s=50, edgecolor='')
                plt.colorbar()
                plt.savefig(sys.argv[4])

            with open(sys.argv[3], 'w') as ipf:
                ipf.write(json.dumps(traffic_flows, indent=4, sort_keys=True))
