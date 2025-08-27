# main.py
from dataclasses import dataclass
import sys

# ======================
#  Token
# ======================
@dataclass
class Token:
    kind: str        # 'INT' | 'PLUS' | 'MINUS' | 'EOF'
    value: int | str # int para INT; str para os demais


# ======================
#  Lexer
# ======================
class Lexer:
    """
    Análise léxica: separa o código-fonte em tokens sob demanda.
    Tokens aceitos neste roteiro: INT, PLUS, MINUS, EOF.
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
        Regras:
          - Ignora espaços
          - '+' -> (PLUS, '+')
          - '-' -> (MINUS, '-')
          - [0-9]+ -> (INT, valor inteiro)
          - Fim -> (EOF, '')
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

        # Qualquer outro caractere é inválido neste roteiro
        raise Exception(f"[Lexer] Invalid symbol '{c}' at position {self.position}")


# ======================
#  Parser
# ======================
class Parser:
    """
    Análise sintática: consome tokens do Lexer e verifica a aderência ao diagrama.
    Gramática (da aula/roteiro):
      Expression := INT { (PLUS | MINUS) INT }*
    Retorna o resultado numérico da expressão analisada.
    """
    lex: Lexer | None = None  # será inicializado em run()

    @staticmethod
    def parse_expression() -> int:
        if Parser.lex is None:
            raise Exception("[Parser] Lexer not initialized")

        # Garantir que temos um token atual
        if Parser.lex.next is None:
            Parser.lex.select_next()

        # Primeiro token deve ser número
        if Parser.lex.next.kind != 'INT':
            raise Exception(f"[Parser] Expected INT at start of expression, got {Parser.lex.next.kind}")

        result = Parser.lex.next.value
        Parser.lex.select_next()

        # { (PLUS | MINUS) INT }*
        while Parser.lex.next.kind in ('PLUS', 'MINUS'):
            op = Parser.lex.next.kind
            Parser.lex.select_next()

            if Parser.lex.next.kind != 'INT':
                # erro específico por operação ajuda na depuração
                raise Exception(f"[Parser] Expected INT after {op}, got {Parser.lex.next.kind}")

            if op == 'PLUS':
                result += Parser.lex.next.value
            else:
                result -= Parser.lex.next.value

            Parser.lex.select_next()

        return result

    @staticmethod
    def run(code: str) -> int:
        """
        Ponto de entrada do Parser.
        - Inicializa o Lexer
        - Posiciona no primeiro token
        - Executa parse_expression()
        - Verifica se toda a cadeia foi consumida (EOF)
        """
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
    # Entrada por ARGUMENTO, conforme pedido no roteiro
    if len(sys.argv) != 2:
        raise Exception('Uso: python main.py "1+2"')

    code = sys.argv[1]
    print(Parser.run(code))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Mensagens de erro claras com a origem ([Lexer]/[Parser])
        print(str(e))
