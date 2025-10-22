from __future__ import annotations

class Variable:
    """
    type ∈ {'number','boolean','string'}
    value: int|bool|str (para interpretador)
    shift: deslocamento [EBP-shift] (para codegen), múltiplos de 4
    """
    __slots__ = ("type", "value", "is_const", "shift")

    def __init__(self, vtype: str, value, is_const: bool=False, shift: int | None = None):
        if vtype not in ("number", "boolean", "string"):
            raise Exception(f"[SymbolTable] Tipo inválido: {vtype}")
        self.type = vtype
        self.value = value
        self.is_const = is_const
        self.shift = shift

    def __repr__(self) -> str:
        return f"Variable(type={self.type!r}, value={self.value!r}, shift={self.shift!r})"


class SymbolTable:
    def __init__(self):
        self._table: dict[str, Variable] = {}
        self._next_shift: int = 0  # em bytes (4,8,12,...)

    def create_variable(self, name: str, vtype: str) -> None:
        if name in self._table:
            raise Exception(f"[Semantic] Variável '{name}' já declarada")
        self._next_shift += 4
        default = 0 if vtype == "number" else (False if vtype == "boolean" else "")
        self._table[name] = Variable(vtype, default, False, self._next_shift)

    def set(self, name: str, var_value: Variable) -> None:
        if name not in self._table:
            raise Exception(f"[Semantic] Variável '{name}' não declarada")
        target = self._table[name]
        if target.is_const:
            raise Exception(f"[Semantic] Não é permitido atribuir em 'const' '{name}'")
        if target.type != var_value.type:
            raise Exception(
                f"[Semantic] Tipos incompatíveis em atribuição: esperado {target.type}, recebeu {var_value.type}"
            )
        target.value = var_value.value

    def get(self, name: str) -> Variable:
        if name not in self._table:
            raise Exception(f"[Semantic] Variável '{name}' não declarada")
        return self._table[name]
