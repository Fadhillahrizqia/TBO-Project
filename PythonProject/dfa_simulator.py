# dfa_simulator.py

def simulate_dfa(dfa_start, dfa_trans, dfa_accepts, input_str):
    cur = dfa_start
    for c in input_str:
        key = (cur, c)
        if key not in dfa_trans:
            return False
        cur = dfa_trans[key]
    return cur in dfa_accepts
