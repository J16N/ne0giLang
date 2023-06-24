from typing import TYPE_CHECKING, Final, Optional

from .callable import Callable
from .environment import Environment
from .exceptions import Return
from .expr import Function as FunctionExpr

if TYPE_CHECKING:
    from .instance import Instance
    from .interpreter import Interpreter


class Function(Callable):
    def __init__(
        self: "Function",
        name: Optional[str],
        declaration: FunctionExpr,
        closure: Environment,
        is_initializer: bool = False,
    ):
        self._name: Final[Optional[str]] = name
        self._closure: Final[Environment] = closure
        self._declaration: Final[FunctionExpr] = declaration
        self._is_initializer: Final[bool] = is_initializer

    def __str__(self: "Function") -> str:
        if self._name is None:
            return "<fn>"
        return f"<fn {self._name}>"

    def arity(self: "Function") -> int:
        return len(self._declaration.params)

    def bind(self: "Function", instance: "Instance") -> "Function":
        environment: Environment = Environment(self._closure)
        environment.define("this", instance)
        return Function(
            self._name, self._declaration, environment, self._is_initializer
        )

    def call(
        self: "Function", interpreter: "Interpreter", arguments: list[object]
    ) -> object:
        environment: Environment = Environment(self._closure)
        for i in range(len(self._declaration.params)):
            environment.define(self._declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self._declaration.body, environment)
            if self._is_initializer:
                return self._closure.get_at(0, "this")
        except Return as r:
            if self._is_initializer:
                return self._closure.get_at(0, "this")

            return r.value
