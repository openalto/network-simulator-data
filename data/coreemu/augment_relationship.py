#!/usr/bin/env python

import sys
import yaml


def augment_relationship(origin, relation):
    nodes = origin['nodes'].keys()
    ids = [origin['nodes'][n]['id'] for n in nodes]
    for n in nodes:
        origin['nodes'][n]['customers'] = [d for d in relation['nodes'][n]['customers'] if d in ids]
        origin['nodes'][n]['providers'] = [d for d in relation['nodes'][n]['providers'] if d in ids]
        origin['nodes'][n]['peers'] = [d for d in relation['nodes'][n]['peers'] if d in ids]
    return origin


routers = {
    2: [18, 19, 20, 21, 22],
    3: [23, 24],
    4: [23, 24],
    5: [23, 24],
    6: [24, 25],
    7: [25],
    8: [26, 57],
    9: [23, 24, 27, 28, 29],
    10: [29],
    11: [30, 31,32, 33, 34, 35, 36],
    12: [34, 35, 36, 37, 38, 39],
    13: [40],
    14: [40],
    15: [41]
}


customers =  [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 57]


if __name__ == '__main__':
    # topo_aug = {}
    # with open(sys.argv[1], 'r') as f1:
    #     topo_with_re = yaml.load(f1)
    #     with open(sys.argv[2], 'r') as f2:
    #         topo_origin = yaml.load(f2)
    #         topo_aug = augment_relationship(topo_origin, topo_with_re)

    # with open(sys.argv[3], 'w') as f3:
    #     yaml.dump(topo_aug, f3)
    with open(sys.argv[1], 'r') as f:
        topo = yaml.load(f)

    name_map = {n['id']: n['name'] for n in topo['nodes'].values()}
    topo['nodes'][name_map[1]]['customers'] = list(routers.keys())

    for c in customers:
        topo['nodes'][name_map[c]]['providers'].remove(1)
        topo['links'].remove([c, 1])

    for r in routers:
        name = 'router-%d' % r
        topo['nodes'][name] = {
            'asn': 900000 + r,
            'customers': routers[r],
            'id': r,
            'ip': None,
            'ip-prefixes': [],
            'name': name,
            'peers': [],
            'providers': [1],
            'type': 'transit'
        }
        topo['links'].append([1, r])
        for c in routers[r]:
            topo['nodes'][name_map[c]]['providers'].append(r)
            topo['links'].append([r, c])

    with open(sys.argv[1], 'w') as f:
        yaml.dump(topo, f)

