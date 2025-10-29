from dataclasses import dataclass

@dataclass
class Token:
    kind: str
    value: int | str
