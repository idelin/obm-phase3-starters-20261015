def dependencies(gates):
    return [set([i-1]) if i else set() for i in range(len(gates))]

def positions(mapping):
    return {logical:physical for physical,logical in enumerate(mapping)}

def available(gates,done):
    pred=dependencies(gates)
    return [i for i in range(len(gates)) if i not in done and pred[i]<=done]

def apply_swaps(mapping,edges,indices):
    result=list(mapping)
    for i in indices:
        a,b=edges[i][:2]
        result[a],result[b]=result[b],result[a]
    return result

def disjoint(actions):
    occupied=set()
    for endpoints in actions:
        if occupied.intersection(endpoints):return False
        occupied.update(endpoints)
    return True
