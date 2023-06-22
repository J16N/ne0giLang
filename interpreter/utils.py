import time
from .callable import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Clock(Callable):
    def arity(self: "Clock") -> int:
        return 0

    def call(self: "Clock", interpreter: "Interpreter", arguments: list[object]) -> int:
        return round(time.time())

    def __str__(self: "Clock") -> str:
        return "<native fn clock>"


class Print(Callable):
    def arity(self: "Print") -> int:
        return 1

    def call(
        self: "Print", interpreter: "Interpreter", arguments: list[object]
    ) -> None:
        if len(arguments) != 1:
            raise TypeError(
                f"Expected {self.arity()} argument, but got {len(arguments)} instead."
            )
        value: object = arguments[0]
        print(interpreter.stringify(value) if not isinstance(value, str) else value)

    def __str__(self: "Print") -> str:
        return "<native fn print>"
