# Advanced Evaluations for SFP (SDN Federation Protocol)

## Convergence Speed

Metric: SFP Convergence Time

Comparison: SFP v.s. dummy fine-grained advertisement (what’s that?) v.s. BGP

Settings: A real federation topology (e.g., LHCONE)

Figures:

- Y-axis: Convergence Time
- X-axis: Scale of flows

Expected result: Cannot imagine now…

Question: We need some insight why SFP will not convergence slowly

Description:

- How does SFP work
- How does the dummy fine-grained advertisement work
- How does BGP work

## On-Demand Latency

Metric: latency to stabilize the routes

Settings: In a real federation topology (e.g., LHCONE), considering the initial
state where each domain only has the route to their own hosts.

Comparison: On-Demand v.s. Non On-Demand

Figures:

- Y-axis: Average latency to fwd a packet
- X-axis: The average as-length of routes

Expected result: Cannot imagine now...

Note: To do the simulation, we need to assume some datapath latency. Why it is
reasonable? In the real system, is there any potential system issue?
