from .token_type import TokenType
from typing import Final


class Token:
    def __init__(
        self: "Token", type: TokenType, lexeme: str, literal: object, line: int
    ):
        self.type: Final[TokenType] = type
        self.lexeme: Final[str] = lexeme
        self.literal: Final[object] = literal
        self.line: Final[int] = line

    def __repr__(self: "Token") -> str:
        return f"{self.type} {self.lexeme} {self.literal}"

    def __str__(self: "Token") -> str:
        return self.__repr__()
