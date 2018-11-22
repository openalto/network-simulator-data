#!/usr/bin/env python

import os
import json

def load_files_replicas(basedir):
    files = []
    replicas = []
    for d in os.listdir(basedir):
        d = os.path.join(basedir, d)
        if os.path.isdir(d):
            files_path = os.path.join(d, 'files.json')
            with open(files_path) as ff:
                new_files = json.load(ff)
                files.extend(new_files)

            for r in os.listdir(d):
                if r.startswith('replicas') and r.endswith('.json'):
                replicas_path = os.path.join(d, r)
                with open(replicas_path) as fr:
                    new_replicas = json.load(fr)
                    replicas.extend(new_replicas)
    return files, replicas

if __name__ == '__main__':
    import sys
    basedir = sys.argv[1]
    files, replicas = load_files_replicas(basedir)

    files_path = os.path.join(basedir, 'files.json')
    with open(files_path, 'w') as ff:
        ff.write(json.dumps(files, indent=4, sort_keys=True))

    replicas_path = os.path.join(basedir, 'replicas.json')
    with open(replicas_path, 'w') as fr:
        fr.write(json.dumps(replicas, indent=4, sort_keys=True))
