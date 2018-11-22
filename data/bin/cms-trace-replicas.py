#!/usr/bin/env python

import json
import sys
from multiprocessing import Pool

import requests


def get_all_replicas(filenames, start=0):
    count = 0
    sum = len(filenames)
    replicas = []

    results = Pool(200).imap_unordered(fetch_replica, filenames)
    for filename, part_replicas, error in results:
        count += 1

        if count <= start:
            continue

        if error is None:
            replicas.extend(part_replicas)

            print("File names: %d/%d" % (count, sum))
        else:
            print("error fetching file name: %s" % filename)
            print(error)

        if count % 10000 == 0:
            s = json.dumps(replicas, indent=4, sort_keys=True)
            with open("replicas-part-%d.json" % int(count / 10000), 'w') as f:
                f.write(s)
            replicas = []

        if count == sum:
            break

    return replicas


def fetch_replica(filename):
    try:
        url = "http://cmsweb.cern.ch/phedex/datasvc/json/prod/filereplicas?lfn=%s" % filename
        resp = requests.get(url, headers={"Accept": "application/json"}, verify=False)
        content = json.loads(resp.content)["phedex"]["block"]
        return filename, content, None
    except Exception as e:
        return filename, None, e


def main(filename):
    file_objs = json.load(open(filename))
    filenames = [file["FileName"] for file in file_objs]
    filenames = set(filenames)
    print("File names: %d" % len(filenames))

    replicas = get_all_replicas(filenames, start=0 if len(sys.argv) < 3 else int(sys.argv[2]))

    with open("replicas-rest.json", 'w') as f:
        f.write(json.dumps(replicas, indent=4, sort_keys=True))


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
