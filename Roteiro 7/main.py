import sys
from prepro import PrePro
from parser import Parser
from symbol_table import SymbolTable

def main():
    if len(sys.argv) != 2:
        raise Exception('Uso: python -m src.main caminho/para/programa.ts (ou: python src/main.py arquivo.ts)')
    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        raw_code = f.read()

    code = PrePro.filter(raw_code)
    root = Parser.run(code)

    st = SymbolTable()
    root.evaluate(st)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        print(str(e), file=sys.stderr)
        sys.exit(1)
