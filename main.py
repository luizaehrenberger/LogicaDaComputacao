import sys
import os
from prepro import PrePro
from parser import Parser
from symbol_table import SymbolTable
from code import Code  # se você renomeou para codegen.py, troque aqui

def main():
    if len(sys.argv) < 2:
        raise Exception('Uso: python -m src.main caminho/para/programa.ts [--no-run]')
    filename = sys.argv[1]
    no_run = (len(sys.argv) >= 3 and sys.argv[2] in ("--no-run", "--gen-only"))

    with open(filename, 'r', encoding='utf-8') as f:
        raw_code = f.read()

    code = PrePro.filter(raw_code)
    root = Parser.run(code)

    # 1) SEMPRE gerar o assembly, independentemente de erros/entradas do interpretador
    st_gen = SymbolTable()
    Code.reset()
    root.generate(st_gen)
    asm_name = os.path.splitext(filename)[0] + ".asm"
    Code.dump(asm_name)

    # 2) Rodar o interpretador só se o usuário quiser (e sem impedir a geração)
    if not no_run:
        try:
            st_eval = SymbolTable()
            root.evaluate(st_eval)
        except KeyboardInterrupt:
            # usuário cancelou a entrada; tudo bem, o .asm já foi gerado
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
