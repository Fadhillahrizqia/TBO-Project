# nfa_builder.py
from collections import namedtuple

Fragment = namedtuple('Fragment', ['start', 'accepts', 'transitions'])

state_id = 0

def new_state():
    global state_id
    s = f'q{state_id}'
    state_id += 1
    return s

def merge_transitions(t1, t2):
    trans = {}
    for k, vs in list(t1.items()) + list(t2.items()):
        trans.setdefault(k, set()).update(vs)
    return trans

def thompson(postfix):
    stack = []
    for c in postfix:
        if c.isalnum():
            s = new_state(); a = new_state()
            trans = {(s, c): {a}}
            stack.append(Fragment(s, {a}, trans))

        elif c == '.':
            f2 = stack.pop(); f1 = stack.pop()
            trans = merge_transitions(f1.transitions, f2.transitions)
            for acc in f1.accepts:
                trans.setdefault((acc, ''), set()).add(f2.start)
            stack.append(Fragment(f1.start, f2.accepts, trans))

        elif c == '|':
            f2 = stack.pop(); f1 = stack.pop()
            s = new_state(); a = new_state()
            trans = merge_transitions(f1.transitions, f2.transitions)
            trans.setdefault((s, ''), set()).update({f1.start, f2.start})
            for acc in f1.accepts:
                trans.setdefault((acc, ''), set()).add(a)
            for acc in f2.accepts:
                trans.setdefault((acc, ''), set()).add(a)
            stack.append(Fragment(s, {a}, trans))

        elif c == '*':
            f = stack.pop()
            s = new_state(); a = new_state()
            trans = dict(f.transitions)
            trans.setdefault((s, ''), set()).add(f.start)
            trans.setdefault((s, ''), set()).add(a)
            for acc in f.accepts:
                trans.setdefault((acc, ''), set()).update({f.start, a})
            stack.append(Fragment(s, {a}, trans))

        else:
            raise ValueError('unknown operator: ' + c)

    if len(stack) != 1:
        raise ValueError('invalid regex')

    return stack[0]

# Test mandiri
if __name__ == '__main__':
    from regex_parser import to_postfix
    postfix = to_postfix('(a|b)*abb')
    frag = thompson(postfix)
    print('start:', frag.start)
    print('accepts:', frag.accepts)
    print('transitions:', frag.transitions)
