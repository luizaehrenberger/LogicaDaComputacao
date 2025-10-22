from dataclasses import dataclass

@dataclass
class Token:
    kind: str        # ver Lexer
    value: int | str
