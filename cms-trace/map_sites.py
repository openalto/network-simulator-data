#!/usr/bin/env python

import json
import yaml
import random
import ipaddress

import stringdist
import numpy as np

def random_ip(prefixes):
    prefix_list = [ipaddress.ip_network(p) for p in prefixes]
    nums = [p.num_addresses for p in prefix_list]
    n = random.randint(0, sum(nums) - 1)
    for i in range(len(nums)):
        if n >= nums[i]:
            n -= nums[i]
        else:
            break
    ip = next(prefix_list[i].hosts()) + n
    return ip.exploded


if __name__ == '__main__':
    with open('simple-flows.json', 'r') as sf:
        flows = json.load(sf)
        sites = {fl[0] for fl in flows}
        sites.update({fl[1] for fl in flows})

        with open('../coreemu/LHCOne-typed.yaml', 'r') as lt:
            topo = yaml.load(lt)
            nets = [n for n in topo['nodes'] if topo['nodes'][n]['type'] == 'edge']

            site_map = {}
            for s in sites:
                dists = np.array([stringdist.rdlevenshtein_norm(s, n) for n in nets])
                i = dists.argmin()
                site_map[s] = nets[i]

            for fl in flows:
                fl[0] = random_ip(topo['nodes'][site_map[fl[0]]]['ip-prefix'])
                fl[1] = random_ip(topo['nodes'][site_map[fl[1]]]['ip-prefix'])

            with open('ip-flows.json', 'w') as ipf:
                ipf.write(json.dumps(flows, indent=4, sort_keys=True))
