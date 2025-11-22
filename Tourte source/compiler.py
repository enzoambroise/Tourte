import sys
from lexer import lex
from parser import Parser
from codegen import CodeGen

if len(sys.argv)<2:
    print("Usage: python compiler.py source.t -o out.asm")
    sys.exit(1)

srcfile = sys.argv[1]
outfile='out.asm'
if '-o' in sys.argv:
    outfile = sys.argv[sys.argv.index('-o')+1]

src=open(srcfile).read()
tokens=list(lex(src))
parser=Parser(tokens)
ast=parser.parse()

cg=CodeGen()
cg.gen(ast)
with open(outfile,'w') as f:
    f.write('\n'.join(cg.lines))
print(f"ASM written to {outfile}")
