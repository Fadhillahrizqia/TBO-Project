# regex_parser.py
precedence = {'*': 3, '.': 2, '|': 1}

def add_concat(regex):
    res = ''
    prev = None
    for c in regex:
        if prev is not None:
            # jika prev bukan '(' atau '|' dan c bukan '|' atau ')' atau '*', sisipkan '.'
            if (prev not in '(|' and c not in '|)*'):
                res += '.'
        res += c
        prev = c
    return res

def to_postfix(regex):
    regex = add_concat(regex)
    output = []
    stack = []
    for c in regex:
        if c.isalnum():
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            # pop sampai '(' atau error jika tidak ada '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses: missing '('")
            stack.pop()
        else:
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(c, 0):
                output.append(stack.pop())
            stack.append(c)
    while stack:
        top = stack.pop()
        if top == '(' or top == ')':
            raise ValueError("Mismatched parentheses")
        output.append(top)
    return ''.join(output)
