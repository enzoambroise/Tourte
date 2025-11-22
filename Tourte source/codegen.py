from ast import *

class CodeGen:
    def __init__(self):
        self.lines=[]
        self.vars={}
        self.label_id=0
        self.format_label='fmt_int'

    def new_label(self, base='L'):
        self.label_id+=1
        return f"{base}{self.label_id}"

    def emit(self, line): self.lines.append(line)

    def ensure_var(self,name):
        if name not in self.vars:
            self.vars[name]=f'v_{name}'
        return self.vars[name]

    def gen(self, node):
        self.emit('extern printf')
        self.emit('global main')
        self.emit('section .text')
        self.emit('main:')
        self.emit('    push rbp')
        self.emit('    mov rbp,rsp')
        self.gen_block(node)
        self.emit('    mov rax,0')
        self.emit('    leave')
        self.emit('    ret')
        # data
        self.emit('section .rodata')
        self.emit(f'{self.format_label}: db "%ld",10,0')
        self.emit('section .bss')
        for name,label in self.vars.items():
            self.emit(f'    {label}: dq 0')

    def gen_block(self,block):
        for s in block.stmts:
            if s: self.gen_stmt(s)

    def gen_stmt(self,s):
        if isinstance(s,Assign):
            lbl=self.ensure_var(s.name)
            self.gen_expr(s.expr,'rax')
            self.emit(f'    mov qword [{lbl}], rax')
        elif isinstance(s,Print):
            self.gen_expr(s.expr,'rdi')
            self.emit('    mov rsi,rdi')
            self.emit(f'    lea rdi,[{self.format_label}]')
            self.emit('    xor rax,rax')
            self.emit('    call printf')
        elif isinstance(s,If):
            Lelse=self.new_label('Lelse')
            Lend=self.new_label('Lend')
            self.gen_expr(s.cond,'rax')
            self.emit('    cmp rax,0')
            self.emit(f'    je {Lelse}')
            self.gen_stmt(s.thenb) if not isinstance(s.thenb,Block) else self.gen_block(s.thenb)
            self.emit(f'    jmp {Lend}')
            self.emit(f'{Lelse}:')
            if s.elseb:
                self.gen_stmt(s.elseb) if not isinstance(s.elseb,Block) else self.gen_block(s.elseb)
            self.emit(f'{Lend}:')
        elif isinstance(s,While):
            Lstart=self.new_label('Lstart')
            Lend=self.new_label('Lend')
            self.emit(f'{Lstart}:')
            self.gen_expr(s.cond,'rax')
            self.emit('    cmp rax,0')
            self.emit(f'    je {Lend}')
            self.gen_stmt(s.body) if not isinstance(s.body,Block) else self.gen_block(s.body)
            self.emit(f'    jmp {Lstart}')
            self.emit(f'{Lend}:')
        elif isinstance(s,Block):
            self.gen_block(s)
        else:
            raise NotImplementedError(s)

    def gen_expr(self,e,reg):
        if isinstance(e,Num):
            self.emit(f'    mov {reg},{e.val}')
        elif isinstance(e,Var):
            lbl=self.ensure_var(e.name)
            self.emit(f'    mov {reg},qword [{lbl}]')
        elif isinstance(e,BinOp):
            self.gen_expr(e.left,'rax')
            self.emit('    push rax')
            self.gen_expr(e.right,'rbx')
            self.emit('    pop rax')
            if e.op=='+': self.emit('    add rax,rbx')
            elif e.op=='-': self.emit('    sub rax,rbx')
            elif e.op=='*': self.emit('    imul rax,rbx')
            elif e.op=='/':
                self.emit('    mov rdx,0')
                self.emit('    cqo')
                self.emit('    idiv rbx')
            elif e.op=='%':
                self.emit('    mov rdx,0')
                self.emit('    cqo')
                self.emit('    idiv rbx')
                self.emit('    mov rax,rdx')
            elif e.op=='**':
                # simple pow via loop (naïf)
                self.emit('    ; pow not implemented')
            else:
                self.emit(f'    ; unknown binop {e.op}')
            if reg!='rax':
                self.emit(f'    mov {reg},rax')
        elif isinstance(e,UniOp):
            self.gen_expr(e.val,reg)
            if e.op=='-': self.emit(f'    neg {reg}')
        else:
            raise NotImplementedError(e)
