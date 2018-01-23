#!/usr/bin/env sh

for policy_type in both deflection blackhole; do
    network_ratio=$1
    prefix_ratio=$1
    for index in `seq 1 10`; do
        ../sfp-eval/correctness-sim.py ../coreemu/LHCOne-typed.yaml ip-flows.json 1234 network_ratio=$network_ratio prefix_ratio=$prefix_ratio policy_type=$policy_type >> results/result.$network_ratio.$prefix_ratio.$policy_type.csv
    done
done
