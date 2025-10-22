from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List
from symbol_table import SymbolTable

class Node(ABC):
    def __init__(self, value: Any, children: List['Node'] | None = None):
        self.value = value
        self.children = children or []

    @abstractmethod
    def evaluate(self, st: SymbolTable) -> Any: ...

class IntVal(Node):
    def __init__(self, value: int):
        super().__init__(value)

    def evaluate(self, st: SymbolTable) -> int:
        return int(self.value)

class Identifier(Node):
    def __init__(self, name: str):
        super().__init__(name)

    def evaluate(self, st: SymbolTable) -> int:
        return st.get(self.value)

class NoOp(Node):
    def __init__(self):
        super().__init__(None)

    def evaluate(self, st: SymbolTable) -> None:
        return None

class Print(Node):
    def __init__(self, child: Node):
        super().__init__('print', [child])

    def evaluate(self, st: SymbolTable) -> None:
        val = self.children[0].evaluate(st)
        print(val)

class Read(Node):
    def __init__(self):
        super().__init__('read', [])

    def evaluate(self, st: SymbolTable) -> int:
        line = input()
        try:
            return int(line.strip())
        except ValueError:
            raise Exception(f"[Semântico] readline esperava inteiro, recebeu: {line!r}")

class Assignment(Node):
    def __init__(self, name_node: Identifier, expr_node: Node):
        super().__init__('=', [name_node, expr_node])

    def evaluate(self, st: SymbolTable) -> None:
        name_node: Identifier = self.children[0]
        value = self.children[1].evaluate(st)
        st.set(name_node.value, value)

class UnOp(Node):
    def __init__(self, op: str, child: Node):
        super().__init__(op, [child])

    def evaluate(self, st: SymbolTable) -> int:
        v = self.children[0].evaluate(st)
        if self.value == '+': return +v
        if self.value == '-': return -v
        if self.value == '!': return 0 if v != 0 else 1
        raise Exception(f"[UnOp] Operador unário inválido: {self.value}")

class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node):
        super().__init__(op, [left, right])

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0: raise Exception("[Semântico] Divisão por zero")
        return int(a / b)

    def evaluate(self, st: SymbolTable) -> int:
        a = self.children[0].evaluate(st)
        b = self.children[1].evaluate(st)

        # arit
        if self.value == '+': return a + b
        if self.value == '-': return a - b
        if self.value == '*': return a * b
        if self.value == '/': return self._int_div_trunc_toward_zero(a, b)
        if self.value == '%':
            if b == 0: raise Exception("[Semântico] Módulo por zero")
            return a % b

        # rel
        if self.value == '==':  return 1 if a == b else 0
        if self.value == '!=':  return 1 if a != b else 0
        if self.value == '===': return 1 if a == b else 0   # strict: igual a ==
        if self.value == '!==': return 1 if a != b else 0   # strict: igual a !=
        if self.value == '<':   return 1 if a <  b else 0
        if self.value == '>':   return 1 if a >  b else 0
        if self.value == '<=':  return 1 if a <= b else 0
        if self.value == '>=':  return 1 if a >= b else 0


        # bool
        if self.value == '&&': return 1 if (a != 0 and b != 0) else 0
        if self.value == '||': return 1 if (a != 0 or  b != 0) else 0

        raise Exception(f"[BinOp] Operador inválido: {self.value}")

class If(Node):
    def __init__(self, cond: Node, then_block: Node, else_block: Node | None = None):
        children = [cond, then_block] + ([else_block] if else_block is not None else [])
        super().__init__('if', children)

    def evaluate(self, st: SymbolTable) -> None:
        if self.children[0].evaluate(st) != 0:
            self.children[1].evaluate(st)
        elif len(self.children) == 3:
            self.children[2].evaluate(st)

class While(Node):
    def __init__(self, cond: Node, body: Node):
        super().__init__('while', [cond, body])

    def evaluate(self, st: SymbolTable) -> None:
        while self.children[0].evaluate(st) != 0:
            self.children[1].evaluate(st)

class Block(Node):
    def __init__(self, children: list[Node]):
        super().__init__('block', children)

    def evaluate(self, st: SymbolTable) -> None:
        for ch in self.children:
            ch.evaluate(st)
