from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, List, Dict
import sys
import re

# ======================
#  PrePro (comentários)
# ======================
class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove "// ...\n" mantendo o \n
        # Não adiciona espaços nem linhas extras
        return re.sub(r"//[^\n]*", "", code)

# ======================
#  Token
# ======================
@dataclass
class Token:
    kind: str        # 'INT' | 'PLUS' | 'MINUS' | 'MULT' | 'DIV' | 'OPEN_PAR' | 'CLOSE_PAR' | 'EOF' | 'ASSIGN' | 'END' | 'IDEN' | 'PRINT'
    value: int | str # int para INT; str para os demais

# ======================
#  Symbol Table
# ======================
@dataclass
class Variable:
    value: int

class SymbolTable:
    def __init__(self):
        self._table: Dict[str, Variable] = {}

    def get(self, name: str) -> int:
        if name not in self._table:
            raise Exception(f"[Semântico] Variável inexistente: '{name}'")
        return self._table[name].value

    def set(self, name: str, value: int) -> None:
        self._table[name] = Variable(value=value)

    @property
    def table(self) -> Dict[str, Variable]:
        return self._table

    @table.setter
    def table(self, new_table: Dict[str, Variable]) -> None:
        self._table = new_table

# ======================
#  Lexer
# ======================
class Lexer:
    RESERVED = {"log": "PRINT"}

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

        # Ignora espaços e quebras de linha; o ';' é o separador de instrução
        while c is not None and c.isspace():
            self.position += 1
            c = self._current_char()

        if c is None:
            self.next = Token('EOF', '')
            return

        # Operadores e pontuação
        if c == '+':
            self.position += 1
            self.next = Token('PLUS', '+'); return
        if c == '-':
            self.position += 1
            self.next = Token('MINUS', '-'); return
        if c == '*':
            self.position += 1
            self.next = Token('MULT', '*'); return
        if c == '/':
            self.position += 1
            self.next = Token('DIV', '/'); return
        if c == '(':
            self.position += 1
            self.next = Token('OPEN_PAR', '('); return
        if c == ')':
            self.position += 1
            self.next = Token('CLOSE_PAR', ')'); return
        if c == '=':
            self.position += 1
            self.next = Token('ASSIGN', '='); return
        if c == ';':
            self.position += 1
            self.next = Token('END', ';'); return

        # Número inteiro
        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self.position += 1
                c = self._current_char()
            lexeme = self.source[start:self.position]
            value = int(lexeme)
            self.next = Token('INT', value)
            return

        # Identificador: letra inicial; depois letras, dígitos ou '_'
        if c.isalpha():
            start = self.position
            while c is not None and (c.isalnum() or c == '_'):
                self.position += 1
                c = self._current_char()
            ident = self.source[start:self.position]
            kind = self.RESERVED.get(ident, 'IDEN')
            self.next = Token(kind, ident)
            return

        # Se começar com '_' é inválido (exigência do roteiro)
        if c == '_':
            raise Exception(f"[Lexer] Identificador inválido: não pode iniciar com '_' (pos {self.position})")

        raise Exception(f"[Lexer] Símbolo inválido '{c}' na posição {self.position}")

# ======================
#  AST Nodes
# ======================
class Node(ABC):
    def __init__(self, value: Any, children: List['Node'] | None = None):
        self.value: Any = value
        self.children: List['Node'] = children or []

    @abstractmethod
    def evaluate(self, st: SymbolTable) -> Any:
        ...

class IntVal(Node):
    def __init__(self, value: int):
        super().__init__(value, [])

    def evaluate(self, st: SymbolTable) -> int:
        return int(self.value)

class Identifier(Node):
    def __init__(self, name: str):
        super().__init__(name, [])

    def evaluate(self, st: SymbolTable) -> int:
        # Busca o valor atual na SymbolTable
        return st.get(self.value)

class NoOp(Node):
    def __init__(self):
        super().__init__(None, [])

    def evaluate(self, st: SymbolTable) -> None:
        return None

class Print(Node):
    def __init__(self, child: Node):
        super().__init__('print', [child])

    def evaluate(self, st: SymbolTable) -> None:
        val = self.children[0].evaluate(st)
        print(val)

class Assignment(Node):
    def __init__(self, name_node: Identifier, expr_node: Node):
        super().__init__('=', [name_node, expr_node])

    def evaluate(self, st: SymbolTable) -> None:
        name_node: Identifier = self.children[0]
        expr_node: Node = self.children[1]
        value = expr_node.evaluate(st)
        st.set(name_node.value, value)

class UnOp(Node):
    def __init__(self, op: str, child: Node):
        super().__init__(op, [child])

    def evaluate(self, st: SymbolTable) -> int:
        operand = self.children[0].evaluate(st)
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

    def evaluate(self, st: SymbolTable) -> int:
        a = self.children[0].evaluate(st)
        b = self.children[1].evaluate(st)
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

class Block(Node):
    def __init__(self, children: List[Node]):
        super().__init__('block', children)

    def evaluate(self, st: SymbolTable) -> None:
        for child in self.children:
            child.evaluate(st)

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
        if tok.kind == 'IDEN':
            node = Identifier(tok.value)
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
    def parse_statement() -> Node:
        tok = Parser.lex.next

        # Linha vazia: apenas ";"
        if tok.kind == 'END':
            Parser.lex.select_next()
            return NoOp()

        # PRINT: log ( EXPR ) ;
        if tok.kind == 'PRINT':
            Parser.lex.select_next()
            if Parser.lex.next.kind != 'OPEN_PAR':
                raise Exception(f"[Parser] Esperado '(', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            expr = Parser.parse_expression()
            if Parser.lex.next.kind != 'CLOSE_PAR':
                raise Exception(f"[Parser] Esperado ')', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            if Parser.lex.next.kind != 'END':
                raise Exception(f"[Parser] Esperado ';', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            return Print(expr)

        # ASSIGNMENT: IDEN = EXPR ;
        if tok.kind == 'IDEN':
            name = Identifier(tok.value)
            Parser.lex.select_next()
            if Parser.lex.next.kind != 'ASSIGN':
                raise Exception(f"[Parser] Esperado '=', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            expr = Parser.parse_expression()
            if Parser.lex.next.kind != 'END':
                raise Exception(f"[Parser] Esperado ';', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            return Assignment(name, expr)

        raise Exception(f"[Parser] Instrução inválida: inicia com {tok.kind}")

    @staticmethod
    def parse_program() -> Node:
        children: List[Node] = []
        while Parser.lex.next.kind != 'EOF':
            stmt = Parser.parse_statement()
            children.append(stmt)
        return Block(children)

    @staticmethod
    def run(code: str) -> Node:
        Parser.lex = Lexer(code)
        Parser.lex.select_next()
        root = Parser.parse_program()
        if Parser.lex.next.kind != 'EOF':
            raise Exception(f"[Parser] Token inesperado ao final: {Parser.lex.next.kind}")
        return root

# ======================
#  Main
# ======================
def main():
    if len(sys.argv) != 2:
        raise Exception('Uso: python3 main.py caminho/para/teste.ts')
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
        print(str(e), file=sys.stderr)
        sys.exit(1)
