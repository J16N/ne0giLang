from typing import TYPE_CHECKING, Final, Optional

from .exceptions import RuntimeError
from .token import Token

if TYPE_CHECKING:
    from .function import Function
    from .klass import Class


class Instance:
    def __init__(self: "Instance", klass: "Class"):
        self.klass: Final["Class"] = klass
        self._fields: Final[dict[str, object]] = {}

    def __repr__(self: "Instance") -> str:
        return f"<{self.klass.name} instance>"

    def __str__(self: "Instance") -> str:
        return self.__repr__()

    def get(self: "Instance", name: Token) -> Optional[object]:
        if name.lexeme in self._fields:
            return self._fields[name.lexeme]

        method: Optional["Function"] = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self: "Instance", name: Token, value: object) -> None:
        self._fields[name.lexeme] = value
