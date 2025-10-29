from token_types import Token

class Lexer:
    RESERVED = {
        "log": "PRINT",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "readline": "READ",
        "let": "VAR",
        "true": "BOOL",
        "false": "BOOL",
        "string": "TYPE",
        "number": "TYPE",
        "boolean": "TYPE",
        "function": "FUNC",
        "return": "RETURN",
        "void": "TYPE",
    }

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.next = None

    def _current_char(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def _peek(self):
        i = self.position + 1
        if i >= len(self.source):
            return None
        return self.source[i]

    def _advance(self, n: int = 1):
        self.position += n

    def _string_literal(self):
        self._advance()
        chars = []
        while True:
            c = self._current_char()
            if c is None:
                raise Exception("[Lexer] String não terminada")
            if c == '"':
                self._advance()
                return "".join(chars)
            if c == '\\':
                nxt = self._peek()
                if nxt is None:
                    raise Exception("[Lexer] Escape inválido no final da string")
                if nxt in ['"', '\\', 'n', 't', 'r']:
                    self._advance()
                    map_ = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r'}
                    chars.append(map_[self._current_char()])
                    self._advance()
                else:
                    raise Exception(f"[Lexer] Escape inválido '\\{nxt}'")
                continue
            chars.append(c)
            self._advance()

    def select_next(self):
        c = self._current_char()
        while c is not None and c.isspace():
            self._advance()
            c = self._current_char()
        if c is None:
            self.next = Token('EOF', '')
            return
        if c == '"':
            s = self._string_literal()
            self.next = Token('STR', s)
            return
        if c == '=' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position + 2] == '='):
            self._advance(3)
            self.next = Token('EQUAL_STRICT', '===')
            return
        if c == '!' and self._peek() == '=' and (self.position + 2 < len(self.source) and self.source[self.position + 2] == '='):
            self._advance(3)
            self.next = Token('NEQ_STRICT', '!==')
            return
        if c == '&' and self._peek() == '&':
            self._advance(2)
            self.next = Token('AND', '&&')
            return
        if c == '|' and self._peek() == '|':
            self._advance(2)
            self.next = Token('OR', '||')
            return
        if c == '=' and self._peek() == '=':
            self._advance(2)
            self.next = Token('EQUAL', '==')
            return
        if c == '!' and self._peek() == '=':
            self._advance(2)
            self.next = Token('NEQ', '!=')
            return
        if c == '<' and self._peek() == '=':
            self._advance(2)
            self.next = Token('LE', '<=')
            return
        if c == '>' and self._peek() == '=':
            self._advance(2)
            self.next = Token('GE', '>=')
            return
        if c == '+':
            self._advance()
            self.next = Token('PLUS', '+')
            return
        if c == '-':
            self._advance()
            self.next = Token('MINUS', '-')
            return
        if c == '*':
            self._advance()
            self.next = Token('MULT', '*')
            return
        if c == '/':
            self._advance()
            self.next = Token('DIV', '/')
            return
        if c == '%':
            self._advance()
            self.next = Token('MOD', '%')
            return
        if c == '(':
            self._advance()
            self.next = Token('OPEN_PAR', '(')
            return
        if c == ')':
            self._advance()
            self.next = Token('CLOSE_PAR', ')')
            return
        if c == '{':
            self._advance()
            self.next = Token('OPEN_BRA', '{')
            return
        if c == '}':
            self._advance()
            self.next = Token('CLOSE_BRA', '}')
            return
        if c == ';':
            self._advance()
            self.next = Token('END', ';')
            return
        if c == ':':
            self._advance()
            self.next = Token('COLON', ':')
            return
        if c == ',':
            self._advance()
            self.next = Token('COMMA', ',')
            return
        if c == '=':
            self._advance()
            self.next = Token('ASSIGN', '=')
            return
        if c == '!':
            self._advance()
            self.next = Token('NOT', '!')
            return
        if c == '<':
            self._advance()
            self.next = Token('LT', '<')
            return
        if c == '>':
            self._advance()
            self.next = Token('GT', '>')
            return
        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self._advance()
                c = self._current_char()
            self.next = Token('INT', int(self.source[start:self.position] or "0"))
            return
        if c.isalpha():
            start = self.position
            while c is not None and (c.isalnum() or c == '_'):
                self._advance()
                c = self._current_char()
            ident = self.source[start:self.position]
            kind = self.RESERVED.get(ident, 'IDEN')
            if kind == 'BOOL':
                self.next = Token('BOOL', True if ident == 'true' else False)
                return
            self.next = Token(kind, ident)
            return
        if c == '_':
            raise Exception(f"[Lexer] Identificador inválido: não pode iniciar com '_' (pos {self.position})")
        raise Exception(f"[Lexer] Símbolo inválido '{c}' na posição {self.position}")
