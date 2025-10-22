import sys
import os
from prepro import PrePro
from parser import Parser
from symbol_table import SymbolTable
from codegen import Code

def main():
    if len(sys.argv) < 2:
        raise Exception('Uso: python -m src.main caminho/para/programa.ts [--gen-only]')
    filename = sys.argv[1]
    gen_only = (len(sys.argv) >= 3 and sys.argv[2] == "--gen-only")

    with open(filename, 'r', encoding='utf-8') as f:
        raw_code = f.read()

    code = PrePro.filter(raw_code)
    root = Parser.run(code)

    if not gen_only:
        st_eval = SymbolTable()
        root.evaluate(st_eval)

    st_gen = SymbolTable()
    Code.reset()
    root.generate(st_gen)
    asm_name = os.path.splitext(filename)[0] + ".asm"
    Code.dump(asm_name)
