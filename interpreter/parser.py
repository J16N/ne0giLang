from typing import TYPE_CHECKING, Final, Optional

from .expr import Assign, Binary, Call, Comma, Expr
from .expr import Function as FunctionExpr
from .expr import Get, Grouping, Literal, Logical, Set, Ternary, This, Unary, Variable
from .stmt import Block, Break
from .stmt import Class as ClassStmt
from .stmt import Continue, Expression, For
from .stmt import Function as FunctionStmt
from .stmt import If, MultiVar, Return, Stmt, Var, While
from .token import Token
from .token_type import TokenType

if TYPE_CHECKING:
    from .lox import Lox


class ParseError(Exception):
    pass


class Parser:
    def __init__(self: "Parser", tokens: list[Token], agent: "Lox"):
        self._tokens: Final[list[Token]] = tokens
        self._current: int = 0
        self._agent: Final["Lox"] = agent
        self._loop_depth: int = 0

    def parse(self: "Parser") -> list[Optional[Stmt]]:
        statements: list[Optional[Stmt]] = []

        while not self._is_at_end():
            statements.append(self._declaration())

        return statements

    def _declaration(self: "Parser") -> Optional[Stmt]:
        try:
            if self._match(TokenType.CLASS):
                return self._class()

            if self._match(TokenType.FN):
                return self._function("function")

            if self._match(TokenType.VAR):
                return self._multi_var_declaration()

            return self._statement()

        except ParseError:
            self._synchronize()

    def _class(self: "Parser") -> ClassStmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expected class name.")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before class body.")

        methods: list[FunctionStmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after class body.")
        return ClassStmt(name, methods)

    def _function(self: "Parser", kind: str) -> FunctionStmt:
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expected {kind} name.")
        return FunctionStmt(name, self._function_body(kind))

    def _function_body(self: "Parser", kind: str) -> FunctionExpr:
        self._consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind}.")
        parameters: list[Token] = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 parameters.")

                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expected parameter name.")
                )

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body.")
        body: list[Optional[Stmt]] = self._block()
        return FunctionExpr(parameters, body)

    def _multi_var_declaration(self: "Parser") -> Stmt:
        multi_var: MultiVar = MultiVar()
        multi_var.add(self._var_declaration())

        while self._match(TokenType.COMMA):
            multi_var.add(self._var_declaration())

        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return multi_var

    def _var_declaration(self: "Parser") -> Var:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expected variable name.")

        initializer: Optional[Expr] = None
        if self._match(TokenType.EQUAL):
            initializer = self._assignment()

        return Var(name, initializer)

    def _statement(self: "Parser") -> Optional[Stmt]:
        if self._match(TokenType.BREAK):
            return self._break_statement()

        if self._match(TokenType.CONTINUE):
            return self._continue_statement()

        if self._match(TokenType.FOR):
            return self._for_statement()

        if self._match(TokenType.IF):
            return self._if_statement()

        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())

        if self._match(TokenType.RETURN):
            return self._return_statement()

        if self._match(TokenType.SEMICOLON):
            return

        if self._match(TokenType.WHILE):
            return self._while_statement()

        return self._expression_statement()

    def _break_statement(self: "Parser") -> Stmt:
        if self._loop_depth == 0:
            raise ParseError("Cannot break outside of a loop.")
        self._consume(TokenType.SEMICOLON, "Expected ';' after 'break'.")
        return Break()

    def _continue_statement(self: "Parser") -> Stmt:
        if self._loop_depth == 0:
            raise ParseError("Cannot continue outside of a loop.")
        self._consume(TokenType.SEMICOLON, "Expected ';' after 'continue'.")
        return Continue()

    def _for_statement(self: "Parser") -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        initializer: Optional[Stmt] = None
        if self._match(TokenType.VAR):
            initializer = self._multi_var_declaration()
        elif not self._match(TokenType.SEMICOLON):
            initializer = self._expression_statement()

        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment: Optional[Expr] = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for clause.")

        try:
            self._loop_depth += 1
            body: Optional[Stmt] = self._statement()
            return Block([For(initializer, condition, increment, body)])

        finally:
            self._loop_depth -= 1

    def _if_statement(self: "Parser") -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        then_branch: Optional[Stmt] = self._statement()
        else_branch: Optional[Stmt] = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _block(self: "Parser") -> list[Optional[Stmt]]:
        statements: list[Optional[Stmt]] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statement: Optional[Stmt] = self._declaration()
            statements.append(statement)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def _return_statement(self: "Parser") -> Stmt:
        keyword: Token = self._previous()
        value: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)

    def _while_statement(self: "Parser") -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")

        try:
            self._loop_depth += 1
            body: Optional[Stmt] = self._statement()
            return While(condition, body)

        finally:
            self._loop_depth -= 1

    def _expression_statement(self: "Parser") -> Stmt:
        expr: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    def _expression(self: "Parser") -> Expr:
        return self._comma_expression()

    def _comma_expression(self: "Parser") -> Expr:
        expr: Expr = self._assignment()

        while self._match(TokenType.COMMA):
            operator: Token = self._previous()
            right_expr: Expr = self._assignment()
            expr = Comma(expr, operator, right_expr)

        return expr

    def _assignment(self: "Parser") -> Expr:
        expr: Expr = self._ternary()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)

            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _ternary(self: "Parser") -> Expr:
        expr: Expr = self._or()

        while self._match(TokenType.QUESTION):
            then_branch: Expr = self._assignment()
            self._consume(TokenType.COLON, "Expected ':' after expression.")
            else_branch: Expr = self._assignment()
            expr = Ternary(expr, then_branch, else_branch)

        return expr

    def _or(self: "Parser") -> Expr:
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self: "Parser") -> Expr:
        expr: Expr = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self: "Parser") -> Expr:
        expr: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self: "Parser") -> Expr:
        expr: Expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self._previous()
            right: Expr = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self: "Parser") -> Expr:
        expr: Expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self: "Parser") -> Expr:
        expr: Expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self: "Parser") -> Expr:
        if self._match(
            TokenType.BANG,
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.INCREMENT,
            TokenType.DECREMENT,
        ):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._exponent()
    
    def _exponent(self: "Parser") -> Expr:
        expr: Expr = self._call()

        while self._match(TokenType.POWER):
            operator: Token = self._previous()
            right: Expr = self._call()
            expr = Binary(expr, operator, right)

        return expr

    def _call(self: "Parser") -> Expr:
        expr: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)

            elif self._match(TokenType.DOT):
                name: Token = self._consume(
                    TokenType.IDENTIFIER, "Expected property name."
                )
                expr = Get(expr, name)

            else:
                break

        return expr

    def _finish_call(self: "Parser", callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 arguments.")
                arguments.append(self._assignment())
                if not self._match(TokenType.COMMA):
                    break

        paren: Token = self._consume(
            TokenType.RIGHT_PAREN, "Expected ')' after arguments."
        )
        return Call(callee, paren, arguments)

    def _primary(self: "Parser") -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)

        if self._match(TokenType.FN):
            return self._function_body("function")

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)

        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.THIS):
            return This(self._previous())

        if self._match(TokenType.TRUE):
            return Literal(True)

        raise self._error(self._peek(), "Expected expression.")

    def _match(self: "Parser", *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _consume(self: "Parser", type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(self: "Parser", token: Token, message: str) -> ParseError:
        self._agent.error_on_token(token, message)
        return ParseError()

    def _synchronize(self: "Parser") -> None:
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            match self._peek().type:
                case TokenType.CLASS | TokenType.FN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.RETURN:
                    return

                case _:
                    ...

            self._advance()

    def _check(self: "Parser", type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self: "Parser") -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self: "Parser") -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self: "Parser") -> Token:
        return self._tokens[self._current]

    def _previous(self: "Parser") -> Token:
        return self._tokens[self._current - 1]
