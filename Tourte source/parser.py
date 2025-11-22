from lexer import lex, Token
from ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else Token('EOF','')
    def pop(self): t=self.peek(); self.i+=1; return t

    def parse(self):
        stmts = []
        while self.peek().type != 'EOF':
            stmts.append(self.parse_stmt())
        return Block(stmts)

    def expect(self, typ, val=None):
        t=self.pop()
        if t.type != typ or (val is not None and t.val!=val):
            raise SyntaxError(f"Expected {typ} {val}, got {t}")
        return t

    def parse_stmt(self):
        t = self.peek()
        if t.type == 'ID':
            if t.val == 'print': return self.parse_print()
            if t.val == 'if': return self.parse_if()
            if t.val == 'while': return self.parse_while()
            if t.val == 'for': return self.parse_for()
            return self.parse_assign()
        elif t.type == 'SEMIC':
            self.pop(); return None
        elif t.type == 'LBRACE':
            return self.parse_block()
        else:
            raise SyntaxError(f"Unexpected {t}")

    def parse_block(self):
        self.expect('LBRACE')
        stmts=[]
        while self.peek().type != 'RBRACE':
            stmts.append(self.parse_stmt())
        self.expect('RBRACE')
        return Block(stmts)

    def parse_assign(self):
        name = self.expect('ID').val
        self.expect('OP','=')
        expr = self.parse_expr()
        self.expect('SEMIC')
        return Assign(name, expr)

    def parse_print(self):
        self.expect('ID','print')
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        self.expect('SEMIC')
        return Print(expr)

    def parse_if(self):
        self.expect('ID','if')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        thenb = self.parse_stmt()
        elseb=None
        if self.peek().type=='ID' and self.peek().val=='else':
            self.pop()
            elseb = self.parse_stmt()
        return If(cond, thenb, elseb)

    def parse_while(self):
        self.expect('ID','while')
        self.expect('LPAREN')
        cond=self.parse_expr()
        self.expect('RPAREN')
        body=self.parse_stmt()
        return While(cond, body)

    def parse_for(self):
        self.expect('ID','for')
        var=self.expect('ID').val
        self.expect('ID','in')
        self.expect('ID','range')
        self.expect('LPAREN')
        start=self.parse_expr()
        self.expect('COMMA')
        end=self.parse_expr()
        step=None
        if self.peek().type=='COMMA':
            self.pop(); step=self.parse_expr()
        self.expect('RPAREN')
        body=self.parse_stmt()
        return For(var, start, end, step, body)

    # Simple expressions (supports +,-,*,/,%,**)
    def parse_expr(self):
        left = self.parse_add()
        t = self.peek()
        if t.type == 'OP' and t.val in ('==','!=','<','>','<=','>='):
            op = self.pop().val
            right = self.parse_add()
            return BinOp(op, left, right)
        return left


    def parse_add(self):
        left = self.parse_mul()
        while self.peek().type=='OP' and self.peek().val in ('+','-'):
            op=self.pop().val
            right=self.parse_mul()
            left=BinOp(op,left,right)
        return left

    def parse_mul(self):
        left=self.parse_unary()
        while self.peek().type=='OP' and self.peek().val in ('*','/','%','**'):
            op=self.pop().val
            right=self.parse_unary()
            left=BinOp(op,left,right)
        return left

    def parse_unary(self):
        if self.peek().type=='OP' and self.peek().val=='-':
            self.pop()
            return UniOp('-', self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        t=self.pop()
        if t.type=='NUMBER': return Num(t.val)
        if t.type=='STRING': return Str(t.val)
        if t.type=='ID': return Var(t.val)
        if t.type=='LPAREN':
            expr=self.parse_expr()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected {t}")
