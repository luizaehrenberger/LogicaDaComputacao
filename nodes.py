from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List
from symbol_table import SymbolTable, Variable

def V_num(x: int) -> Variable: return Variable("number", int(x))
def V_bool(b: bool) -> Variable: return Variable("boolean", bool(b))
def V_str(s: str) -> Variable: return Variable("string", str(s))

def str_value_of(var: Variable) -> str:
    if var.type == "boolean":
        return "true" if var.value else "false"
    return str(var.value)

def ensure_type(var: Variable, expected: str, ctx: str):
    if var.type != expected:
        raise Exception(f"[Semantic] Esperado {expected} em {ctx}, recebeu {var.type}")

class Node(ABC):
    def __init__(self, value: Any, children: List['Node'] | None = None):
        self.value = value
        self.children = children or []
    @abstractmethod
    def evaluate(self, st: SymbolTable) -> Any: ...

class IntVal(Node):
    def __init__(self, value: int): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_num(self.value)

class BoolVal(Node):
    def __init__(self, value: bool): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_bool(self.value)

class StringVal(Node):
    def __init__(self, value: str): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_str(self.value)

class Identifier(Node):
    def __init__(self, name: str): super().__init__(name)
    def evaluate(self, st: SymbolTable) -> Variable: return st.get(self.value)

class NoOp(Node):
    def __init__(self): super().__init__(None)
    def evaluate(self, st: SymbolTable) -> None: return None

class Print(Node):
    def __init__(self, child: Node): super().__init__('print', [child])
    def evaluate(self, st: SymbolTable) -> None:
        v = self.children[0].evaluate(st)
        print(str_value_of(v))

class Read(Node):
    def __init__(self): super().__init__('read', [])
    def evaluate(self, st: SymbolTable) -> Variable:
        line = input()
        line = line.rstrip("\n")
        try:
            return V_num(int(line.strip()))
        except ValueError:
            raise Exception(f"[Semantic] readline esperava inteiro, recebeu: {line!r}")

class Assignment(Node):
    def __init__(self, name_node: Identifier, expr_node: Node): super().__init__('=', [name_node, expr_node])
    def evaluate(self, st: SymbolTable) -> None:
        name_node = self.children[0]
        var_value = self.children[1].evaluate(st)
        st.set(name_node.value, var_value)

class VarDec(Node):
    def __init__(self, vtype: str, ident: Identifier, init_expr: Node | None = None, *, is_function: bool=False):
        kids = [ident] + ([init_expr] if init_expr is not None else [])
        super().__init__(vtype, kids)
        self.is_function = is_function
    def evaluate(self, st: SymbolTable) -> None:
        ident = self.children[0]
        if self.value == 'void' and not self.is_function:
            raise Exception(f"[Semantic] Variável '{ident.value}' não pode ter tipo void")
        st.create_variable(ident.value, self.value)
        if len(self.children) == 2:
            init = self.children[1].evaluate(st)
            if init.type != self.value:
                raise Exception(f"[Semantic] Tipos incompatíveis em inicialização de '{ident.value}': esperado {self.value}, recebeu {init.type}")
            st.set(ident.value, init)

class UnOp(Node):
    def __init__(self, op: str, child: Node): super().__init__(op, [child])
    def evaluate(self, st: SymbolTable) -> Variable:
        v = self.children[0].evaluate(st)
        if self.value == '+':
            ensure_type(v, "number", "unário +"); return V_num(+v.value)
        if self.value == '-':
            ensure_type(v, "number", "unário -"); return V_num(-v.value)
        if self.value == '!':
            ensure_type(v, "boolean", "unário !"); return V_bool(not v.value)
        raise Exception(f"[Semantic] Operador unário inválido: {self.value}")

class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node): super().__init__(op, [left, right])
    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0: raise Exception("[Semantic] Divisão por zero")
        return int(a / b)
    def evaluate(self, st: SymbolTable) -> Variable:
        a = self.children[0].evaluate(st)
        b = self.children[1].evaluate(st)
        op = self.value
        if op in ('+', '-', '*', '/', '%'):
            if op == '+' and ('string' in (a.type, b.type)):
                return V_str(str_value_of(a) + str_value_of(b))
            if a.type != 'number' or b.type != 'number':
                raise Exception(f"[Semantic] Operação aritmética requer 'number', recebeu {a.type} {op} {b.type}")
            if op == '+': return V_num(a.value + b.value)
            if op == '-': return V_num(a.value - b.value)
            if op == '*': return V_num(a.value * b.value)
            if op == '/': return V_num(self._int_div_trunc_toward_zero(a.value, b.value))
            if op == '%':
                if b.value == 0: raise Exception("[Semantic] Módulo por zero")
                return V_num(a.value % b.value)
        if op in ('==', '!=', '===', '!==', '<', '>', '<=', '>='):
            if op in ('<', '>', '<=', '>='):
                if a.type == 'number' and b.type == 'number':
                    res = {'<':a.value<b.value,'>':a.value>b.value,'<=':a.value<=b.value,'>=':a.value>=b.value}[op]
                    return V_bool(res)
                if a.type == 'string' and b.type == 'string':
                    res = {'<':a.value<b.value,'>':a.value>b.value,'<=':a.value<=b.value,'>=':a.value>=b.value}[op]
                    return V_bool(res)
                raise Exception(f"[Semantic] Operador relacional '{op}' requer tipos iguais number/number ou string/string; recebeu {a.type} e {b.type}")
            if op in ('===', '!=='):
                if a.type != b.type:
                    raise Exception(f"[Semantic] Tipos incompatíveis em comparação estrita: {a.type} {op} {b.type}")
                res = (a.value == b.value)
                return V_bool(res if op == '===' else (not res))
            if a.type != b.type:
                return V_bool(op == '!=')
            return V_bool((a.value == b.value) if op == '==' else (a.value != b.value))
        if op in ('&&', '||'):
            if a.type != 'boolean' or b.type != 'boolean':
                raise Exception(f"[Semantic] Operadores lógicos requerem boolean: recebeu {a.type} {op} {b.type}")
            if op == '&&': return V_bool(a.value and b.value)
            if op == '||': return V_bool(a.value or b.value)
        raise Exception(f"[Semantic] Operador inválido: {op}")

class If(Node):
    def __init__(self, cond: Node, then_block: Node, else_block: Node | None = None):
        children = [cond, then_block] + ([else_block] if else_block is not None else [])
        super().__init__('if', children)
    def evaluate(self, st: SymbolTable) -> Any:
        cond = self.children[0].evaluate(st)
        ensure_type(cond, 'boolean', 'if(cond)')
        if cond.value:
            r = self.children[1].evaluate(st)
            return r
        elif len(self.children) == 3:
            r = self.children[2].evaluate(st)
            return r
        return None

class While(Node):
    def __init__(self, cond: Node, body: Node): super().__init__('while', [cond, body])
    def evaluate(self, st: SymbolTable) -> Any:
        while True:
            cond = self.children[0].evaluate(st)
            ensure_type(cond, 'boolean', 'while(cond)')
            if not cond.value: break
            r = self.children[1].evaluate(st)
            if isinstance(r, Variable):
                return r
        return None

class Block(Node):
    def __init__(self, children: list[Node]): super().__init__('block', children)
    def evaluate(self, st: SymbolTable) -> Any:
        for ch in self.children:
            if isinstance(ch, Block):
                inner = SymbolTable(parent=st)
                r = ch.evaluate(inner)
            else:
                r = ch.evaluate(st)
            if isinstance(r, Variable):
                return r
        return None

class Return(Node):
    def __init__(self, expr: Node): super().__init__('return', [expr])
    def evaluate(self, st: SymbolTable) -> Variable:
        return self.children[0].evaluate(st)

class FuncDec(Node):
    def __init__(self, return_type: str, name_ident: Identifier, param_nodes: list[VarDec], body_block: Block):
        super().__init__(return_type, [name_ident] + param_nodes + [body_block])
    def evaluate(self, st: SymbolTable) -> None:
        name = self.children[0].value
        st.create_function(name, self.value, self)

class FuncCall(Node):
    def __init__(self, name: str, arg_exprs: list[Node]): super().__init__(name, arg_exprs)
    def evaluate(self, st: SymbolTable) -> Any:
        fname = self.value
        fvar = st.get(fname)
        if not getattr(fvar, "is_function", False):
            raise Exception(f"[Semantic] '{fname}' não é uma função")
        fnode: FuncDec = fvar.value
        params = fnode.children[1:-1]
        body: Block = fnode.children[-1]
        if len(params) != len(self.children):
            raise Exception(f"[Semantic] Chamada de '{fname}' com {len(self.children)} argumentos; esperado {len(params)}")
        call_st = SymbolTable(parent=st)
        for pnode, arg_expr in zip(params, self.children, strict=True):
            p_ident = pnode.children[0]
            p_type = pnode.value
            call_st.create_variable(p_ident.value, p_type)
            aval = arg_expr.evaluate(st)
            if aval.type != p_type:
                raise Exception(f"[Semantic] Tipo inválido no argumento '{p_ident.value}' de '{fname}': esperado {p_type}, recebeu {aval.type}")
            call_st.set(p_ident.value, aval)
        r = body.evaluate(call_st)
        ret_type = fnode.value
        if ret_type == 'void':
            return None
        if not isinstance(r, Variable):
            raise Exception(f"[Semantic] Função '{fname}' ({ret_type}) sem return")
        if r.type != ret_type:
            raise Exception(f"[Semantic] Return de '{fname}' incorreto: esperado {ret_type}, recebeu {r.type}")
        return r
