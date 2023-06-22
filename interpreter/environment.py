from typing import Final, Optional
from .exceptions import RuntimeError
from .token import Token
from .types import Uninitialized


class Environment:
    def __init__(
        self: "Environment", enclosing: Optional["Environment"] = None
    ) -> None:
        self._values: Final[dict[str, object]] = {}
        self._enclosing: Optional["Environment"] = enclosing

    def ancestor(self: "Environment", distance: int) -> "Environment":
        environment: "Environment" = self
        for _ in range(distance):
            if environment._enclosing is None:
                break
            environment = environment._enclosing
        return environment

    def assign(self: "Environment", name: Token, value: object) -> None:
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return

        if self._enclosing:
            self._enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(
        self: "Environment", distance: int, name: Token, value: object
    ) -> None:
        self.ancestor(distance).assign(name, value)

    def get(self: "Environment", name: Token) -> object:
        var: str = name.lexeme
        if var in self._values:
            value: object = self._values[var]
            if not isinstance(value, Uninitialized):
                return self._values[var]
            raise RuntimeError(name, f"Cannot access '{var}' before initialization.")

        if self._enclosing:
            return self._enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self: "Environment", distance: int, name: str) -> Optional[object]:
        return self.ancestor(distance)._values.get(name)

    def define(self: "Environment", name: str, value: object) -> None:
        self._values[name] = value
