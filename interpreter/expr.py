from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Final
from .token import Token

T = TypeVar("T")


class Expr(ABC):
    @abstractmethod
    def accept(self: "Expr", visitor: "Visitor[T]") -> T:
        ...


# class Assign(Expr):
#     def __init__(self: "Assign", name: Token, value: Expr):
#         self.name: Final[Token] = name
#         self.value: Final[Expr] = value

#     def accept(self: "Assign", visitor: "Visitor[T]") -> T:
#         return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self: "Binary", left: Expr, operator: Token, right: Expr):
        self.left: Final[Expr] = left
        self.operator: Final[Token] = operator
        self.right: Final[Expr] = right

    def accept(self: "Binary", visitor: "Visitor[T]") -> T:
        return visitor.visit_binary_expr(self)


# class Call(Expr):
#     def __init__(self: "Call", callee: Expr, paren: Token, arguments: list[Expr]):
#         self.callee: Final[Expr] = callee
#         self.paren: Final[Token] = paren
#         self.arguments: Final[list[Expr]] = arguments

#     def accept(self: "Call", visitor: "Visitor[T]") -> T:
#         return visitor.visit_call_expr(self)


class Comma(Expr):
    def __init__(self: "Comma", left: Expr, operator: Token, right: Expr):
        self.left: Final[Expr] = left
        self.operator: Final[Token] = operator
        self.right: Final[Expr] = right

    def accept(self: "Comma", visitor: "Visitor[T]") -> T:
        return visitor.visit_comma_expr(self)


# class Function(Expr):
#     def __init__(self: "Function", params: list[Token], body: list[Stmt]):
#         self.params: Final[list[Token]] = params
#         self.body: Final[list[Stmt]] = body

#     def accept(self: "Function", visitor: "Visitor[T]") -> T:
#         return visitor.visit_function_expr(self)


# class Get(Expr):
#     def __init__(self: "Get", obj: Expr, name: Token):
#         self.obj: Final[Expr] = obj
#         self.name: Final[Token] = name

#     def accept(self: "Get", visitor: "Visitor[T]") -> T:
#         return visitor.visit_get_expr(self)


class Grouping(Expr):
    def __init__(self: "Grouping", expression: Expr):
        self.expression: Final[Expr] = expression

    def accept(self: "Grouping", visitor: "Visitor[T]") -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self: "Literal", value: object):
        self.value: Final[object] = value

    def accept(self: "Literal", visitor: "Visitor[T]") -> T:
        return visitor.visit_literal_expr(self)


# class Logical(Expr):
#     def __init__(self: "Logical", left: Expr, operator: Token, right: Expr):
#         self.left: Final[Expr] = left
#         self.operator: Final[Token] = operator
#         self.right: Final[Expr] = right

#     def accept(self: "Logical", visitor: "Visitor[T]") -> T:
#         return visitor.visit_logical_expr(self)


# class Set(Expr):
#     def __init__(self: "Set", obj: Expr, name: Token, value: Expr):
#         self.obj: Final[Expr] = obj
#         self.name: Final[Token] = name
#         self.value: Final[Expr] = value

#     def accept(self: "Set", visitor: "Visitor[T]") -> T:
#         return visitor.visit_set_expr(self)


class Ternary(Expr):
    def __init__(
        self: "Ternary", condition: Expr, then_branch: Expr, else_branch: Expr
    ):
        self.condition: Final[Expr] = condition
        self.then_branch: Final[Expr] = then_branch
        self.else_branch: Final[Expr] = else_branch

    def accept(self: "Ternary", visitor: "Visitor[T]") -> T:
        return visitor.visit_ternary_expr(self)


# class This(Expr):
#     def __init__(self: "This", keyword: Token):
#         self.keyword: Final[Token] = keyword

#     def accept(self: "This", visitor: "Visitor[T]") -> T:
#         return visitor.visit_this_expr(self)


class Unary(Expr):
    def __init__(self: "Unary", operator: Token, right: Expr):
        self.operator: Final[Token] = operator
        self.right: Final[Expr] = right

    def accept(self: "Unary", visitor: "Visitor[T]") -> T:
        return visitor.visit_unary_expr(self)


# class Variable(Expr):
#     def __init__(self: "Variable", name: Token):
#         self.name: Final[Token] = name

#     def accept(self: "Variable", visitor: "Visitor[T]") -> T:
#         return visitor.visit_variable_expr(self)


class Visitor(ABC, Generic[T]):
    # @abstractmethod
    # def visit_assign_expr(self: "Visitor[T]", expr: Assign) -> T:
    #     ...

    @abstractmethod
    def visit_binary_expr(self: "Visitor[T]", expr: Binary) -> T:
        ...

    # @abstractmethod
    # def visit_call_expr(self: "Visitor[T]", expr: Call) -> T:
    #     ...

    @abstractmethod
    def visit_comma_expr(self: "Visitor[T]", expr: Comma) -> T:
        ...

    # @abstractmethod
    # def visit_function_expr(self: "Visitor[T]", expr: Function) -> T:
    #     ...

    # @abstractmethod
    # def visit_get_expr(self: "Visitor[T]", expr: Get) -> T:
    #     ...

    @abstractmethod
    def visit_grouping_expr(self: "Visitor[T]", expr: Grouping) -> T:
        ...

    @abstractmethod
    def visit_literal_expr(self: "Visitor[T]", expr: Literal) -> T:
        ...

    # @abstractmethod
    # def visit_logical_expr(self: "Visitor[T]", expr: Logical) -> T:
    #     ...

    # @abstractmethod
    # def visit_set_expr(self: "Visitor[T]", expr: Set) -> T:
    #     ...

    @abstractmethod
    def visit_ternary_expr(self: "Visitor[T]", expr: Ternary) -> T:
        ...

    # @abstractmethod
    # def visit_this_expr(self: "Visitor[T]", expr: This) -> T:
    #     ...

    @abstractmethod
    def visit_unary_expr(self: "Visitor[T]", expr: Unary) -> T:
        ...

    # @abstractmethod
    # def visit_variable_expr(self: "Visitor[T]", expr: Variable) -> T:
    #     ...
