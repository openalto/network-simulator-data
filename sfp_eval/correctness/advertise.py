import networkx
from pytricia import PyTricia

# FIXME: They are global variable and need to be removed
ip_prefixes = PyTricia()
global_policy = dict()  # type: dict[str, PyTricia]


def update_initial_rib(rib, prefix):
    """
    Update the initial the rib for a prefix
    """
    if prefix not in rib:
        rib[prefix] = {0: []}
    else:
        rib[prefix].update({0: []})


def initiate_ribs(G):
    """
    Initiate ribs for each network in G.
    """
    for n in G.nodes():
        for prefix in G.node[n]['ip-prefixes']:
            update_initial_rib(G.node[n]['rib'], prefix)
            # out_ribs = G.node[n]['adj-ribs-out']
            # for d in out_ribs:
            #     update_initial_rib(out_ribs[d], prefix, n)


def read_local_rib(G, curr, prefix):
    """
    Read local rib and return the next hop of a prefix. Return None if it doesn't have hop.
    """
    local_rib = G.node[curr]['rib']
    ribs_in = G.node[curr]['adj-ribs-in']
    if prefix not in local_rib:
        return None
    action = local_rib[prefix][0]
    if type(action) == list:
        return action
    if action in ribs_in:
        return ribs_in[action][prefix].get(0, None)
    return None


def advertise(G, curr, post, prefix):
    """
    Make curr node advertise routing information accepted from pre node to post node.

    G.node[curr]['rib'][prefix] + curr -> G.node[curr]['adj-ribs-out'][post][prefix]

    But we can update G.node[post]['adj-ribs-in'][curr] directly
    """
    # TODO: Consider route update later
    # print('curr: %d post: %d prefix: %s' % (curr, post, prefix))
    # print([k for k in G.neighbors(post)])
    # print(G.node[post]['adj-ribs-in'])
    post_rib_in = G.node[post]['adj-ribs-in'][curr]
    # print(dict(post_rib_in))
    if prefix not in post_rib_in:
        # G.node[curr]['adj-ribs-out'][post][prefix] = {0: G.node[curr]['rib'][prefix] + [curr]}
        # print(read_local_rib(G, curr, prefix), curr, post, prefix)
        post_rib_in[prefix] = {0: read_local_rib(G, curr, prefix) + [curr]}
    else:
        if prefix not in G.node[curr]['rib']:
            post_rib_in.delete(prefix)
        else:
            post_rib_in[prefix][0] = read_local_rib(G, curr, prefix) + [curr]
    # print(dict(post_rib_in))


def withdraw(G, curr, post, prefix):
    """
    """
    post_rib_in = G.node[post]['adj-ribs-in'][curr]
    if prefix in post_rib_in:
        # if post == 59 and curr in [29]:
        #     print('!!!Withdraw:', post, curr, prefix)
        # post_rib_in.delete(prefix)
        G.node[post]['adj-ribs-in'][curr].delete(prefix)
        if prefix in G.node[post]['rib']:
            if G.node[post]['rib'][prefix][0] == curr:
                del G.node[post]['rib'][prefix]
            else:
                ports = list(G.node[post]['rib'][prefix].keys())
                for port in ports:
                    if G.node[post]['rib'][prefix][port] == curr:
                        del G.node[post]['rib'][prefix][port]
        # if post == 59 and curr in [29]:
        #     print('!!!RIB_IN:', dict(G.node[59]['adj-ribs-in'][29]))


def correct_bgp_advertise(G):
    """
    Correct BGP Advertisement:
        If the internal fine-grained policy differs from the selected best BGP route,
        do not advertise such a destination IP prefix.
    """
    # Update adj-ribs-out (Unnecessary)
    # Update neighbor's adj-ribs-in
    for n in G.nodes():
        local_rib = G.node[n]['rib']
        # Scan whether prefix in cus tomer neighbors
        for prefix in local_rib:
            # If local_rib has internal fine-grained policy differ from port 0, withdraw.
            if len(set([x if x != [] else () for x in local_rib[prefix].values()])) > 1:
                for d in G.neighbors(n):
                    # if n == 29 or n == 30:
                    #     print("DEBUG:", n, d, prefix)
                    withdraw(G, n, d, prefix)
                continue
            # If so, advertise the local route (w/o fine-grained) to all other neighbors
            # else only advertise to customers
            last_hop = local_rib[prefix][0] or None
            if local_rib[prefix][0] == []:
                for d in G.neighbors(n):
                    advertise(G, n, d, prefix)
            if last_hop in G.node[n]['customers']:
                for d in G.neighbors(n):
                    if d != last_hop:
                        advertise(G, n, d, prefix)
            else:
                for c in G.node[n]['customers']:
                    advertise(G, n, c, prefix)
    # print('=====>', dict(G.node[59]['adj-ribs-in'][29]))
    # print(dict(G.node[59]['adj-ribs-in'][30]))
    # Update local-rib
    for n in G.nodes():
        # Compose rib_in into local rib
        # Principle: customer > provider/peer, shorter_as_path > longer_as_path
        compose_ribs_in(G, n)
        # Check whether there are local policies can be activated.
        enable_local_policy(G, n)
    # print('<======', dict(G.node[59]['adj-ribs-in'][29]))
    # print(dict(G.node[59]['adj-ribs-in'][30]))
    # report_rib(G, 59)


def fp_bgp_advertise(G):
    """
    False-Positive BGP Advertisement:
        Always advertise the destination IP prefix based routes regardless of
        the network's internal fine-grained flow based policies.
    """
    # Update adj-ribs-out
    # Update neighbor's adj-ribs-in
    for n in G.nodes():
        local_rib = G.node[n]['rib']
        # Scan whether prefix in customer neighbors
        for prefix in local_rib:
            #   if so, advertise the local route (w/o fine-grained) to all other neighbors
            #   else only advertise to customers
            last_hop = local_rib[prefix][0] or None
            if local_rib[prefix][0] == []:
                for d in G.neighbors(n):
                    advertise(G, n, d, prefix)
            if last_hop in G.node[n]['customers']:
                for d in G.neighbors(n):
                    if d != last_hop:
                        advertise(G, n, d, prefix)
            else:
                for c in G.node[n]['customers']:
                    advertise(G, n, c, prefix)
    # Update local-rib
    for n in G.nodes():
        # Compose rib_in into local rib
        # Principle: customer > provider/peer, shorter_as_path > longer_as_path
        compose_ribs_in(G, n)
        # Check whether there are local policies can be activated.
        enable_local_policy(G, n)


def sfp_advertise(G):
    """
    SFP Advertisement:
        Always advertise valid fine-grained routing information.
    """
    for n in G.nodes():
        local_rib = G.node[n]['rib']
        for prefix in local_rib:
            pass


def get_last_hop(path):
    return path[-1] if path else None


def best_choice(G, n, *actions):
    best = 0
    customers = G.node[n]['customers']
    for i in range(1, len(actions)):
        act = actions[i]
        best_act = actions[best]
        if not act:
            continue
        if (get_last_hop(act) in customers) > (get_last_hop(best_act) in customers):
            best = i
        elif (get_last_hop(act) in customers) == (get_last_hop(best_act) in customers):
            if not best_act or len(act) < len(best_act):
                best = i
    # print(actions, best)
    return best


def compose_ribs_in(G, n):
    """
    Compose rib_in into local rib.

    Principle:
        customer > provider/peer,
        shorter_as_path > longer_as_path.
    """
    ribs_in = G.node[n]['adj-ribs-in']
    local_rib = G.node[n]['rib']
    for d in ribs_in:
        curr_rib_in = ribs_in[d]
        for prefix in curr_rib_in:
            if prefix not in local_rib:
                local_rib[prefix] = {0: None}
            for port in curr_rib_in[prefix]:
                # print(n, d)
                # local_rib[prefix][port] = best_choice(G, n, curr_rib_in[prefix][port],
                #                                       local_rib[prefix].get(port, None))
                curr_act = curr_rib_in[prefix][port]
                # print(n, d, prefix, port, curr_act)
                if not best_choice(G, n, curr_act, read_local_rib(G, n, prefix)) and curr_act:
                    local_rib[prefix][port] = d
    # report_rib(G, n)


def enable_local_policy(G, n):
    """
    Check whether there are local policies can be activated.
    """
    local_policy = G.node[n]['local_policy']
    for prefix in local_policy:
        if prefix not in G.node[n]['rib']:
            continue
        for port in local_policy[prefix]:
            next_hop = local_policy[prefix][port]
            if not next_hop:
                G.node[n]['rib'][prefix][port] = None
            rib_in = G.node[n]['adj-ribs-in'].get(next_hop, [])
            if prefix in rib_in:
                G.node[n]['rib'][prefix][port] = next_hop
            #     G.node[n]['rib'][prefix][port] = rib_in[prefix].get(port,
            #                                                         rib_in[prefix].get(0, None))
            # G.node[n]['rib'][prefix][port] = next_hop


def common_advertise(G, advertise=advertise):
    # Update adj-ribs-out
    # Update neighbor's adj-ribs-in
    for n in G.nodes():
        local_rib = G.node[n]['rib']
        # Scan whether prefix in customer neighbors
        for prefix in local_rib:
            #   if so, advertise the local route (w/o fine-grained) to all other neighbors
            #   else only advertise to customers
            last_hop = local_rib[prefix][0] or None
            if local_rib[prefix][0] == []:
                for d in G.neighbors(n):
                    advertise(G, n, d, prefix)
            if last_hop in G.node[n]['customers']:
                for d in G.neighbors(n):
                    if d != last_hop:
                        advertise(G, n, d, prefix)
            else:
                for c in G.node[n]['customers']:
                    advertise(G, n, c, prefix)
    # Update local-rib
    for n in G.nodes():
        # Compose rib_in into local rib
        # Principle: customer > provider/peer, shorter_as_path > longer_as_path
        compose_ribs_in(G, n)
        # Check whether there are local policies can be activated.
        enable_local_policy(G, n)


# For DEBUG Use
def report_rib(G, n=None):
    if n:
        print('>>>', n, dict(G.node[n]['rib']))
        return
    for n in G.nodes():
        print('>>>', n, dict(G.node[n]['rib']))


def report_local_policy(G, n=None):
    if n:
        print('<<<', n, dict(G.node[n]['local_policy']))
        return
    for n in G.nodes():
        print('<<<', n, dict(G.node[n]['local_policy']))


def fp_bgp_convergence(G):
    """
    False-positive BGP Convergence. node["routing"] is the table of  {ip-prefix -> next hop node}
    """
    paths = networkx.shortest_path(G)
    for src in G.nodes:
        for dst in G.nodes:
            if src != dst:
                try:
                    path = paths[src].get(dst)
                except KeyError:
                    path = None
                if path:
                    prefixes = G.node[dst]['ip-prefix']
                    for hop, next_hop in zip(path[:-1], path[1:]):
                        for prefix in prefixes:
                            G.node[hop]["routing"][prefix] = next_hop


def all_fg_nodes(G, prefix):
    """
    Let's assume the local_policy is generated from the prefixes of nodes first.
    """
    # FIXME: If the granularity of prefixes in local_policy is different from ones in node, it will conduct error.
    fg_nodes = []
    for node in G.nodes:
        local = get_local_policy(node)
        if local.get(prefix):
            fg_nodes.append(node)
    return fg_nodes


def correct_bgp_convergence(G):
    """
    Correct BGP Convergence
    """
    for dst in G.nodes:
        prefixes = G.node[dst]['ip-prefix']
        for prefix in prefixes:
            H = G.copy()
            for node in all_fg_nodes(G, prefix):
                H.remove_node(node)
            paths = networkx.shortest_path(H)
            for src in H.nodes:
                if src != dst:
                    # path = paths[src][dst]
                    path = paths[src].get(dst, [])
                    for hop, next_hop in zip(path[:-1], path[1:]):
                        G.node[hop]["routing"][prefix] = next_hop


def find_fine_grained_routes(G, prefix_port):
    for prefix, ports in prefix_port.items():
        for port in ports:
            delete_nodes = set()
            delete_links = set()
            H = G.copy()  # A copy of directed graph to modify links and nodes
            # Step 1: Remove unused links for <prefix, port>
            for node in H.nodes:
                action = get_local_policy(node).get(prefix)
                if action and (port in action):
                    action = action[port]
                    if action:
                        for neig in H.neighbors(node):
                            if action != neig:
                                delete_links.add((node, neig))
                    else:
                        delete_nodes.add(node)
            for edge in delete_links:
                H.remove_edge(*edge)
            for node in delete_nodes:
                H.remove_node(node)
            # Step 2: Find shortest path (Is it possible to be not found?)
            dst = ip_prefixes[prefix]
            paths = networkx.shortest_path(H, target=dst)
            # Step 3: Traverse the shortest path
            for src in H.nodes:
                if src != dst:
                    path = paths.get(src)
                    if path:
                        for hop, next_hop in zip(path[:-1], path[1:]):
                            if prefix not in G.node[hop]["fine_grained"]:
                                G.node[hop]["fine_grained"][prefix] = dict()
                            G.node[hop]["fine_grained"][prefix][port] = next_hop

    # Step 4: BGP shortest path in all nodes
    fp_bgp_convergence(G)
    return G


def fine_grained_convergence(G):
    # TODO
    pass


def fine_grained_announcement(G):
    for node in G.nodes:
        del G.node[node]["routing"]
        del G.node[node]["fine_grained"]
    G = G.to_directed()
    for node in G.nodes:
        G.node[node]["routing"] = PyTricia()
        G.node[node]["fine_grained"] = PyTricia()
    prefix_port = dict()  # type: dict[str, set[int]]
    for node in G.nodes:
        local = get_local_policy(node)
        for prefix in local:
            ports_actions = local[prefix]
            if prefix not in prefix_port:
                prefix_port[prefix] = set()
            for port in ports_actions:
                prefix_port[prefix].add(port)
    return find_fine_grained_routes(G, prefix_port)
