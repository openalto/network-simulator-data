#!/usr/bin/env python

import json

if __name__ == '__main__':
    with open("flows.json", 'r') as fl:
        flows = json.load(fl)
        simple_flows = []
        for f in flows:
            if f[0] == 'unknown' or f[1] == 'unknown':
                continue
            f[0] = f[0][3:]
            f[1] = f[1][3:]
            if f[0].endswith('_MSS'):
                f[0] = f[0][:-4]
            elif f[0].endswith('_Disk'):
                f[0] = f[0][:-5]
            elif f[0].endswith('_Buffer'):
                f[0] = f[0][:-7]
            if f[1].endswith('_MSS'):
                f[1] = f[1][:-4]
            elif f[1].endswith('_Disk'):
                f[1] = f[1][:-5]
            elif f[1].endswith('_Buffer'):
                f[1] = f[1][:-7]
            simple_flows.append(f)

        with open("simple-flows.json", 'w') as sfl:
            sfl.write(json.dumps(simple_flows, indent=4, sort_keys=True))
