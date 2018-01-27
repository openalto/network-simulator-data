import networkx
from pytricia import PyTricia

# FIXME: They are global variable and need to be removed
ip_prefixes = PyTricia()
global_policy = dict()  # type: dict[str, PyTricia]


def update_initial_rib(rib, prefix, overwrite=True):
    """
    Update the initial the rib for a prefix
    """
    if overwrite or prefix not in rib:
        rib[prefix] = {0: []}
    else:
        rib[prefix].update({0: []})


def initiate_ribs(G, overwrite=True):
    """
    Initiate ribs for each network in G.
    """
    for n in G.nodes():
        for prefix in G.node[n]['ip-prefixes']:
            update_initial_rib(G.node[n]['rib'], prefix, overwrite)
            # out_ribs = G.node[n]['adj-ribs-out']
            # for d in out_ribs:
            #     update_initial_rib(out_ribs[d], prefix, n)
        if overwrite:
            G.node[n]['adj-ribs-in'] = {n: PyTricia() for n in G.neighbors(n)}
            G.node[n]['adj-ribs-out'] = {n: PyTricia() for n in G.neighbors(n)}


def read_local_rib(G, curr, prefix, port=0):
    """
    Read local rib and return the next hop of a prefix. Return None if it doesn't have hop.
    """
    # FIXME: This function is duplicate with default_routing_policy() in route.py
    local_rib = G.node[curr]['rib']
    ribs_in = G.node[curr]['adj-ribs-in']
    if prefix not in local_rib:
        return None
    prefix_actions = local_rib[prefix]
    action = prefix_actions.get(port, prefix_actions.get(0, None))
    if type(action) == list:
        return action
    if action in ribs_in:
        rib_in_prefix_actions = ribs_in[action][prefix]
        return rib_in_prefix_actions.get(port, rib_in_prefix_actions.get(0, None))
    return None


def legacy_advertise(G, curr, post, prefix):
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
    elif prefix not in G.node[curr]['rib']:
        post_rib_in.delete(prefix)
    else:
        post_rib_in[prefix][0] = read_local_rib(G, curr, prefix) + [curr]
    # print(dict(post_rib_in))


def is_all_block(actions):
    """
    Test if actions for all ports are block.
    """
    for port in actions:
        if actions[port] is not None:
            return False
    return True


def advertise(G, curr, post, prefix, port=0):
    """
    """
    # TODO: Try to make it compatible with coarse-grained advertisement
    post_rib_in = G.node[post]['adj-ribs-in'][curr]
    action = read_local_rib(G, curr, prefix, port)
    if prefix not in post_rib_in:
        post_rib_in[prefix] = {}
    post_rib_in[prefix][port] = action + [curr] if validate(action) else None

    if is_all_block(post_rib_in[prefix]):
        post_rib_in.delete(prefix)


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
        compose_ribs_in(G, n)
        enable_local_policy(G, n)
        local_rib = G.node[n]['rib']
        for prefix in local_rib:
            for port in local_rib[prefix]:
                if port == 0:
                    # Advertise by following as relationship
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
                else:
                    # Do not follow as relationship
                    for d in G.neighbors(n):
                        advertise(G, n, d, prefix, port)
    # report_rib(G, 29)
    # report_rib(G, 30)


def get_last_hop(path):
    return path[-1] if path else None


def best_choice(G, n, port, *actions):
    best = 0
    customers = G.node[n]['customers']
    for i in range(1, len(actions)):
        act = actions[i]
        best_act = actions[best]
        if not act:
            continue
        if port == 0:
            # Follow as-relationship
            if (get_last_hop(act) in customers) > (get_last_hop(best_act) in customers):
                best = i
            elif (get_last_hop(act) in customers) == (get_last_hop(best_act) in customers):
                if not best_act or len(act) < len(best_act):
                    best = i
        elif not best_act or len(act) < len(best_act):
            # Do not follow as-relationship
            best = i
    # print(actions, best)
    return best


def validate(action, n=None):
    """
    Validate whether it is a valid non-block action
    """
    if action is None:
        return False
    else:
        return n not in action


def remove_invalid_local_rib(G, n):
    """
    """
    local_rib = G.node[n]['rib']
    ribs_in = G.node[n]['adj-ribs-in']
    for prefix in local_rib:
        prefix_actions = local_rib[prefix]
        ports = list(prefix_actions.keys())
        for port in ports:
            action = prefix_actions[port]
            if action:
                if action not in ribs_in:
                    del prefix_actions[port]
                elif prefix not in ribs_in[action]:
                    del prefix_actions[port]
                elif ribs_in[action][prefix].get(port, ribs_in[action][prefix].get(0, None)) is None:
                    del prefix_actions[port]
        if is_all_block(prefix_actions):
            local_rib.delete(prefix)


def compose_ribs_in(G, n):
    """
    Compose rib_in into local rib.

    Principle:
        customer > provider/peer,
        shorter_as_path > longer_as_path.
    """
    # TODO: How to handle invalid local rib entries?
    ribs_in = G.node[n]['adj-ribs-in']
    local_rib = G.node[n]['rib']
    for d in ribs_in:
        curr_rib_in = ribs_in[d]
        for prefix in curr_rib_in:
            if prefix not in local_rib:
                local_rib[prefix] = {0: None}
            for port in curr_rib_in[prefix]:
                curr_act = curr_rib_in[prefix][port]
                if best_choice(G, n, port, read_local_rib(G, n, prefix), curr_act) and validate(curr_act, n):
                    local_rib[prefix][port] = d
    # Walk through local_rib to delete invalid entry?
    # The invalid entry means the next_hop rib_in no longer has a route.
    remove_invalid_local_rib(G, n)
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
            if prefix in rib_in and validate(rib_in[prefix].get(port, rib_in[prefix].get(0, None)), n):
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
def report_rib(G, n=None, table='rib', neigh=None):
    if n:
        print(table, '>>>', n, dict(G.node[n][table][neigh]) if neigh else dict(G.node[n][table]))
        return
    for n in G.nodes():
        print(table, '>>>', n, dict(G.node[n][table][neigh]) if neigh else dict(G.node[n][table]))


def report_local_policy(G, n=None):
    if n:
        print('<<<', n, dict(G.node[n]['local_policy']))
        return
    for n in G.nodes():
        print('<<<', n, dict(G.node[n]['local_policy']))
