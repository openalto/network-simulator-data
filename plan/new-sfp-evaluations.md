# Advanced Evaluations for SFP (SDN Federation Protocol)

## Convergence Speed

Metric: SFP Convergence Time

Comparison: SFP v.s. dummy fine-grained advertisement (what’s that?) v.s. BGP

Settings: A real federation topology (e.g., LHCONE)

> TODO: approach to simulate the convergence performance of the inter-domain
> protocol.

Figures:

- Figure 1: Initial convergence
    - Description: traffic generated in some rate.
    - Y-axis: Convergence Time
    - X-axis: Scale of flows
- Figure 2: Reroute convergence
    - Description: remove some links in the topology to trigger the reroute.
    - Y-axis: Convergence Time
    - X-axis: Scale of rerouted flows

Expected result: Cannot imagine now…

Question:

- We need some insight why SFP will not convergence slowly
- How can we process the computation (composition) time? Is it reasonable to do
  somehow simulation?

Description:

- How does SFP work
- How does the dummy fine-grained advertisement work
- How does BGP work

References: D-BGP (SIGCOMM'18), SWIFT (SIGCOMM'18)

## On-Demand Latency

Metric: latency to stabilize the routes

Settings: In a real federation topology (e.g., LHCONE), considering the initial
state where each domain only has the route to their own hosts.

Comparison: On-Demand v.s. Non On-Demand

> TODO: Approach to simulate the latency as real as possible?

Figures:

- Y-axis: Average latency to fwd a packet
- X-axis: The average as-length of routes

Expected result: Cannot imagine now...

Note: To do the simulation, we need to assume some datapath latency. Why it is
reasonable? In the real system, is there any potential system issue?
