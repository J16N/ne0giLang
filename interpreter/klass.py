from typing import TYPE_CHECKING, Final, Optional

from .callable import Callable
from .function import Function
from .instance import Instance

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Class(Callable):
    def __init__(
        self: "Class",
        name: str,
        superclass: Optional["Class"],
        methods: dict[str, Function],
    ):
        self.name: Final[str] = name
        self.superclass: Final[Optional["Class"]] = superclass
        self.methods: Final[dict[str, Function]] = methods

    def __repr__(self: "Class") -> str:
        return f"<class {self.name}>"

    def __str__(self: "Class") -> str:
        return self.__repr__()

    def arity(self: "Class") -> int:
        intializer: Optional[Function] = self.find_method(self.name)
        return intializer.arity() if intializer else 0

    def call(
        self: "Class", interpreter: "Interpreter", arguments: list[object]
    ) -> object:
        instance: Instance = Instance(self)
        initializer: Optional[Function] = self.find_method(self.name)
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self: "Class", name: str) -> Optional[Function]:
        if name in self.methods:
            return self.methods.get(name)

        if self.superclass:
            return self.superclass.find_method(name)
