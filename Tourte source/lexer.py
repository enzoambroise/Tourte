import re

token_spec = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('STRING',   r'"[^"]*"'),
    ('OP',       r'==|!=|<=|>=|<|>|=|\+|\-|\*|\/|\*\*|%|!|\*'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('COMMA',    r','),
    ('SEMIC',    r';'),
    ('SKIP',     r'[ \t\r\n]+'),
    ('MISMATCH', r'.'),
]

tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)

class Token:
    def __init__(self, typ, val):
        self.type = typ
        self.val = val
    def __repr__(self):
        return f"Token({self.type},{self.val})"

def lex(code):
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        val = mo.group()
        if kind == 'NUMBER':
            yield Token('NUMBER', float(val) if '.' in val else int(val))
        elif kind == 'STRING':
            yield Token('STRING', val[1:-1])
        elif kind == 'ID':
            yield Token('ID', val)
        elif kind == 'OP':
            yield Token('OP', val)
        elif kind in ('LPAREN','RPAREN','LBRACE','RBRACE','COMMA','SEMIC'):
            yield Token(kind, val)
        elif kind == 'SKIP':
            continue
        else:
            raise SyntaxError(f"Unexpected {val}")
