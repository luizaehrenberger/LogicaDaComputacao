from __future__ import annotations
from typing import List
from lexer import Lexer
from nodes import (
    Node, IntVal, StringVal, BoolVal, Identifier, NoOp, Print, Read, Assignment,
    UnOp, BinOp, If, While, Block, VarDec, Return, FuncDec, FuncCall
)

class Parser:
    lex: Lexer | None = None

    # ------ helpers ------
    @staticmethod
    def _expect(kind: str, msg: str):
        if Parser.lex.next.kind != kind:
            raise Exception(f"[Parser] {msg}: obtido {Parser.lex.next.kind}")
        Parser.lex.select_next()

    # ------- fatores -------
    @staticmethod
    def parse_factor() -> Node:
        tok = Parser.lex.next

        if tok.kind == 'NOT':
            Parser.lex.select_next()
            return UnOp('!', Parser.parse_factor())

        if tok.kind == 'PLUS':
            Parser.lex.select_next()
            return UnOp('+', Parser.parse_factor())
        if tok.kind == 'MINUS':
            Parser.lex.select_next()
            return UnOp('-', Parser.parse_factor())

        if tok.kind == 'OPEN_PAR':
            Parser.lex.select_next()
            node = Parser.parse_bool_expression()
            Parser._expect('CLOSE_PAR', "Esperado ')'")
            return node

        if tok.kind == 'INT':
            Parser.lex.select_next()
            return IntVal(tok.value)

        if tok.kind == 'STR':
            Parser.lex.select_next()
            return StringVal(tok.value)

        if tok.kind == 'BOOL':
            Parser.lex.select_next()
            return BoolVal(tok.value)

        if tok.kind == 'IDEN':
            name = tok.value
            Parser.lex.select_next()
            # fator pode ser: IDENT ou CHAMADA
            if Parser.lex.next.kind == 'OPEN_PAR':
                Parser.lex.select_next()  # '('
                args: List[Node] = []
                if Parser.lex.next.kind != 'CLOSE_PAR':
                    args.append(Parser.parse_bool_expression())
                    while Parser.lex.next.kind == 'COMMA':
                        Parser.lex.select_next()
                        args.append(Parser.parse_bool_expression())
                Parser._expect('CLOSE_PAR', "Esperado ')'")
                return FuncCall(name, args)
            else:
                return Identifier(name)

        if tok.kind == 'READ':
            Parser.lex.select_next()
            Parser._expect('OPEN_PAR', "Esperado '('")
            Parser._expect('CLOSE_PAR', "Esperado ')'")
            return Read()

        raise Exception(f"[Parser] Token inesperado em FACTOR: {tok.kind}")

    # ------- aritmética -------
    @staticmethod
    def parse_term() -> Node:
        left = Parser.parse_factor()
        while Parser.lex.next.kind in ('MULT', 'DIV', 'MOD'):
            opk = Parser.lex.next.kind
            Parser.lex.select_next()
            right = Parser.parse_factor()
            op = {'MULT': '*', 'DIV': '/', 'MOD': '%'}[opk]
            left = BinOp(op, left, right)
        return left

    @staticmethod
    def parse_expression() -> Node:
        left = Parser.parse_term()
        while Parser.lex.next.kind in ('PLUS', 'MINUS'):
            opk = Parser.lex.next.kind
            Parser.lex.select_next()
            right = Parser.parse_term()
            op = '+' if opk == 'PLUS' else '-'
            left = BinOp(op, left, right)
        return left

    # ------- relacionais -------
    @staticmethod
    def parse_rel_expression() -> Node:
        left = Parser.parse_expression()
        while Parser.lex.next.kind in ('EQUAL', 'NEQ', 'LT', 'GT', 'LE', 'GE', 'EQUAL_STRICT', 'NEQ_STRICT'):
            kind = Parser.lex.next.kind
            op = {
                'EQUAL': '==', 'NEQ': '!=',
                'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>=',
                'EQUAL_STRICT': '===', 'NEQ_STRICT': '!=='
            }[kind]
            Parser.lex.select_next()
            right = Parser.parse_expression()
            left = BinOp(op, left, right)
        return left

    # ------- booleanos -------
    @staticmethod
    def parse_bool_term() -> Node:
        left = Parser.parse_rel_expression()
        while Parser.lex.next.kind == 'AND':
            Parser.lex.select_next()
            right = Parser.parse_rel_expression()
            left = BinOp('&&', left, right)
        return left

    @staticmethod
    def parse_bool_expression() -> Node:
        left = Parser.parse_bool_term()
        while Parser.lex.next.kind == 'OR':
            Parser.lex.select_next()
            right = Parser.parse_bool_term()
            left = BinOp('||', left, right)
        return left

    # ------- bloco -------
    @staticmethod
    def parse_block() -> Node:
        Parser._expect('OPEN_BRA', "Esperado '{'")
        children: List[Node] = []
        while Parser.lex.next.kind != 'CLOSE_BRA':
            if Parser.lex.next.kind == 'OPEN_BRA':
                children.append(Parser.parse_block())
            else:
                children.append(Parser.parse_statement())
        Parser.lex.select_next()  # consumir '}'
        return Block(children)

    # ------- var decl -------
    @staticmethod
    def parse_var_declaration() -> Node:
        # Aceita:
        #   (A) let TYPE IDEN [= expr] ;
        #   (B) let IDEN : TYPE [= expr] ;
        if Parser.lex.next.kind != 'VAR':
            raise Exception(f"[Parser] Esperado 'let', obtido {Parser.lex.next.kind}")
        Parser.lex.select_next()

        vtype_text = None
        ident_name = None
        init_expr = None

        if Parser.lex.next.kind == 'TYPE':
            # Forma A
            vtype_text = Parser.lex.next.value
            Parser.lex.select_next()
            if Parser.lex.next.kind != 'IDEN':
                raise Exception(f"[Parser] Esperado IDENTIFIER após TYPE, obtido {Parser.lex.next.kind}")
            ident_name = Parser.lex.next.value
            Parser.lex.select_next()
        elif Parser.lex.next.kind == 'IDEN':
            # Forma B
            ident_name = Parser.lex.next.value
            Parser.lex.select_next()
            Parser._expect('COLON', "Esperado ':'")
            if Parser.lex.next.kind != 'TYPE':
                raise Exception(f"[Parser] Esperado TYPE (string|number|boolean|void), obtido {Parser.lex.next.kind}")
            vtype_text = Parser.lex.next.value
            Parser.lex.select_next()
        else:
            raise Exception(f"[Parser] Esperado TYPE ou IDENTIFIER após 'let', obtido {Parser.lex.next.kind}")

        if Parser.lex.next.kind == 'ASSIGN':
            Parser.lex.select_next()
            init_expr = Parser.parse_bool_expression()

        Parser._expect('END', "Esperado ';' ao final da declaração")
        return VarDec(vtype_text, Identifier(ident_name), init_expr)

    # ------- func decl -------
    @staticmethod
    def parse_func_declaration() -> Node:
        # function nome ( [id:TYPE {, id:TYPE}] ) : TYPE  { Block }
        Parser._expect('FUNC', "Esperado 'function'")
        if Parser.lex.next.kind != 'IDEN':
            raise Exception(f"[Parser] Esperado nome da função, obtido {Parser.lex.next.kind}")
        fname = Parser.lex.next.value
        Parser.lex.select_next()

        Parser._expect('OPEN_PAR', "Esperado '('")
        params: List[VarDec] = []
        if Parser.lex.next.kind != 'CLOSE_PAR':
            # pelo menos um param: id : TYPE
            if Parser.lex.next.kind != 'IDEN':
                raise Exception(f"[Parser] Esperado identificador de parâmetro, obtido {Parser.lex.next.kind}")
            p_name = Parser.lex.next.value
            Parser.lex.select_next()
            Parser._expect('COLON', "Esperado ':' após nome do parâmetro")
            if Parser.lex.next.kind != 'TYPE':
                raise Exception(f"[Parser] Esperado TYPE em parâmetro, obtido {Parser.lex.next.kind}")
            p_type = Parser.lex.next.value
            Parser.lex.select_next()
            params.append(VarDec(p_type, Identifier(p_name)))
            while Parser.lex.next.kind == 'COMMA':
                Parser.lex.select_next()
                if Parser.lex.next.kind != 'IDEN':
                    raise Exception(f"[Parser] Esperado identificador de parâmetro, obtido {Parser.lex.next.kind}")
                p_name = Parser.lex.next.value
                Parser.lex.select_next()
                Parser._expect('COLON', "Esperado ':' após nome do parâmetro")
                if Parser.lex.next.kind != 'TYPE':
                    raise Exception(f"[Parser] Esperado TYPE em parâmetro, obtido {Parser.lex.next.kind}")
                p_type = Parser.lex.next.value
                Parser.lex.select_next()
                params.append(VarDec(p_type, Identifier(p_name)))
        Parser._expect('CLOSE_PAR', "Esperado ')'")

        Parser._expect('COLON', "Esperado ':' após parâmetros")
        if Parser.lex.next.kind != 'TYPE':
            raise Exception(f"[Parser] Esperado TYPE de retorno (string|number|boolean|void), obtido {Parser.lex.next.kind}")
        ret_type = Parser.lex.next.value
        Parser.lex.select_next()

        body = Parser.parse_block()
        return FuncDec(ret_type, Identifier(fname), params, body)

    # ------- statement -------
    @staticmethod
    def parse_statement() -> Node:
        tok = Parser.lex.next

        if tok.kind == 'END':
            Parser.lex.select_next()
            return NoOp()

        if tok.kind == 'OPEN_BRA':
            return Parser.parse_block()

        if tok.kind == 'VAR':
            return Parser.parse_var_declaration()

        if tok.kind == 'PRINT':
            Parser.lex.select_next()
            Parser._expect('OPEN_PAR', "Esperado '('")
            expr = Parser.parse_bool_expression()
            Parser._expect('CLOSE_PAR', "Esperado ')'")
            Parser._expect('END', "Esperado ';'")
            return Print(expr)

        if tok.kind == 'IF':
            Parser.lex.select_next()
            Parser._expect('OPEN_PAR', "Esperado '('")
            cond = Parser.parse_bool_expression()
            Parser._expect('CLOSE_PAR', "Esperado ')'")
            then_block = Parser.parse_block()
            else_block = None
            if Parser.lex.next.kind == 'ELSE':
                Parser.lex.select_next()
                else_block = Parser.parse_block()
            return If(cond, then_block, else_block)

        if tok.kind == 'WHILE':
            Parser.lex.select_next()
            Parser._expect('OPEN_PAR', "Esperado '('")
            cond = Parser.parse_bool_expression()
            Parser._expect('CLOSE_PAR', "Esperado ')'")
            body = Parser.parse_block()
            return While(cond, body)

        if tok.kind == 'RETURN':
            Parser.lex.select_next()
            expr = Parser.parse_bool_expression()
            Parser._expect('END', "Esperado ';' após return")
            return Return(expr)

        if tok.kind == 'FUNC':
            return Parser.parse_func_declaration()

        if tok.kind == 'IDEN':
            name = tok.value
            Parser.lex.select_next()
            # pode ser atribuição OU chamada de função terminada em ';'
            if Parser.lex.next.kind == 'ASSIGN':
                Parser.lex.select_next()
                expr = Parser.parse_bool_expression()
                Parser._expect('END', "Esperado ';'")
                return Assignment(Identifier(name), expr)
            elif Parser.lex.next.kind == 'OPEN_PAR':
                Parser.lex.select_next()  # '('
                args: List[Node] = []
                if Parser.lex.next.kind != 'CLOSE_PAR':
                    args.append(Parser.parse_bool_expression())
                    while Parser.lex.next.kind == 'COMMA':
                        Parser.lex.select_next()
                        args.append(Parser.parse_bool_expression())
                Parser._expect('CLOSE_PAR', "Esperado ')'")
                Parser._expect('END', "Esperado ';'")
                return FuncCall(name, args)
            else:
                raise Exception(f"[Parser] Esperado '=' ou '(' após identificador em statement, obtido {Parser.lex.next.kind}")

        raise Exception(f"[Parser] Instrução inválida: inicia com {tok.kind}")

    # ------- programa -------
    @staticmethod
    def parse_program() -> Node:
        children: List[Node] = []
        while Parser.lex.next.kind != 'EOF':
            if Parser.lex.next.kind == 'FUNC':
                children.append(Parser.parse_func_declaration())
            elif Parser.lex.next.kind == 'OPEN_BRA':
                children.append(Parser.parse_block())
            elif Parser.lex.next.kind == 'VAR':
                children.append(Parser.parse_var_declaration())
            else:
                children.append(Parser.parse_statement())
        return Block(children)

    @staticmethod
    def run(code: str) -> Node:
        Parser.lex = Lexer(code)
        Parser.lex.select_next()
        root = Parser.parse_program()
        if Parser.lex.next.kind != 'EOF':
            raise Exception(f"[Parser] Token inesperado ao final: {Parser.lex.next.kind}")
        return root
