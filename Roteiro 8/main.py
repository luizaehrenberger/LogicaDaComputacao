import sys
import os
from prepro import PrePro
from parser import Parser
from symbol_table import SymbolTable
from codegen import Code  # estamos dentro de src/, então pegamos o nosso code.py

def main():
    if len(sys.argv) < 2:
        raise Exception('Uso: python -m src.main caminho/para/programa.ts [--no-run|--gen-only]')
    filename = sys.argv[1]
    no_run = (len(sys.argv) >= 3 and sys.argv[2] in ("--no-run", "--gen-only"))

    with open(filename, 'r', encoding='utf-8') as f:
        raw_code = f.read()

    code = PrePro.filter(raw_code)
    root = Parser.run(code)

    # 1) GERAÇÃO DE ASM (SEMPRE)
    st_gen = SymbolTable()
    Code.reset()
    root.generate(st_gen)
    asm_name = os.path.splitext(filename)[0] + ".asm"
    Code.dump(asm_name)

    # 2) INTERPRETAÇÃO (opcional)
    if not no_run:
        try:
            st_eval = SymbolTable()
            root.evaluate(st_eval)
        except KeyboardInterrupt:
            # usuário cancelou entrada; o .asm já foi gerado
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
