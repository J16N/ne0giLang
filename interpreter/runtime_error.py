from .token import Token
from typing import Final


class RuntimeError(Exception):
    def __init__(self: "RuntimeError", token: Token, message: str):
        self.token: Final[Token] = token
        self.message: Final[str] = message
