from dataclasses import dataclass
import sys

# ======================
#  Token
# ======================
@dataclass
class Token:
    kind: str        # 'INT' | 'PLUS' | 'MINUS' | 'MULT' | 'DIV' | 'OPEN_PAR' | 'CLOSE_PAR' | 'EOF'
    value: int | str # int para INT; str para os demais


# ======================
#  Lexer
# ======================
class Lexer:
    """
    Análise léxica: separa o código-fonte em tokens sob demanda.
    Tokens aceitos: INT, PLUS, MINUS, MULT, DIV, OPEN_PAR, CLOSE_PAR, EOF.
    Ignora espaços em branco.
    """
    def __init__(self, source: str):
        self.source: str = source
        self.position: int = 0
        self.next: Token | None = None

    def _current_char(self) -> str | None:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def select_next(self) -> None:
        """
        Lê o próximo token e atualiza self.next.
        """
        c = self._current_char()

        # Ignora espaços
        while c is not None and c.isspace():
            self.position += 1
            c = self._current_char()

        # Fim da entrada
        if c is None:
            self.next = Token('EOF', '')
            return

        # Símbolos simples
        if c == '+':
            self.position += 1
            self.next = Token('PLUS', '+')
            return

        if c == '-':
            self.position += 1
            self.next = Token('MINUS', '-')
            return

        if c == '*':
            self.position += 1
            self.next = Token('MULT', '*')
            return

        if c == '/':
            self.position += 1
            self.next = Token('DIV', '/')
            return

        if c == '(':
            self.position += 1
            self.next = Token('OPEN_PAR', '(')
            return

        if c == ')':
            self.position += 1
            self.next = Token('CLOSE_PAR', ')')
            return

        # Número inteiro (múltiplos dígitos)
        if c.isdigit():
            start = self.position
            while c is not None and c.isdigit():
                self.position += 1
                c = self._current_char()
            lexeme = self.source[start:self.position]
            try:
                value = int(lexeme)
            except ValueError:
                raise Exception(f"[Lexer] Invalid integer literal '{lexeme}'")
            self.next = Token('INT', value)
            return

        # Qualquer outro caractere é inválido
        raise Exception(f"[Lexer] Invalid symbol '{c}' at position {self.position}")


# ======================
#  Parser
# ======================
class Parser:
    """
    EBNF:
      EXPRESSION = TERM, { ("+" | "-"), TERM } ;
      TERM       = FACTOR, { ("*" | "/"), FACTOR } ;
      FACTOR     = ("+" | "-"), FACTOR | "(", EXPRESSION, ")" | NUMBER ;
    """
    lex: Lexer | None = None  # será inicializado em run()

    @staticmethod
    def _int_div_trunc_toward_zero(a: int, b: int) -> int:
        if b == 0:
            raise Exception("[Semântico] Divisão por zero")
        # truncamento em direção ao zero (ex.: -3/2 -> -1)
        return int(a / b)

    @staticmethod
    def parse_factor() -> int:
        if Parser.lex is None or Parser.lex.next is None:
            raise Exception("[Parser] Lexer not initialized")

        tok = Parser.lex.next

        # Operadores unários
        if tok.kind == 'PLUS':
            Parser.lex.select_next()
            val = Parser.parse_factor()
            return +val

        if tok.kind == 'MINUS':
            Parser.lex.select_next()
            val = Parser.parse_factor()
            return -val

        # Parênteses
        if tok.kind == 'OPEN_PAR':
            Parser.lex.select_next()
            val = Parser.parse_expression()
            if Parser.lex.next.kind != 'CLOSE_PAR':
                raise Exception(f"[Parser] Esperado ')', obtido {Parser.lex.next.kind}")
            Parser.lex.select_next()
            return val

        # Número
        if tok.kind == 'INT':
            val = tok.value
            Parser.lex.select_next()
            return val

        raise Exception(f"[Parser] Token inesperado em FACTOR: {tok.kind}")

    @staticmethod
    def parse_term() -> int:
        if Parser.lex is None or Parser.lex.next is None:
            raise Exception("[Parser] Lexer not initialized")

        result = Parser.parse_factor()

        while Parser.lex.next.kind in ('MULT', 'DIV'):
            op = Parser.lex.next.kind
            Parser.lex.select_next()
            rhs = Parser.parse_factor()

            if op == 'MULT':
                result = result * rhs
            else:  # DIV
                result = Parser._int_div_trunc_toward_zero(result, rhs)

        return result

    @staticmethod
    def parse_expression() -> int:
        if Parser.lex is None or Parser.lex.next is None:
            raise Exception("[Parser] Lexer not initialized")

        result = Parser.parse_term()

        while Parser.lex.next.kind in ('PLUS', 'MINUS'):
            op = Parser.lex.next.kind
            Parser.lex.select_next()
            rhs = Parser.parse_term()
            if op == 'PLUS':
                result = result + rhs
            else:
                result = result - rhs

        return result

    @staticmethod
    def run(code: str) -> int:
        Parser.lex = Lexer(code)
        Parser.lex.select_next()  # primeiro token
        result = Parser.parse_expression()

        if Parser.lex.next.kind != 'EOF':
            raise Exception(f"[Parser] Unexpected token {Parser.lex.next.kind} after end of expression")

        return result


# ======================
#  Main (CLI)
# ======================
def main():
    if len(sys.argv) != 2:
        raise Exception('Uso: python main.py "1+2"')

    code = sys.argv[1]
    print(Parser.run(code))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
