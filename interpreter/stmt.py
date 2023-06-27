from abc import ABC, abstractmethod
from typing import Final, Generic, Optional, TypeVar

from .expr import Expr
from .expr import Function as FunctionExpr
from .expr import Variable
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

    def __repr__(self: "Block") -> str:
        return f"Block(statements={self.statements})"

    def __str__(self: "Block") -> str:
        return self.__repr__()


class Break(Stmt):
    def accept(self: "Break", visitor: "Visitor[T]") -> T:
        return visitor.visit_break_stmt()

    def __repr__(self: "Break") -> str:
        return "Break()"

    def __str__(self: "Break") -> str:
        return self.__repr__()


class Class(Stmt):
    def __init__(
        self: "Class",
        name: Token,
        superclass: Optional[Variable],
        methods: list["Function"],
    ):
        self.name: Final[Token] = name
        self.superclass: Final[Optional[Variable]] = superclass
        self.methods: Final[list["Function"]] = methods

    def accept(self: "Class", visitor: "Visitor[T]") -> T:
        return visitor.visit_class_stmt(self)

    def __repr__(self: "Class") -> str:
        return f"ClassStmt(name={self.name}, methods={self.methods})"

    def __str__(self: "Class") -> str:
        return self.__repr__()


class Continue(Stmt):
    def accept(self: "Continue", visitor: "Visitor[T]") -> T:
        return visitor.visit_continue_stmt()

    def __repr__(self: "Continue") -> str:
        return "Continue()"

    def __str__(self: "Continue") -> str:
        return self.__repr__()


class Expression(Stmt):
    def __init__(self: "Expression", expression: Expr):
        self.expression: Final[Expr] = expression

    def accept(self: "Expression", visitor: "Visitor[T]") -> T:
        return visitor.visit_expression_stmt(self)

    def __repr__(self: "Expression") -> str:
        return f"ExpressionStmt(expression={self.expression})"

    def __str__(self: "Expression") -> str:
        return self.__repr__()


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

    def __repr__(self: "For") -> str:
        return f"ForStmt(initializer={self.initializer}, condition={self.condition}, increment={self.increment})"

    def __str__(self: "For") -> str:
        return self.__repr__()


class Function(Stmt):
    def __init__(self: "Function", name: Token, function: FunctionExpr):
        self.name: Final[Token] = name
        self.function: Final[FunctionExpr] = function

    def accept(self: "Function", visitor: "Visitor[T]") -> T:
        return visitor.visit_function_stmt(self)

    def __repr__(self: "Function") -> str:
        return f"FunctionStmt(name={self.name}, function={self.function})"

    def __str__(self: "Function") -> str:
        return self.__repr__()


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

    def __repr__(self: "If") -> str:
        return f"IfStmt(condition={self.condition})"

    def __str__(self: "If") -> str:
        return self.__repr__()


class Return(Stmt):
    def __init__(self: "Return", keyword: Token, value: Optional[Expr]):
        self.keyword: Final[Token] = keyword
        self.value: Final[Optional[Expr]] = value

    def accept(self: "Return", visitor: "Visitor[T]") -> T:
        return visitor.visit_return_stmt(self)

    def __repr__(self: "Return") -> str:
        return f"ReturnStmt(keyword={self.keyword}, value={self.value})"

    def __str__(self: "Return") -> str:
        return self.__repr__()


class MultiVar(Stmt):
    def __init__(self: "MultiVar"):
        self.variables: Final[list["Var"]] = []

    def add(self: "MultiVar", variable: "Var") -> None:
        self.variables.append(variable)

    def accept(self: "MultiVar", visitor: "Visitor[T]") -> T:
        return visitor.visit_multi_var_stmt(self)

    def __repr__(self: "MultiVar") -> str:
        return f"MultiVarStmt(variables={self.variables})"

    def __str__(self: "MultiVar") -> str:
        return self.__repr__()


class Var(Stmt):
    def __init__(self: "Var", name: Token, initializer: Optional[Expr]):
        self.name: Final[Token] = name
        self.initializer: Final[Optional[Expr]] = initializer

    def accept(self: "Var", visitor: "Visitor[T]") -> T:
        return visitor.visit_var_stmt(self)

    def __repr__(self: "Var") -> str:
        return f"VarStmt(name={self.name}, initializer={self.initializer})"

    def __str__(self: "Var") -> str:
        return self.__repr__()


class While(Stmt):
    def __init__(self: "While", condition: Expr, body: Optional[Stmt]):
        self.condition: Final[Expr] = condition
        self.body: Final[Optional[Stmt]] = body

    def accept(self: "While", visitor: "Visitor[T]") -> T:
        return visitor.visit_while_stmt(self)

    def __repr__(self: "While") -> str:
        return f"WhileStmt(condition={self.condition})"

    def __str__(self: "While") -> str:
        return self.__repr__()


class Visitor(ABC, Generic[T]):
    @abstractmethod
    def visit_block_stmt(self: "Visitor[T]", stmt: Block) -> T:
        ...

    @abstractmethod
    def visit_break_stmt(self: "Visitor[T]") -> T:
        ...

    @abstractmethod
    def visit_class_stmt(self: "Visitor[T]", stmt: Class) -> T:
        ...

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
