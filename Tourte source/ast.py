class Node:
    pass

class Num(Node):
    def __init__(self, val): self.val = val

class Str(Node):
    def __init__(self, val): self.val = val

class Var(Node):
    def __init__(self, name): self.name = name

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op; self.left = left; self.right = right

class UniOp(Node):
    def __init__(self, op, val):
        self.op = op; self.val = val

class Assign(Node):
    def __init__(self, name, expr): self.name = name; self.expr = expr

class Print(Node):
    def __init__(self, expr): self.expr = expr

class If(Node):
    def __init__(self, cond, thenb, elseb=None):
        self.cond = cond; self.thenb = thenb; self.elseb = elseb

class While(Node):
    def __init__(self, cond, body): self.cond = cond; self.body = body

class For(Node):
    def __init__(self, var, start, end, step, body):
        self.var=var; self.start=start; self.end=end; self.step=step; self.body=body

class Block(Node):
    def __init__(self, stmts): self.stmts = stmts
