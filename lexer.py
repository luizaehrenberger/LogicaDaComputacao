from token_types import Token

class Lexer:
    RESERVED = {
        "log": "PRINT",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "readline": "READ",
        # Roteiro 7:
        "let": "VAR",
        "true": "BOOL",
        "false": "BOOL",
        "string": "TYPE",
        "number": "TYPE",
        "boolean": "TYPE",
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

    def _advance(self, n: int = 1) -> None:
        self.position += n

    def _string_literal(self) -> str:
        # Consome '"' atual e lê até o próximo '"'
        # Suporta escape simples \" e \\.
        self._advance()  # consumir "
        chars = []
        while True:
            c = self._current_char()
            if c is None:
                raise Exception("[Lexer] String não terminada")
            if c == '"':
                self._advance()
                return "".join(chars)
            if c == '\\':  # escape
                nxt = self._peek()
                if nxt is None:
                    raise Exception("[Lexer] Escape inválido no final da string")
                if nxt in ['"', '\\', 'n', 't', 'r']:
                    self._advance()  # consome '\'
                    map_ = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r'}
                    chars.append(map_[self._current_char()])
                    self._advance()
                else:
                    raise Exception(f"[Lexer] Escape inválido '\\{nxt}'")
                continue
            chars.append(c)
            self._advance()

    def select_next(self) -> None:
        c = self._current_char()

        # pular espaços
        while c is not None and c.isspace():
            self._advance()
            c = self._current_char()

        if c is None:
            self.next = Token('EOF', '')
            return

        # --- string literal ---
        if c == '"':
            s = self._string_literal()
            self.next = Token('STR', s)
            return

        # --- 3 caracteres ---
        if c == '=' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position+2] == '='):
            self._advance(3); self.next = Token('EQUAL_STRICT', '==='); return
        if c == '!' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position+2] == '='):
            self._advance(3); self.next = Token('NEQ_STRICT', '!=='); return

        # --- 2 caracteres ---
        if c == '&' and self._peek() == '&':
            self._advance(2); self.next = Token('AND', '&&'); return
        if c == '|' and self._peek() == '|':
            self._advance(2); self.next = Token('OR', '||'); return
        if c == '=' and self._peek() == '=':
            self._advance(2); self.next = Token('EQUAL', '=='); return
        if c == '!' and self._peek() == '=':
            self._advance(2); self.next = Token('NEQ', '!='); return
        if c == '<' and self._peek() == '=':
            self._advance(2); self.next = Token('LE', '<='); return
        if c == '>' and self._peek() == '=':
            self._advance(2); self.next = Token('GE', '>='); return

        # operadores de 1 char
        if c == '+': self._advance(); self.next = Token('PLUS', '+'); return
        if c == '-': self._advance(); self.next = Token('MINUS', '-'); return
        if c == '*': self._advance(); self.next = Token('MULT', '*'); return
        if c == '/': self._advance(); self.next = Token('DIV', '/'); return
        if c == '%': self._advance(); self.next = Token('MOD', '%'); return
        if c == '(': self._advance(); self.next = Token('OPEN_PAR', '('); return
        if c == ')': self._advance(); self.next = Token('CLOSE_PAR', ')'); return
        if c == '{': self._advance(); self.next = Token('OPEN_BRA', '{'); return
        if c == '}': self._advance(); self.next = Token('CLOSE_BRA', '}'); return
        if c == ';': self._advance(); self.next = Token('END', ';'); return
        if c == '=': self._advance(); self.next = Token('ASSIGN', '='); return
        if c == '!': self._advance(); self.next = Token('NOT', '!'); return
        if c == '<': self._advance(); self.next = Token('LT', '<'); return
        if c == '>': self._advance(); self.next = Token('GT', '>'); return

        # números
        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self._advance()
                c = self._current_char()
            self.next = Token('INT', int(self.source[start:self.position] or "0"))
            return

        # identificador / palavra reservada / tipo / bool
        if c.isalpha():
            start = self.position
            while c is not None and (c.isalnum() or c == '_'):
                self._advance()
                c = self._current_char()
            ident = self.source[start:self.position]
            kind = self.RESERVED.get(ident, 'IDEN')
            # BOOL tem valor True/False no token
            if kind == 'BOOL':
                self.next = Token('BOOL', True if ident == 'true' else False); return
            self.next = Token(kind, ident)
            return

        if c == '_':
            raise Exception(f"[Lexer] Identificador inválido: não pode iniciar com '_' (pos {self.position})")

        raise Exception(f"[Lexer] Símbolo inválido '{c}' na posição {self.position}")
