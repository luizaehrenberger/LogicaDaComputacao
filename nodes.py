from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List
from symbol_table import SymbolTable, Variable

# Helpers de criação
def V_num(x: int) -> Variable: return Variable("number", int(x))
def V_bool(b: bool) -> Variable: return Variable("boolean", bool(b))
def V_str(s: str) -> Variable: return Variable("string", str(s))

def str_value_of(var: Variable) -> str:
    if var.type == "boolean":
        return "true" if var.value else "false"
    return str(var.value)

def ensure_type(var: Variable, expected: str, ctx: str):
    if var.type != expected:
        raise Exception(f"[Semântico] Esperado {expected} em {ctx}, recebeu {var.type}")

class Node(ABC):
    def __init__(self, value: Any, children: List['Node'] | None = None):
        self.value = value
        self.children = children or []

    @abstractmethod
    def evaluate(self, st: SymbolTable) -> Any: ...


# ---- Literais ----
class IntVal(Node):
    def __init__(self, value: int):
        super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable:
        return V_num(self.value)

class BoolVal(Node):
    def __init__(self, value: bool):
        super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable:
        return V_bool(self.value)

class StringVal(Node):
    def __init__(self, value: str):
        super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable:
        return V_str(self.value)


# ---- Identificador ----
class Identifier(Node):
    def __init__(self, name: str):
        super().__init__(name)
    def evaluate(self, st: SymbolTable) -> Variable:
        return st.get(self.value)


# ---- NoOp ----
class NoOp(Node):
    def __init__(self):
        super().__init__(None)
    def evaluate(self, st: SymbolTable) -> None:
        return None


# ---- Print ----
class Print(Node):
    def __init__(self, child: Node):
        super().__init__('print', [child])
    def evaluate(self, st: SymbolTable) -> None:
        v: Variable = self.children[0].evaluate(st)
        print(str_value_of(v))


# ---- Read ----
class Read(Node):
    def __init__(self):
        super().__init__('read', [])
    def evaluate(self, st: SymbolTable) -> Variable:
        line = input()
        line = line.rstrip("\n")
        # Mantém compat com roteiros antigos: retorna number
        try:
            return V_num(int(line.strip()))
        except ValueError:
            raise Exception(f"[Semântico] readline esperava inteiro, recebeu: {line!r}")


# ---- Atribuição ----
class Assignment(Node):
    def __init__(self, name_node: Identifier, expr_node: Node):
        super().__init__('=', [name_node, expr_node])
    def evaluate(self, st: SymbolTable) -> None:
        name_node: Identifier = self.children[0]
        var_value: Variable = self.children[1].evaluate(st)
        st.set(name_node.value, var_value)


# ---- Declaração de variável ----
class VarDec(Node):
    """
    value: string com o tipo ('number' | 'boolean' | 'string')
    children[0]: Identifier
    children[1] (opcional): expressão de inicialização
    """
    def __init__(self, vtype: str, ident: Identifier, init_expr: Node | None = None):
        kids = [ident] + ([init_expr] if init_expr is not None else [])
        super().__init__(vtype, kids)
    def evaluate(self, st: SymbolTable) -> None:
        ident: Identifier = self.children[0]
        st.create_variable(ident.value, self.value)
        # inicialização opcional
        if len(self.children) == 2:
            init: Variable = self.children[1].evaluate(st)
            if init.type != self.value:
                raise Exception(
                    f"[Semântico] Tipos incompatíveis em inicialização de '{ident.value}': "
                    f"esperado {self.value}, recebeu {init.type}"
                )
            st.set(ident.value, init)


# ---- Unário ----
class UnOp(Node):
    def __init__(self, op: str, child: Node):
        super().__init__(op, [child])

    def evaluate(self, st: SymbolTable) -> Variable:
        v: Variable = self.children[0].evaluate(st)
        if self.value == '+':
            ensure_type(v, "number", "unário +")
            return V_num(+v.value)
        if self.value == '-':
            ensure_type(v, "number", "unário -")
            return V_num(-v.value)
        if self.value == '!':
            ensure_type(v, "boolean", "unário !")
            return V_bool(not v.value)
        raise Exception(f"[UnOp] Operador unário inválido: {self.value}")


# ---- Binário ----
class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node):
        super().__init__(op, [left, right])

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0: raise Exception("[Semântico] Divisão por zero")
        return int(a / b)

    def evaluate(self, st: SymbolTable) -> Variable:
        a: Variable = self.children[0].evaluate(st)
        b: Variable = self.children[1].evaluate(st)
        op = self.value

        # ---- Aritmética / Concatenação ----
        if op in ('+', '-', '*', '/', '%'):
            # Concatenação: se qualquer operando for string -> resultado string
            if op == '+' and ('string' in (a.type, b.type)):
                return V_str(str_value_of(a) + str_value_of(b))
            # Caso contrário: aritmética estrita sobre number
            if a.type != 'number' or b.type != 'number':
                raise Exception(f"[Semântico] Operação aritmética requer 'number', recebeu {a.type} {op} {b.type}")
            if op == '+': return V_num(a.value + b.value)
            if op == '-': return V_num(a.value - b.value)
            if op == '*': return V_num(a.value * b.value)
            if op == '/': return V_num(self._int_div_trunc_toward_zero(a.value, b.value))
            if op == '%':
                if b.value == 0: raise Exception("[Semântico] Módulo por zero")
                return V_num(a.value % b.value)

        # ---- Relacionais (estritos e não-estritos) ----
        if op in ('==', '!=', '===', '!==', '<', '>', '<=', '>='):
            if op in ('<', '>', '<=', '>='):
                # number vs number  OU  string vs string (ordem lexicográfica)
                if a.type == 'number' and b.type == 'number':
                    res = {
                        '<':  a.value <  b.value,
                        '>':  a.value >  b.value,
                        '<=': a.value <= b.value,
                        '>=': a.value >= b.value,
                    }[op]
                    return V_bool(res)
                if a.type == 'string' and b.type == 'string':
                    res = {
                        '<':  a.value <  b.value,
                        '>':  a.value >  b.value,
                        '<=': a.value <= b.value,
                        '>=': a.value >= b.value,
                    }[op]
                    return V_bool(res)
                raise Exception(f"[Semântico] Operador relacional '{op}' requer tipos iguais number/number ou string/string; recebeu {a.type} e {b.type}")

            if op in ('===', '!=='):
                # estrito: tipos devem ser iguais
                res = (a.type == b.type and a.value == b.value)
                return V_bool(res if op == '===' else (not res))

            # == e != "solto": se tipos diferentes -> false/true diretamente
            if a.type != b.type:
                return V_bool(op == '!=')
            return V_bool((a.value == b.value) if op == '==' else (a.value != b.value))

        # ---- Booleanos ----
        if op in ('&&', '||'):
            if a.type != 'boolean' or b.type != 'boolean':
                raise Exception(f"[Semântico] Operadores lógicos requerem boolean: recebeu {a.type} {op} {b.type}")
            if op == '&&': return V_bool(a.value and b.value)
            if op == '||': return V_bool(a.value or  b.value)

        raise Exception(f"[BinOp] Operador inválido: {op}")


# ---- If / While / Block ----
class If(Node):
    def __init__(self, cond: Node, then_block: Node, else_block: Node | None = None):
        children = [cond, then_block] + ([else_block] if else_block is not None else [])
        super().__init__('if', children)
    def evaluate(self, st: SymbolTable) -> None:
        cond: Variable = self.children[0].evaluate(st)
        ensure_type(cond, 'boolean', 'if(cond)')
        if cond.value:
            self.children[1].evaluate(st)
        elif len(self.children) == 3:
            self.children[2].evaluate(st)

class While(Node):
    def __init__(self, cond: Node, body: Node):
        super().__init__('while', [cond, body])
    def evaluate(self, st: SymbolTable) -> None:
        while True:
            cond: Variable = self.children[0].evaluate(st)
            ensure_type(cond, 'boolean', 'while(cond)')
            if not cond.value: break
            self.children[1].evaluate(st)

class Block(Node):
    def __init__(self, children: list[Node]):
        super().__init__('block', children)
    def evaluate(self, st: SymbolTable) -> None:
        for ch in self.children:
            ch.evaluate(st)
