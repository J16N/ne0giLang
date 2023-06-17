from typing import Final, TYPE_CHECKING
from .token import Token
from .token_type import TokenType
from .expr import Expr, Binary, Comma, Grouping, Literal, Ternary, Unary

if TYPE_CHECKING:
    from .lox import Lox


class ParseError(Exception):
    pass


class Parser:
    def __init__(self: "Parser", tokens: list[Token], agent: "Lox"):
        self._tokens: Final[list[Token]] = tokens
        self._current: int = 0
        self._agent = agent

    def parse(self: "Parser") -> Expr:
        return self._expression()

    def _expression(self: "Parser") -> Expr:
        return self._comma_expression()

    def _comma_expression(self: "Parser") -> Expr:
        expr: Expr = self._ternary()

        while self._match(TokenType.COMMA):
            operator: Token = self._previous()
            right_expr: Expr = self._ternary()
            expr = Comma(expr, operator, right_expr)

        return expr

    def _ternary(self: "Parser") -> Expr:
        expr: Expr = self._equality()

        while self._match(TokenType.QUESTION):
            then_branch: Expr = self._ternary()
            self._consume(TokenType.COLON, "Expected ':' after expression.")
            else_branch: Expr = self._ternary()
            expr = Ternary(expr, then_branch, else_branch)

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
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self: "Parser") -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)

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
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
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
