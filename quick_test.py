# quick_test.py
from __future__ import annotations
import sys
from typing import Callable, Optional, Any

# Importa o Parser do seu compilador
from main import Parser

def eval_expr(expr: str) -> Any:
    """Monta a AST e avalia a expressão."""
    return Parser.run(expr).evaluate()

class Test:
    def __init__(self, expr: str, expected: Any = None, expect_error: Optional[str] = None):
        self.expr = expr
        self.expected = expected
        self.expect_error = expect_error  # substring esperada na mensagem de erro

    def run(self) -> tuple[bool, str]:
        try:
            got = eval_expr(self.expr)
            if self.expect_error is not None:
                return False, f"ERRO ESPERADO mas avaliou para {got}"
            if got != self.expected:
                return False, f"esperado={self.expected}, obtido={got}"
            return True, "ok"
        except Exception as e:
            if self.expect_error is None:
                return False, f"exceção inesperada: {e}"
            msg = str(e)
            if self.expect_error in msg:
                return True, "ok (erro esperado)"
            return False, f"mensagem de erro diferente.\nesperado conter: {self.expect_error}\nobtido: {msg}"

tests = [
    # números e espaços
    Test("0", 0),
    Test("42", 42),
    Test("   7   ", 7),

    # soma/subtração
    Test("2+3", 5),
    Test("10-4-3", 3),            # associatividade à esquerda: (10-4)-3
    Test("1 - -2", 3),

    # precedência * / sobre + -
    Test("2+3*4", 14),
    Test("2*3+4", 10),
    Test("8/4+2", 4),             # (8/4)+2
    Test("6/2*3", 9),             # (6/2)*3

    # parênteses
    Test("(2+3)/(5*1)", 1),
    Test("((1))", 1),
    Test("  12 +   3 * ( 4 - 2 )  ", 18),

    # unários encadeados
    Test("-2", -2),
    Test("--2", 2),
    Test("+-2", -2),
    Test("++--++2", 2),

    # divisão inteira truncando em direção ao zero
    Test("7/3", 2),
    Test("-7/3", -2),
    Test("7/-3", -2),
    Test("-7/-3", 2),

    # multiplicação e combinações
    Test("-3*2", -6),
    Test("(-3)*(-2)", 6),
    Test("2*-3+5", -1),

    # números grandes
    Test("123456*0", 0),
    Test("99999+1", 100000),

    # erros esperados
    Test("1/0", expect_error="Divisão por zero"),
    Test("2+*", expect_error="Token inesperado"),     # sintaxe inválida
    Test("(1+2", expect_error="Esperado ')'"),        # parêntese faltando
]

def main() -> None:
    total = len(tests)
    passed = 0

    print("=== Testes do Roteiro 4 (AST) ===\n")
    for i, t in enumerate(tests, 1):
        ok, msg = t.run()
        status = "✅" if ok else "❌"
        print(f"{status} [{i:02d}/{total}] {t.expr!r} -> {msg}")
        if ok:
            passed += 1

    print(f"\nResumo: {passed}/{total} passaram.")
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
