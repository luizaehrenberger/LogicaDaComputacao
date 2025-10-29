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
        raise Exception(f"[Semantic] Esperado {expected} em {ctx}, recebeu {var.type}")

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
        try:
            return V_num(int(line.strip()))
        except ValueError:
            raise Exception(f"[Semantic] readline esperava inteiro, recebeu: {line!r}")


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
    value: string com o tipo ('number' | 'boolean' | 'string' | 'void')
    children[0]: Identifier
    children[1] (opcional): expressão de inicialização
    """
    def __init__(self, vtype: str, ident: Identifier, init_expr: Node | None = None, *, is_function: bool=False):
        kids = [ident] + ([init_expr] if init_expr is not None else [])
        super().__init__(vtype, kids)
        self.is_function = is_function  # sempre False para vars comuns

    def evaluate(self, st: SymbolTable) -> None:
        ident: Identifier = self.children[0]
        if self.value == 'void' and not self.is_function:
            raise Exception(f"[Semantic] Variável '{ident.value}' não pode ter tipo void")
        st.create_variable(ident.value, self.value)
        # inicialização opcional
        if len(self.children) == 2:
            init: Variable = self.children[1].evaluate(st)
            if init.type != self.value:
                raise Exception(
                    f"[Semantic] Tipos incompatíveis em inicialização de '{ident.value}': "
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
        raise Exception(f"[Semantic] Operador unário inválido: {self.value}")


# ---- Binário ----
class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node):
        super().__init__(op, [left, right])

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0: raise Exception("[Semantic] Divisão por zero")
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
                raise Exception(f"[Semantic] Operação aritmética requer 'number', recebeu {a.type} {op} {b.type}")
            if op == '+': return V_num(a.value + b.value)
            if op == '-': return V_num(a.value - b.value)
            if op == '*': return V_num(a.value * b.value)
            if op == '/': return V_num(self._int_div_trunc_toward_zero(a.value, b.value))
            if op == '%':
                if b.value == 0: raise Exception("[Semantic] Módulo por zero")
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
                raise Exception(f"[Semantic] Operador relacional '{op}' requer tipos iguais number/number ou string/string; recebeu {a.type} e {b.type}")

            if op in ('===', '!=='):
                # comparação estrita exige tipos iguais; caso contrário -> erro
                if a.type != b.type:
                    raise Exception(f"[Semantic] Tipos incompatíveis em comparação estrita: {a.type} {op} {b.type}")
                res = (a.value == b.value)
                return V_bool(res if op == '===' else (not res))

            # == e != soltos: tipos diferentes -> false/true direto
            if a.type != b.type:
                return V_bool(op == '!=')
            return V_bool((a.value == b.value) if op == '==' else (a.value != b.value))

        # ---- Booleanos ----
        if op in ('&&', '||'):
            if a.type != 'boolean' or b.type != 'boolean':
                raise Exception(f"[Semantic] Operadores lógicos requerem boolean: recebeu {a.type} {op} {b.type}")
            if op == '&&': return V_bool(a.value and b.value)
            if op == '||': return V_bool(a.value or  b.value)

        raise Exception(f"[Semantic] Operador inválido: {op}")


# ---- If / While / Block (com propagação de return e escopo em blocos aninhados) ----
class If(Node):
    def __init__(self, cond: Node, then_block: Node, else_block: Node | None = None):
        children = [cond, then_block] + ([else_block] if else_block is not None else [])
        super().__init__('if', children)
    def evaluate(self, st: SymbolTable) -> Any:
        cond: Variable = self.children[0].evaluate(st)
        ensure_type(cond, 'boolean', 'if(cond)')
        if cond.value:
            r = self.children[1].evaluate(st)
            return r
        elif len(self.children) == 3:
            r = self.children[2].evaluate(st)
            return r
        return None

class While(Node):
    def __init__(self, cond: Node, body: Node):
        super().__init__('while', [cond, body])
    def evaluate(self, st: SymbolTable) -> Any:
        while True:
            cond: Variable = self.children[0].evaluate(st)
            ensure_type(cond, 'boolean', 'while(cond)')
            if not cond.value: break
            r = self.children[1].evaluate(st)
            if isinstance(r, Variable):
                return r
        return None

class Block(Node):
    def __init__(self, children: list[Node]):
        super().__init__('block', children)
    def evaluate(self, st: SymbolTable) -> Any:
        for ch in self.children:
            if isinstance(ch, Block):
                # novo escopo encadeado para bloco aninhado
                inner = SymbolTable(parent=st)
                r = ch.evaluate(inner)
            else:
                r = ch.evaluate(st)
            if isinstance(r, Variable):  # Return propagado (Variable)
                return r
        return None


# ---- Return ----
class Return(Node):
    # value: 'return'; children[0]: expressão obrigatória
    def __init__(self, expr: Node):
        super().__init__('return', [expr])
    def evaluate(self, st: SymbolTable) -> Variable:
        return self.children[0].evaluate(st)


# ---- Declaração de Função ----
class FuncDec(Node):
    """
    value: tipo de retorno ('number' | 'boolean' | 'string' | 'void')
    children: [Identifier(nome), VarDec(param1), ..., VarDec(paramN), Block(corpo)]
    """
    def __init__(self, return_type: str, name_ident: Identifier, param_nodes: list[VarDec], body_block: Block):
        super().__init__(return_type, [name_ident] + param_nodes + [body_block])

    def evaluate(self, st: SymbolTable) -> None:
        name: str = self.children[0].value
        st.create_function(name, self.value, self)  # registra a própria função na ST


# ---- Chamada de Função ----
class FuncCall(Node):
    """
    value: nome da função
    children: lista de expressões dos argumentos
    """
    def __init__(self, name: str, arg_exprs: list[Node]):
        super().__init__(name, arg_exprs)

    def evaluate(self, st: SymbolTable) -> Any:
        fname = self.value
        fvar = st.get(fname)
        if not getattr(fvar, "is_function", False):
            raise Exception(f"[Semantic] '{fname}' não é uma função")
        fnode: FuncDec = fvar.value

        params = fnode.children[1:-1]  # VarDecs
        body: Block = fnode.children[-1]
        if len(params) != len(self.children):
            raise Exception(f"[Semantic] Chamada de '{fname}' com {len(self.children)} argumentos; esperado {len(params)}")

        # novo escopo da função (herda do chamador)
        call_st = SymbolTable(parent=st)

        # declara e inicializa parâmetros na nova ST
        for pnode, arg_expr in zip(params, self.children, strict=True):
            assert isinstance(pnode, VarDec)
            p_ident: Identifier = pnode.children[0]
            p_type: str = pnode.value
            call_st.create_variable(p_ident.value, p_type)
            aval: Variable = arg_expr.evaluate(st)  # avaliado no escopo do chamador
            if aval.type != p_type:
                raise Exception(
                    f"[Semantic] Tipo inválido no argumento '{p_ident.value}' de '{fname}': esperado {p_type}, recebeu {aval.type}"
                )
            call_st.set(p_ident.value, aval)

        # executa corpo
        r = body.evaluate(call_st)  # Variable (de Return) ou None
        ret_type = fnode.value

        if ret_type == 'void':
            # chamadas void não retornam valor
            return None

        if not isinstance(r, Variable):
            raise Exception(f"[Semantic] Função '{fname}' ({ret_type}) sem return")
        if r.type != ret_type:
            raise Exception(f"[Semantic] Return de '{fname}' incorreto: esperado {ret_type}, recebeu {r.type}")
        return r
