#!/usr/bin/env sh

for policy_type in both deflection blackhole; do
    network_ratio=0.3
    prefix_ratio=0.3
    for index in `seq 1 10`; do
        ../sfp-eval/correctness-sim.py ../coreemu/LHCOne-typed.yaml ip-flows.json 123 network_ratio=$network_ratio prefix_ratio=$prefix_ratio policy_type=$policy_type >> results/result.$network_ratio.$prefix_ratio.$policy_type.csv
    done
        network_ratio=0.5
        prefix_ratio=0.5
    for index in `seq 1 10`; do
        ../sfp-eval/correctness-sim.py ../coreemu/LHCOne-typed.yaml ip-flows.json 123 network_ratio=$network_ratio prefix_ratio=$prefix_ratio policy_type=$policy_type >> results/result.$network_ratio.$prefix_ratio.$policy_type.csv
    done
done
