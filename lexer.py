from token_types import Token

class Lexer:
    RESERVED = {
        "log": "PRINT",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "readline": "READ",
    }

    def __init__(self, source: str):
        self.source: str = source
        self.position: int = 0
        self.next: Token | None = None

    def _current_char(self) -> str | None:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def _peek(self) -> str | None:
        i = self.position + 1
        if i >= len(self.source):
            return None
        return self.source[i]

    def select_next(self) -> None:
        c = self._current_char()

        # pular espaços
        while c is not None and c.isspace():
            self.position += 1
            c = self._current_char()

        if c is None:
            self.next = Token('EOF', '')
            return

        # --- 3 caracteres (tem que vir ANTES dos de 2) ---
        if c == '=' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position+2] == '='):
            self.position += 3
            self.next = Token('EQUAL_STRICT', '==='); return
        if c == '!' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position+2] == '='):
            self.position += 3
            self.next = Token('NEQ_STRICT', '!=='); return

        # --- 2 caracteres ---
        if c == '&' and self._peek() == '&':
            self.position += 2; self.next = Token('AND', '&&'); return
        if c == '|' and self._peek() == '|':
            self.position += 2; self.next = Token('OR', '||'); return
        if c == '=' and self._peek() == '=':
            self.position += 2; self.next = Token('EQUAL', '=='); return
        if c == '!' and self._peek() == '=':
            self.position += 2; self.next = Token('NEQ', '!='); return
        if c == '<' and self._peek() == '=':
            self.position += 2; self.next = Token('LE', '<='); return
        if c == '>' and self._peek() == '=':
            self.position += 2; self.next = Token('GE', '>='); return


        # operadores de 1 char
        if c == '+': self.position += 1; self.next = Token('PLUS', '+'); return
        if c == '-': self.position += 1; self.next = Token('MINUS', '-'); return
        if c == '*': self.position += 1; self.next = Token('MULT', '*'); return
        if c == '/': self.position += 1; self.next = Token('DIV', '/'); return
        if c == '%': self.position += 1; self.next = Token('MOD', '%'); return
        if c == '(': self.position += 1; self.next = Token('OPEN_PAR', '('); return
        if c == ')': self.position += 1; self.next = Token('CLOSE_PAR', ')'); return
        if c == '{': self.position += 1; self.next = Token('OPEN_BRA', '{'); return
        if c == '}': self.position += 1; self.next = Token('CLOSE_BRA', '}'); return
        if c == ';': self.position += 1; self.next = Token('END', ';'); return
        if c == '=': self.position += 1; self.next = Token('ASSIGN', '='); return
        if c == '!': self.position += 1; self.next = Token('NOT', '!'); return
        if c == '<': self.position += 1; self.next = Token('LT', '<'); return
        if c == '>': self.position += 1; self.next = Token('GT', '>'); return

        # números
        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self.position += 1
                c = self._current_char()
            self.next = Token('INT', int(self.source[start:self.position]))
            return

        # identificador
        if c.isalpha():
            start = self.position
            while c is not None and (c.isalnum() or c == '_'):
                self.position += 1
                c = self._current_char()
            ident = self.source[start:self.position]
            kind = self.RESERVED.get(ident, 'IDEN')
            self.next = Token(kind, ident)
            return

        if c == '_':
            raise Exception(f"[Lexer] Identificador inválido: não pode iniciar com '_' (pos {self.position})")

        raise Exception(f"[Lexer] Símbolo inválido '{c}' na posição {self.position}")
