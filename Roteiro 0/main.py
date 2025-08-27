import sys
import re

def main():
    if len(sys.argv) != 2:
        raise Exception('Uso: python main.py "1+2"')

    s = sys.argv[1].strip()

    # Validação: número, seguido de (op (+|-) com número) repetidamente.
    # Espaços são permitidos APENAS ao redor dos operadores, nunca entre dígitos.
    if not re.fullmatch(r'\d+(?:\s*[+-]\s*\d+)*', s):
        raise Exception("Expressão inválida")

    # Remove espaços para avaliar
    expr = re.sub(r'\s+', '', s)

    # Captura inteiros com sinal (o primeiro sem sinal explícito; os seguintes com + ou -)
    tokens = re.findall(r'[+-]?\d+', expr)
    total = sum(int(t) for t in tokens)

    # Imprime apenas o número
    print(total)

if __name__ == "__main__":
    main()
