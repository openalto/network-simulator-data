#!/usr/bin/env python
# Target: [(src_node, dst_node, start_time, end_time, size)]

import datetime
import json
import random
import sys
import time


def main(files_path, replicas_path):
    files = json.load(open(files_path))
    replicas = json.load(open(replicas_path))

    file_dict = dict()
    for file_obj in files:
        file_dict[file_obj["FileName"]] = file_obj

    flows = []

    count = 0
    sum = len(replicas)
    for block in replicas:
        count += 1
        print("Block: %d/%d" % (count, sum))

        for file_block in block['file']:
            if len(file_block["replica"]) < 1:
                continue
            name = file_block['name']
            file_obj = file_dict[name]
            start_time = str(datetime.datetime.now().year) + '-' + file_obj["started"]
            start_time = time.strptime(start_time, "%Y-%d-%m %H:%M:%S")
            start_time = int(time.mktime(start_time))

            end_time = str(datetime.datetime.now().year) + '-' + file_obj["finished"]
            end_time = time.strptime(end_time, "%Y-%d-%m %H:%M:%S")
            end_time = int(time.mktime(end_time))

            size = file_block["bytes"]
            dst_node = file_obj["site"]

            if len(file_block["replica"]) == 1:
                src_node = file_block["replica"][0]["node"]
                if src_node == dst_node:
                    continue
                else:
                    flows.append((src_node, dst_node, start_time, end_time, size))
            else:
                while True:
                    rand = random.randint(0, len(file_block["replica"]) - 1)
                    src_node = file_block["replica"][rand]["node"]
                    if src_node != dst_node:
                        flows.append((src_node, dst_node, start_time, end_time, size))
                        break
    return flows


if __name__ == '__main__':
    files_path = sys.argv[1]
    replicas_path = sys.argv[2]
    flows = main(files_path, replicas_path)
    for key, value in dict(zip(sys.argv[3::2], sys.argv[4::2])).items():
        flows.extend(main(key, value))
    with open("flows.json", 'w') as f:
        f.write(json.dumps(flows, indent=4, sort_keys=True))
