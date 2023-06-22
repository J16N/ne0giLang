from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Callable(ABC):
    @abstractmethod
    def arity(self: "Callable") -> int:
        ...

    @abstractmethod
    def call(
        self: "Callable", interpreter: "Interpreter", arguments: list[object]
    ) -> object:
        ...
