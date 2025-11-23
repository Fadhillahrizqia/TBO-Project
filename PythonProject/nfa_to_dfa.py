# nfa_to_dfa.py
from collections import deque

def epsilon_closure(states, transitions):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for t in transitions.get((s, ''), []):
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure

def move(states, symbol, transitions):
    res = set()
    for s in states:
        for t in transitions.get((s, symbol), []):
            res.add(t)
    return res

def nfa_to_dfa(nfa_fragment):
    start = nfa_fragment.start
    trans = nfa_fragment.transitions
    symbols = set(k[1] for k in trans.keys() if k[1] != '')

    start_cl = frozenset(epsilon_closure({start}, trans))
    dfa_states = {start_cl}
    queue = deque([start_cl])
    dfa_trans = {}
    dfa_accepts = set()

    while queue:
        cur = queue.popleft()
        for sym in symbols:
            mv = move(cur, sym, trans)
            if not mv:
                continue
            cl = frozenset(epsilon_closure(mv, trans))
            dfa_trans[(cur, sym)] = cl
            if cl not in dfa_states:
                dfa_states.add(cl)
                queue.append(cl)

    for s in dfa_states:
        if any(a in s for a in nfa_fragment.accepts):
            dfa_accepts.add(s)

    return dfa_states, dfa_trans, start_cl, dfa_accepts
