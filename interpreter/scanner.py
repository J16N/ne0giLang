from typing import Final, Optional, Mapping
from .token_type import TokenType
from .token import Token
from .lox import Lox


class Scanner:
    tokens: list[Token]
    start: int = 0
    current: int = 0
    line: int = 1

    keywords: Final[Mapping[str, TokenType]] = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source: Final[str] = source

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            Scanner.start = Scanner.current
            self.scan_token()

        Scanner.tokens.append(Token(TokenType.EOF, "", None, Scanner.line))
        return Scanner.tokens

    def is_at_end(self) -> bool:
        return Scanner.current >= len(self.source)

    def scan_token(self) -> None:
        c: str = self.advance()
        match (c):
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)

            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )

            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )

            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )

            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )

            case "/" if self.match("/"):
                # A comment goes until the end of the line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()

            case "/" if self.match("*"):
                self.block_comment()

            case "/":
                self.add_token(TokenType.SLASH)

            case " " | "\r" | "\t":
                # Ignore whitespace.
                pass

            case "\n":
                Scanner.line += 1

            case '"':
                self.string()

            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    Lox.error(Scanner.line, "Unexpected character.")

    def advance(self) -> str:
        Scanner.current += 1
        return self.source[Scanner.current - 1]

    def add_token(self, type: TokenType, literal: Optional[object] = None) -> None:
        text: str = self.source[Scanner.start : Scanner.current]
        Scanner.tokens.append(Token(type, text, literal, Scanner.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[Scanner.current] != expected:
            return False

        Scanner.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[Scanner.current]

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                Scanner.line += 1
            self.advance()

        if self.is_at_end():
            Lox.error(Scanner.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value: str = self.source[Scanner.start + 1 : Scanner.current - 1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, c: str) -> bool:
        return c >= "0" and c <= "9"

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(
            TokenType.NUMBER, float(self.source[Scanner.start : Scanner.current])
        )

    def peek_next(self) -> str:
        if Scanner.current + 1 >= len(self.source):
            return "\0"
        return self.source[Scanner.current + 1]

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text: str = self.source[Scanner.start : Scanner.current]
        type: TokenType = Scanner.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def is_alpha(self, c: str) -> bool:
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def block_comment(self) -> None:
        while not (self.is_at_end() or self.peek() != "*" and self.peek_next() != "/"):
            if self.peek() == "\n":
                Scanner.line += 1
            self.advance()
