#!/usr/bin/env python
import sys

from sfp_eval.correctness.session import session_start

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(
            "Usage: %s topo_filepath flow_filepath relations_filepath [arg=value]\n"
        )
        print("arg: policy_type")
        exit(-1)

    topo_filepath = sys.argv[1]
    flow_filepath = sys.argv[2]
    relations_filepath = sys.argv[3]
    args = dict([arg.split('=') for arg in sys.argv[4:]])  # type: dict[str, str]

    session_start(topo_filepath, flow_filepath, relations_filepath, *args)
