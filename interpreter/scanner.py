from typing import TYPE_CHECKING, ClassVar, Mapping, Optional

from .token import Token
from .token_type import TokenType

if TYPE_CHECKING:
    from .lox import Lox


class Scanner:
    keywords: ClassVar[Mapping[str, TokenType]] = {
        "break": TokenType.BREAK,
        "class": TokenType.CLASS,
        "continue": TokenType.CONTINUE,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fn": TokenType.FN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self: "Scanner", source: str, agent: "Lox"):
        self._tokens: list[Token] = []
        self._start: int = 0
        self._current: int = 0
        self._column: int = 0
        self._line: int = 1
        self._source: str = source
        self._agent: Lox = agent

    def scan_tokens(self: "Scanner") -> list[Token]:
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line, self._column))
        return self._tokens

    def _is_at_end(self: "Scanner") -> bool:
        return self._current >= len(self._source)

    def _scan_token(self: "Scanner") -> None:
        c: str = self._advance()
        match (c):
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-" if self._match("="):
                self._add_token(TokenType.MINUS_EQUAL)
            case "-" if self._match("-"):
                self._add_token(TokenType.DECREMENT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+" if self._match("="):
                self._add_token(TokenType.PLUS_EQUAL)
            case "+" if self._match("+"):
                self._add_token(TokenType.INCREMENT)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*" if self._match("="):
                self._add_token(TokenType.STAR_EQUAL)
            case "*" if self._match("*"):
                self._add_token(TokenType.POWER)
            case "*":
                self._add_token(TokenType.STAR)
            case "?":
                self._add_token(TokenType.QUESTION)
            case ":":
                self._add_token(TokenType.COLON)
            case "!" if self._match("="):
                self._add_token(TokenType.BANG_EQUAL)
            case "!":
                self._add_token(TokenType.BANG)
            case "=" if self._match("="):
                self._add_token(TokenType.EQUAL_EQUAL)
            case "=":
                self._add_token(TokenType.EQUAL)
            case "<" if self._match("<"):
                self._add_token(
                    TokenType.BIT_LSHIFT_EQUAL
                    if self._match("=")
                    else TokenType.BIT_LSHIFT
                )
            case "<" if self._match("="):
                self._add_token(TokenType.LESS_EQUAL)
            case "<":
                self._add_token(TokenType.LESS)
            case ">" if self._match("="):
                self._add_token(TokenType.GREATER_EQUAL)
            case ">" if self._match(">"):
                self._add_token(
                    TokenType.BIT_RSHIFT_EQUAL
                    if self._match("=")
                    else TokenType.BIT_RSHIFT
                )
            case ">":
                self._add_token(TokenType.GREATER)

            case "/" if self._match("/"):
                # A comment goes until the end of the line.
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()

            case "/" if self._match("*"):
                self._block_comment()
            case "/" if self._match("="):
                self._add_token(TokenType.SLASH_EQUAL)
            case "/":
                self._add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # Ignore whitespace.
                pass
            case "\n":
                self._line += 1
                self._column = 0
            case '"':
                self._string()
            case "&" if self._match("&"):
                self._add_token(TokenType.AND)
            case "&" if self._match("="):
                self._add_token(TokenType.BIT_AND_EQUAL)
            case "&":
                self._add_token(TokenType.BIT_AND)
            case "~":
                self._add_token(TokenType.BIT_NOT)
            case "|" if self._match("|"):
                self._add_token(TokenType.OR)
            case "|" if self._match("="):
                self._add_token(TokenType.BIT_OR_EQUAL)
            case "|":
                self._add_token(TokenType.BIT_OR)
            case "%" if self._match("="):
                self._add_token(TokenType.MODULO_EQUAL)
            case "%":
                self._add_token(TokenType.MODULO)
            case "^" if self._match("="):
                self._add_token(TokenType.BIT_XOR_EQUAL)
            case "^":
                self._add_token(TokenType.BIT_XOR)

            case _:
                if self._is_digit(c):
                    self._number()
                elif self._is_alpha(c):
                    self._identifier()
                else:
                    self._agent.error_on_line(
                        self._line, self._column, "Unexpected character."
                    )

    def _advance(self: "Scanner") -> str:
        self._current += 1
        self._column += 1
        return self._source[self._current - 1]

    def _add_token(
        self: "Scanner", type: TokenType, literal: Optional[object] = None
    ) -> None:
        text: str = self._source[self._start : self._current]
        self._tokens.append(Token(type, text, literal, self._line, self._column))

    def _match(self: "Scanner", expected: str) -> bool:
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self: "Scanner") -> str:
        if self._is_at_end():
            return "\0"
        return self._source[self._current]

    def _string(self: "Scanner") -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        if self._is_at_end():
            self._agent.error_on_line(self._line, self._column, "Unterminated string.")
            return

        # The closing ".
        self._advance()

        # Trim the surrounding quotes.
        value: str = self._source[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, value)

    def _is_digit(self: "Scanner", c: str) -> bool:
        return c >= "0" and c <= "9"

    def _number(self: "Scanner") -> None:
        while self._is_digit(self._peek()):
            self._advance()

        # Look for a fractional part.
        if self._peek() == ".":
            # Consume the "."
            self._advance()

            while self._is_digit(self._peek()):
                self._advance()

            self._add_token(
                TokenType.NUMBER, float(self._source[self._start : self._current])
            )
        else:
            self._add_token(
                TokenType.NUMBER, int(self._source[self._start : self._current])
            )

    def _peek_next(self: "Scanner") -> str:
        if self._current + 1 >= len(self._source):
            return "\0"
        return self._source[self._current + 1]

    def _identifier(self: "Scanner") -> None:
        while self._is_alpha_numeric(self._peek()):
            self._advance()

        text: str = self._source[self._start : self._current]
        type: TokenType = Scanner.keywords.get(text, TokenType.IDENTIFIER)
        self._add_token(type)

    def _is_alpha(self: "Scanner", c: str) -> bool:
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def _is_alpha_numeric(self: "Scanner", c: str) -> bool:
        return self._is_alpha(c) or self._is_digit(c)

    def _block_comment(self: "Scanner") -> None:
        while not (
            self._is_at_end() or self._peek() != "*" and self._peek_next() != "/"
        ):
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        self._advance()  # consume the "*"
        self._advance()  # consume the "/"
