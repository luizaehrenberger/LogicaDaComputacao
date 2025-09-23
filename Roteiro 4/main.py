from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, List
import sys

# ======================
#  Token
# ======================
@dataclass
class Token:
    kind: str        # 'INT' | 'PLUS' | 'MINUS' | 'MULT' | 'DIV' | 'OPEN_PAR' | 'CLOSE_PAR' | 'EOF'
    value: int | str # int para INT; str para os demais


# ======================
#  Lexer
# ======================
class Lexer:
    def __init__(self, source: str):
        self.source: str = source
        self.position: int = 0
        self.next: Token | None = None

    def _current_char(self) -> str | None:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def select_next(self) -> None:
        c = self._current_char()

        while c is not None and c.isspace():
            self.position += 1
            c = self._current_char()

        if c is None:
            self.next = Token('EOF', '')
            return

        if c == '+':
            self.position += 1
            self.next = Token('PLUS', '+')
            return
        if c == '-':
            self.position += 1
            self.next = Token('MINUS', '-')
            return
        if c == '*':
            self.position += 1
            self.next = Token('MULT', '*')
            return
        if c == '/':
            self.position += 1
            self.next = Token('DIV', '/')
            return
        if c == '(':
            self.position += 1
            self.next = Token('OPEN_PAR', '(')
            return
        if c == ')':
            self.position += 1
            self.next = Token('CLOSE_PAR', ')')
            return

        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self.position += 1
                c = self._current_char()
            lexeme = self.source[start:self.position]
            value = int(lexeme)
            self.next = Token('INT', value)
            return

        raise Exception(f"[Lexer] Invalid symbol '{c}' at position {self.position}")


# ======================
#  AST Nodes
# ======================
class Node(ABC):
    def __init__(self, value: Any, children: List[Node] | None = None):
        self.value: Any = value
        self.children: List[Node] = children or []

    @abstractmethod
    def evaluate(self) -> Any:
        pass


class IntVal(Node):
    def __init__(self, value: int):
        super().__init__(value, [])

    def evaluate(self) -> int:
        return int(self.value)


class UnOp(Node):
    def __init__(self, op: str, child: Node):
        super().__init__(op, [child])

    def evaluate(self) -> int:
        operand = self.children[0].evaluate()
        if self.value == '+':
            return +operand
        elif self.value == '-':
            return -operand
        else:
            raise Exception(f"[UnOp] Operador unário inválido: {self.value}")


class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node):
        super().__init__(op, [left, right])

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0:
            raise Exception("[Semântico] Divisão por zero")
        return int(a / b)

    def evaluate(self) -> int:
        a = self.children[0].evaluate()
        b = self.children[1].evaluate()
        if self.value == '+':
            return a + b
        elif self.value == '-':
            return a - b
        elif self.value == '*':
            return a * b
        elif self.value == '/':
            return self._int_div_trunc_toward_zero(a, b)
        else:
            raise Exception(f"[BinOp] Operador inválido: {self.value}")


# ======================
#  Parser
# ======================
class Parser:
    lex: Lexer | None = None

    @staticmethod
    def parse_factor() -> Node:
        tok = Parser.lex.next
        if tok.kind == 'PLUS':
            Parser.lex.select_next()
            return UnOp('+', Parser.parse_factor())
        if tok.kind == 'MINUS':
            Parser.lex.select_next()
            return UnOp('-', Parser.parse_factor())
        if tok.kind == 'OPEN_PAR':
            Parser.lex.select_next()
            node = Parser.parse_expression()
            if Parser.lex.next.kind != 'CLOSE_PAR':
                raise Exception(f"[Parser] Esperado ')', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            return node
        if tok.kind == 'INT':
            node = IntVal(tok.value)
            Parser.lex.select_next()
            return node
        raise Exception(f"[Parser] Token inesperado em FACTOR: {tok.kind}")

    @staticmethod
    def parse_term() -> Node:
        left = Parser.parse_factor()
        while Parser.lex.next.kind in ('MULT', 'DIV'):
            op = Parser.lex.next.kind
            Parser.lex.select_next()
            right = Parser.parse_factor()
            left = BinOp('*' if op == 'MULT' else '/', left, right)
        return left

    @staticmethod
    def parse_expression() -> Node:
        left = Parser.parse_term()
        while Parser.lex.next.kind in ('PLUS', 'MINUS'):
            op = Parser.lex.next.kind
            Parser.lex.select_next()
            right = Parser.parse_term()
            left = BinOp('+' if op == 'PLUS' else '-', left, right)
        return left

    @staticmethod
    def run(code: str) -> Node:
        Parser.lex = Lexer(code)
        Parser.lex.select_next()
        root = Parser.parse_expression()
        if Parser.lex.next.kind != 'EOF':
            raise Exception(f"[Parser] Unexpected token {Parser.lex.next.kind}")
        return root


# ======================
#  Main
# ======================
def main():
    if len(sys.argv) != 2:
        raise Exception('Uso: python main.py "1+2"')
    code = sys.argv[1]
    root = Parser.run(code)
    print(root.evaluate())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
