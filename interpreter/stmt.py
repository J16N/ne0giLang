from abc import ABC, abstractmethod
from typing import Final, Generic, Optional, TypeVar

from .expr import Expr
from .expr import Function as FunctionExpr
from .token import Token

T = TypeVar("T")


class Stmt(ABC):
    @abstractmethod
    def accept(self: "Stmt", visitor: "Visitor[T]") -> T:
        ...


class Block(Stmt):
    def __init__(self: "Block", statements: list[Optional[Stmt]]):
        self.statements: Final[list[Optional[Stmt]]] = statements

    def accept(self: "Block", visitor: "Visitor[T]") -> T:
        return visitor.visit_block_stmt(self)


class Break(Stmt):
    def accept(self: "Break", visitor: "Visitor[T]") -> T:
        return visitor.visit_break_stmt()


# class Class(Stmt):
#     def __init__(self: "Class", name: Token, methods: list["Function"]):
#         self.name: Final[Token] = name
#         self.methods: Final[list["Function"]] = methods

#     def accept(self: "Class", visitor: "Visitor[T]") -> T:
#         return visitor.visit_class_stmt(self)


class Continue(Stmt):
    def accept(self: "Continue", visitor: "Visitor[T]") -> T:
        return visitor.visit_continue_stmt()


class Expression(Stmt):
    def __init__(self: "Expression", expression: Expr):
        self.expression: Final[Expr] = expression

    def accept(self: "Expression", visitor: "Visitor[T]") -> T:
        return visitor.visit_expression_stmt(self)


class For(Stmt):
    def __init__(
        self: "For",
        initializer: Optional[Stmt],
        condition: Optional[Expr],
        increment: Optional[Expr],
        body: Optional[Stmt],
    ):
        self.initializer: Final[Optional[Stmt]] = initializer
        self.condition: Final[Optional[Expr]] = condition
        self.increment: Final[Optional[Expr]] = increment
        self.body: Final[Optional[Stmt]] = body

    def accept(self: "For", visitor: "Visitor[T]") -> T:
        return visitor.visit_for_stmt(self)


class Function(Stmt):
    def __init__(self: "Function", name: Token, function: FunctionExpr):
        self.name: Final[Token] = name
        self.function: Final[FunctionExpr] = function

    def accept(self: "Function", visitor: "Visitor[T]") -> T:
        return visitor.visit_function_stmt(self)


class If(Stmt):
    def __init__(
        self: "If",
        condition: Expr,
        then_branch: Optional[Stmt],
        else_branch: Optional[Stmt],
    ):
        self.condition: Final[Expr] = condition
        self.then_branch: Final[Optional[Stmt]] = then_branch
        self.else_branch: Final[Optional[Stmt]] = else_branch

    def accept(self: "If", visitor: "Visitor[T]") -> T:
        return visitor.visit_if_stmt(self)


class Return(Stmt):
    def __init__(self: "Return", keyword: Token, value: Optional[Expr]):
        self.keyword: Final[Token] = keyword
        self.value: Final[Optional[Expr]] = value

    def accept(self: "Return", visitor: "Visitor[T]") -> T:
        return visitor.visit_return_stmt(self)


class MultiVar(Stmt):
    def __init__(self: "MultiVar"):
        self.variables: Final[list["Var"]] = []

    def add(self: "MultiVar", variable: "Var") -> None:
        self.variables.append(variable)

    def accept(self: "MultiVar", visitor: "Visitor[T]") -> T:
        return visitor.visit_multi_var_stmt(self)


class Var(Stmt):
    def __init__(self: "Var", name: Token, initializer: Optional[Expr]):
        self.name: Final[Token] = name
        self.initializer: Final[Optional[Expr]] = initializer

    def accept(self: "Var", visitor: "Visitor[T]") -> T:
        return visitor.visit_var_stmt(self)


class While(Stmt):
    def __init__(self: "While", condition: Expr, body: Optional[Stmt]):
        self.condition: Final[Expr] = condition
        self.body: Final[Optional[Stmt]] = body

    def accept(self: "While", visitor: "Visitor[T]") -> T:
        return visitor.visit_while_stmt(self)


class Visitor(ABC, Generic[T]):
    @abstractmethod
    def visit_block_stmt(self: "Visitor[T]", stmt: Block) -> T:
        ...

    @abstractmethod
    def visit_break_stmt(self: "Visitor[T]") -> T:
        ...

    # @abstractmethod
    # def visit_class_stmt(self: "Visitor[T]", stmt: Class) -> T:
    #     ...

    @abstractmethod
    def visit_continue_stmt(self: "Visitor[T]") -> T:
        ...

    @abstractmethod
    def visit_expression_stmt(self: "Visitor[T]", stmt: Expression) -> T:
        ...

    @abstractmethod
    def visit_for_stmt(self: "Visitor[T]", stmt: For) -> T:
        ...

    @abstractmethod
    def visit_function_stmt(self: "Visitor[T]", stmt: Function) -> T:
        ...

    @abstractmethod
    def visit_if_stmt(self: "Visitor[T]", stmt: If) -> T:
        ...

    @abstractmethod
    def visit_multi_var_stmt(self: "Visitor[T]", stmt: MultiVar) -> T:
        ...

    @abstractmethod
    def visit_return_stmt(self: "Visitor[T]", stmt: Return) -> T:
        ...

    @abstractmethod
    def visit_var_stmt(self: "Visitor[T]", stmt: Var) -> T:
        ...

    @abstractmethod
    def visit_while_stmt(self: "Visitor[T]", stmt: While) -> T:
        ...
