from __future__ import annotations

class Variable:
    """
    Representa um valor tipado na linguagem.
    type ∈ {'number', 'boolean', 'string'}
    value: int | bool | str
    """
    __slots__ = ("type", "value", "is_const")

    def __init__(self, vtype: str, value, is_const: bool=False):
        if vtype not in ("number", "boolean", "string"):
            raise Exception(f"[SymbolTable] Tipo inválido: {vtype}")
        self.type = vtype
        self.value = value
        self.is_const = is_const  # reservado para 'const' (questionário)

    def __repr__(self) -> str:
        return f"Variable(type={self.type!r}, value={self.value!r})"


class SymbolTable:
    def __init__(self):
        self._table: dict[str, Variable] = {}

    # Roteiro 7: criar variáveis com tipo
    def create_variable(self, name: str, vtype: str) -> None:
        if name in self._table:
            raise Exception(f"[Semântico] Variável '{name}' já declarada")
        default = 0 if vtype == "number" else (False if vtype == "boolean" else "")
        self._table[name] = Variable(vtype, default)

    # Setter agora exige declaração prévia
    def set(self, name: str, var_value: Variable) -> None:
        if name not in self._table:
            raise Exception(f"[Semântico] Variável '{name}' não declarada")
        target = self._table[name]
        if target.is_const:
            raise Exception(f"[Semântico] Não é permitido atribuir em 'const' '{name}'")
        if target.type != var_value.type:
            raise Exception(
                f"[Semântico] Tipos incompatíveis em atribuição: esperado {target.type}, recebeu {var_value.type}"
            )
        target.value = var_value.value  # mantém o tipo

    def get(self, name: str) -> Variable:
        if name not in self._table:
            raise Exception(f"[Semântico] Variável '{name}' não declarada")
        return self._table[name]
