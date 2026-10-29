"""Finite positive AND/OR closure. Costs are a ranking heuristic, not learning difficulty."""
from collections import defaultdict
from heapq import heappop, heappush


def closure(clauses, known):
    reverse=defaultdict(list)
    edges=[]
    remaining=[]
    total=[]
    for head, alternatives in clauses.items():
        for i, body in enumerate(alternatives):
            # A repeated prerequisite must be satisfied only once.
            deps=list(dict.fromkeys(body))
            n=len(edges)
            edges.append((head,i))
            remaining.append(len(deps))
            total.append(1)
            for dep in deps: reverse[dep].append(n)
    heap=[]
    for node in set(known): heappush(heap,(0,node))
    for j,(head,_) in enumerate(edges):
        if not remaining[j]: heappush(heap,(1,head))
    costs={}
    while heap:
        cost,node=heappop(heap)
        if node in costs: continue
        costs[node]=cost
        for j in reverse.get(node,()):
            remaining[j]-=1
            total[j]+=cost
            if remaining[j]==0: heappush(heap,(total[j],edges[j][0]))
    return costs


def rank_alternatives(alternatives, costs):
    out=[]
    for i,body in enumerate(alternatives):
        deps=list(dict.fromkeys(body))
        missing=[x for x in deps if x not in costs]
        score=1+sum(costs[x] for x in deps if x in costs)
        out.append({'index':i,'complete':not missing,'missing':missing,'cost':score})
    return sorted(out,key=lambda x:(not x['complete'],len(x['missing']),x['cost'],x['index']))
