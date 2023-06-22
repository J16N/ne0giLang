from typing import Final

from .token_type import TokenType


class Token:
    def __init__(
        self: "Token", type: TokenType, lexeme: str, literal: object, line: int
    ):
        self.type: Final[TokenType] = type
        self.lexeme: Final[str] = lexeme
        self.literal: Final[object] = literal
        self.line: Final[int] = line

    def __repr__(self: "Token") -> str:
        return f"Token(type={self.type.name}, lexeme='{self.lexeme}', literal={self.literal})"

    def __str__(self: "Token") -> str:
        return self.__repr__()

    def __hash__(self: "Token") -> int:
        return hash(f"{self.type}{self.lexeme}")

    def __eq__(self: "Token", other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.lexeme == other.lexeme
