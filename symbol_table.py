from dataclasses import dataclass
from typing import Dict

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
