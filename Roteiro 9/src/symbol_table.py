from __future__ import annotations
from typing import Optional

class Variable:
    __slots__ = ("type", "value", "is_const", "shift", "is_function")

    def __init__(self, vtype: str, value, is_const: bool=False, shift: int | None=None, *, is_function: bool=False):
        if is_function:
            if vtype not in ("number", "boolean", "string", "void"):
                raise Exception(f"[SymbolTable] Tipo de retorno inválido para função: {vtype}")
        else:
            if vtype not in ("number", "boolean", "string"):
                raise Exception(f"[SymbolTable] Tipo inválido: {vtype}")
        self.type = vtype
        self.value = value
        self.is_const = is_const
        self.shift = shift
        self.is_function = is_function

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable']=None):
        self.parent = parent
        self._table = {}
        self._next_shift = 0

    def create_variable(self, name: str, vtype: str):
        if name in self._table:
            raise Exception(f"[Semantic] Variável '{name}' já declarada")
        self._next_shift += 4
        default = 0 if vtype == "number" else (False if vtype == "boolean" else "")
        self._table[name] = Variable(vtype, default, False, self._next_shift)

    def create_function(self, name: str, return_type: str, func_node):
        if name in self._table:
            raise Exception(f"[Semantic] Identificador '{name}' já declarado")
        self._table[name] = Variable(return_type, func_node, is_const=True, shift=None, is_function=True)

    def get(self, name: str) -> Variable:
        if name in self._table:
            return self._table[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise Exception(f"[Semantic] Identificador '{name}' não declarado")

    def set(self, name: str, var_value: Variable):
        if name in self._table:
            target = self._table[name]
            if target.is_function:
                raise Exception(f"[Semantic] '{name}' é uma função, não pode receber atribuição")
            if target.is_const:
                raise Exception(f"[Semantic] Não é permitido atribuir em 'const' '{name}'")
            if target.type != var_value.type:
                raise Exception(f"[Semantic] Tipos incompatíveis em atribuição: esperado {target.type}, recebeu {var_value.type}")
            target.value = var_value.value
            return
        if self.parent is not None:
            self.parent.set(name, var_value)
            return
        raise Exception(f"[Semantic] Identificador '{name}' não declarado")
