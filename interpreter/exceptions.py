from .token import Token
from typing import Final


class RuntimeError(Exception):
    def __init__(self: "RuntimeError", token: Token, message: str):
        self.token: Final[Token] = token
        self.message: Final[str] = message


class Break(Exception):
    pass


class Continue(Exception):
    pass


class Return(Exception):
    def __init__(self: "Return", value: object):
        super().__init__()
        self.value: Final[object] = value
