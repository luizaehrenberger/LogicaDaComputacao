from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List
from symbol_table import SymbolTable, Variable
from code import Code

# Helpers (interpretador)
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

# ---------- Base Node ----------
class Node(ABC):
    _uid: int = 0

    @staticmethod
    def newId() -> int:
        Node._uid += 1
        return Node._uid

    def __init__(self, value: Any, children: List['Node'] | None = None):
        self.value = value
        self.children = children or []
        self.id = Node.newId()

    @abstractmethod
    def evaluate(self, st: SymbolTable) -> Any: ...

    def generate(self, st: SymbolTable) -> None:
        raise Exception("[CodeGen] generate() não implementado para este nó")

# ---------- Literais ----------
class IntVal(Node):
    def __init__(self, value: int): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_num(self.value)
    def generate(self, st: SymbolTable) -> None: Code.append(f"  mov eax, {int(self.value)}")

class BoolVal(Node):
    def __init__(self, value: bool): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_bool(self.value)
    def generate(self, st: SymbolTable) -> None: Code.append(f"  mov eax, {1 if self.value else 0}")

class StringVal(Node):
    def __init__(self, value: str): super().__init__(value)
    def evaluate(self, st: SymbolTable) -> Variable: return V_str(self.value)
    def generate(self, st: SymbolTable) -> None:
        raise Exception("[CodeGen] Strings não são suportadas no gerador")

# ---------- Identificador ----------
class Identifier(Node):
    def __init__(self, name: str): super().__init__(name)
    def evaluate(self, st: SymbolTable) -> Variable: return st.get(self.value)
    def generate(self, st: SymbolTable) -> None:
        var = st.get(self.value)
        if var.shift is None:
            raise Exception("[CodeGen] Variável sem deslocamento de pilha")
        Code.append(f"  mov eax, [ebp-{var.shift}]")

# ---------- NoOp ----------
class NoOp(Node):
    def __init__(self): super().__init__(None)
    def evaluate(self, st: SymbolTable) -> None: return None
    def generate(self, st: SymbolTable) -> None: pass

# ---------- Print ----------
class Print(Node):
    def __init__(self, child: Node): super().__init__('print', [child])
    def evaluate(self, st: SymbolTable) -> None:
        v: Variable = self.children[0].evaluate(st)
        print(str_value_of(v))
    def generate(self, st: SymbolTable) -> None:
        self.children[0].generate(st)
        Code.append("  push eax")
        Code.append("  push dword format_out")
        Code.append("  call printf")
        Code.append("  add esp, 8")

# ---------- Read ----------
class Read(Node):
    def __init__(self): super().__init__('read', [])
    def evaluate(self, st: SymbolTable) -> Variable:
        line = input().rstrip("\n")
        try:
            return V_num(int(line.strip()))
        except ValueError:
            raise Exception(f"[Semantic] readline esperava inteiro, recebeu: {line!r}")
    def generate(self, st: SymbolTable) -> None:
        Code.append("  push dword scan_int")
        Code.append("  push dword format_in")
        Code.append("  call scanf")
        Code.append("  add esp, 8")
        Code.append("  mov eax, dword [scan_int]")

# ---------- Atribuição ----------
class Assignment(Node):
    def __init__(self, name_node: Identifier, expr_node: Node):
        super().__init__('=', [name_node, expr_node])
    def evaluate(self, st: SymbolTable) -> None:
        name_node: Identifier = self.children[0]
        var_value: Variable = self.children[1].evaluate(st)
        st.set(name_node.value, var_value)
    def generate(self, st: SymbolTable) -> None:
        name_node: Identifier = self.children[0]
        expr_node: Node = self.children[1]
        var = st.get(name_node.value)
        if var.shift is None:
            raise Exception("[CodeGen] Variável sem deslocamento de pilha")
        expr_node.generate(st)
        Code.append(f"  mov [ebp-{var.shift}], eax")

# ---------- Declaração ----------
class VarDec(Node):
    def __init__(self, vtype: str, ident: Identifier, init_expr: Node | None = None):
        kids = [ident] + ([init_expr] if init_expr is not None else [])
        super().__init__(vtype, kids)
    def evaluate(self, st: SymbolTable) -> None:
        ident: Identifier = self.children[0]
        st.create_variable(ident.value, self.value)
        if len(self.children) == 2:
            init: Variable = self.children[1].evaluate(st)
            if init.type != self.value:
                raise Exception(
                    f"[Semantic] Tipos incompatíveis em inicialização de '{ident.value}': "
                    f"esperado {self.value}, recebeu {init.type}"
                )
            st.set(ident.value, init)
    def generate(self, st: SymbolTable) -> None:
        ident: Identifier = self.children[0]
        st.create_variable(ident.value, self.value)
        var = st.get(ident.value)
        Code.append(f"  sub esp, 4 ; var {ident.value} int [EBP-{var.shift}]")
        if len(self.children) == 2:
            self.children[1].generate(st)
            Code.append(f"  mov [ebp-{var.shift}], eax")

# ---------- Unário ----------
class UnOp(Node):
    def __init__(self, op: str, child: Node): super().__init__(op, [child])
    def evaluate(self, st: SymbolTable) -> Variable:
        v: Variable = self.children[0].evaluate(st)
        if self.value == '+':
            ensure_type(v, "number", "unário +"); return V_num(+v.value)
        if self.value == '-':
            ensure_type(v, "number", "unário -"); return V_num(-v.value)
        if self.value == '!':
            ensure_type(v, "boolean", "unário !"); return V_bool(not v.value)
        raise Exception(f"[Semantic] Operador unário inválido: {self.value}")
    def generate(self, st: SymbolTable) -> None:
        self.children[0].generate(st)
        if self.value == '+': return
        if self.value == '-':
            Code.append("  neg eax"); return
        if self.value == '!':
            Code.append("  cmp eax, 0")
            Code.append(f"  jne not_false_{self.id}")
            Code.append("  mov eax, 1")
            Code.append(f"  jmp not_end_{self.id}")
            Code.append(f"not_false_{self.id}:")
            Code.append("  mov eax, 0")
            Code.append(f"not_end_{self.id}:")
            return
        raise Exception(f"[CodeGen] UnOp inválido: {self.value}")

# ---------- Binário ----------
class BinOp(Node):
    def __init__(self, op: str, left: Node, right: Node): super().__init__(op, [left, right])

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0: raise Exception("[Semantic] Divisão por zero")
        return int(a / b)

    def evaluate(self, st: SymbolTable) -> Variable:
        a: Variable = self.children[0].evaluate(st)
        b: Variable = self.children[1].evaluate(st)
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
                    res = {'<': a.value < b.value, '>': a.value > b.value,
                           '<=': a.value <= b.value, '>=': a.value >= b.value}[op]
                    return V_bool(res)
                if a.type == 'string' and b.type == 'string':
                    res = {'<': a.value < b.value, '>': a.value > b.value,
                           '<=': a.value <= b.value, '>=': a.value >= b.value}[op]
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
            if op == '||': return V_bool(a.value or  b.value)

        raise Exception(f"[Semantic] Operador inválido: {op}")

    def generate(self, st: SymbolTable) -> None:
        left, right = self.children
        right.generate(st)          # EAX = right
        Code.append("  push eax")
        left.generate(st)           # EAX = left
        Code.append("  pop ecx")    # ECX = right
        op = self.value

        if op == '+': Code.append("  add eax, ecx"); return
        if op == '-': Code.append("  sub eax, ecx"); return
        if op == '*': Code.append("  imul ecx");     return
        if op == '/':
            Code.append("  cdq")
            Code.append("  idiv ecx"); return
        if op == '%':
            Code.append("  cdq")
            Code.append("  idiv ecx")
            Code.append("  mov eax, edx"); return

        if op in ('<','>','<=','>=','==','!=','===','!=='):
            Code.append("  cmp eax, ecx")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            if op == '<':   Code.append("  cmovl  eax, ecx"); return
            if op == '>':   Code.append("  cmovg  eax, ecx"); return
            if op == '<=':  Code.append("  cmovle eax, ecx"); return
            if op == '>=':  Code.append("  cmovge eax, ecx"); return
            if op in ('==','==='): Code.append("  cmove  eax, ecx"); return
            if op in ('!=','!=='): Code.append("  cmovne eax, ecx"); return

        if op == '&&':
            lbl_f = f"and_false_{self.id}"; lbl_e = f"and_end_{self.id}"
            Code.append("  cmp eax, 0")
            Code.append(f"  je {lbl_f}")
            Code.append("  cmp ecx, 0")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmovne eax, ecx")
            Code.append(f"  jmp {lbl_e}")
            Code.append(f"{lbl_f}:")
            Code.append("  mov eax, 0")
            Code.append(f"{lbl_e}:")
            return

        if op == '||':
            lbl_t = f"or_true_{self.id}"; lbl_e = f"or_end_{self.id}"
            Code.append("  cmp eax, 0")
            Code.append(f"  jne {lbl_t}")
            Code.append("  cmp ecx, 0")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmovne eax, ecx")
            Code.append(f"  jmp {lbl_e}")
            Code.append(f"{lbl_t}:")
            Code.append("  mov eax, 1")
            Code.append(f"{lbl_e}:")
            return

        raise Exception(f"[CodeGen] Operador '{op}' não suportado no gerador (strings não são geradas)")

# ---------- If / While / Block ----------
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
    def generate(self, st: SymbolTable) -> None:
        cond, then_block = self.children[0], self.children[1]
        else_block = self.children[2] if len(self.children) == 3 else None
        lbl_else = f"else_{self.id}"
        lbl_end  = f"endif_{self.id}"
        cond.generate(st)
        Code.append("  cmp eax, 0")
        if else_block is not None:
            Code.append(f"  je {lbl_else}")
            then_block.generate(st)
            Code.append(f"  jmp {lbl_end}")
            Code.append(f"{lbl_else}:")
            else_block.generate(st)
            Code.append(f"{lbl_end}:")
        else:
            Code.append(f"  je {lbl_end}")
            then_block.generate(st)
            Code.append(f"{lbl_end}:")

class While(Node):
    def __init__(self, cond: Node, body: Node):
        super().__init__('while', [cond, body])
    def evaluate(self, st: SymbolTable) -> None:
        while True:
            cond: Variable = self.children[0].evaluate(st)
            ensure_type(cond, 'boolean', 'while(cond)')
            if not cond.value: break
            self.children[1].evaluate(st)
    def generate(self, st: SymbolTable) -> None:
        cond, body = self.children
        lbl_loop = f"loop_{self.id}"
        lbl_exit = f"exit_{self.id}"
        Code.append(f"{lbl_loop}:")
        cond.generate(st)
        Code.append("  cmp eax, 0")
        Code.append(f"  je {lbl_exit}")
        body.generate(st)
        Code.append(f"  jmp {lbl_loop}")
        Code.append(f"{lbl_exit}:")

class Block(Node):
    def __init__(self, children: list[Node]): super().__init__('block', children)
    def evaluate(self, st: SymbolTable) -> None:
        for ch in self.children: ch.evaluate(st)
    def generate(self, st: SymbolTable) -> None:
        for ch in self.children: ch.generate(st)
