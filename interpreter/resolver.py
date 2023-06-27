from enum import Enum
from typing import TYPE_CHECKING, Final, Optional

from .expr import Assign, Binary, Call, Comma, Expr
from .expr import Function as FunctionExpr
from .expr import (
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    Ternary,
    This,
    UArithmeticOp,
    Unary,
    Variable,
)
from .expr import Visitor as ExprVisitor
from .interpreter import Interpreter
from .stmt import Block
from .stmt import Class as ClassStmt
from .stmt import Expression, For
from .stmt import Function as FunctionStmt
from .stmt import If, MultiVar
from .stmt import Return as ReturnStmt
from .stmt import Stmt, Var
from .stmt import Visitor as StmtVisitor
from .stmt import While
from .token import Token
from .token_type import TokenType

if TYPE_CHECKING:
    from .lox import Lox


class FunctionType(Enum):
    NONE = "none"
    FUNCTION = "function"
    INITIALIZER = "initializer"
    METHOD = "method"


class ClassType(Enum):
    NONE = "none"
    CLASS = "class"
    SUBCLASS = "subclass"


class ConstructorType(Enum):
    NONE = "none"
    OTHER = "other"
    SUPER = "super"
    THIS = "this"


class VariableTracker:
    def __init__(
        self: "VariableTracker", initialized: bool = False, occurence: int = 1
    ):
        self.initialized: bool = initialized
        self.occurence: int = occurence

    def __repr__(self: "VariableTracker") -> str:
        return f"VariableTracker(initialized={self.initialized}, occurence={self.occurence})"

    def __str__(self: "VariableTracker") -> str:
        return self.__repr__()


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    def __init__(
        self: "Resolver", agent: "Lox", interpreter: Interpreter, repl: bool = False
    ):
        self._interpreter: Final[Interpreter] = interpreter
        self._scopes: Final[list[dict[Token, VariableTracker]]] = []
        self._agent: Final[Lox] = agent
        self._current_function: FunctionType = FunctionType.NONE
        self._current_class: ClassType = ClassType.NONE
        self._repl = repl
        self._statement_index: int = 0
        self._current_constructor_type: ConstructorType = ConstructorType.NONE

    def _begin_scope(self: "Resolver") -> None:
        self._scopes.append({})

    def _declare(self: "Resolver", name: Token) -> None:
        scope: dict[Token, VariableTracker] = self._scopes[-1]
        if scope.get(name):
            self._agent.error_on_token(
                name, "Already variable with this name in this scope."
            )
            return
        scope[name] = VariableTracker()

    def _define(self: "Resolver", name: Token) -> None:
        scope: dict[Token, VariableTracker] = self._scopes[-1]
        scope[name].initialized = True

    def _end_scope(self: "Resolver") -> None:
        scope: dict[Token, VariableTracker] = self._scopes.pop()
        if self._repl:
            return
        for name, tracker in scope.items():
            if tracker.occurence == 1 and name.lexeme not in ("this", "super"):
                self._agent.warn(
                    name, f"Unused variable '{name.lexeme}' in the current scope."
                )

    def _resolve_expr(self: "Resolver", expr: Optional[Expr]) -> None:
        if expr:
            expr.accept(self)

    def _resolve_function(
        self: "Resolver", func: FunctionExpr, type: FunctionType
    ) -> None:
        enclosing_function: FunctionType = self._current_function
        previous_state: ConstructorType = self._current_constructor_type
        self._current_function = type
        self._current_constructor_type = (
            ConstructorType.OTHER
            if type == FunctionType.INITIALIZER
            else ConstructorType.NONE
        )
        self._begin_scope()

        for param in func.params:
            self._declare(param)
            self._define(param)

        self._resolve_stmts(func.body)
        self._end_scope()
        self._current_function = enclosing_function
        self._current_constructor_type = previous_state

    def _resolve_local(self: "Resolver", expr: Expr, name: Token) -> None:
        for i, scope in enumerate(reversed(self._scopes)):
            if name in scope:
                scope[name].occurence += 1
                self._interpreter.resolve(expr, i)
                break

    def _resolve_stmt(self: "Resolver", stmt: Optional[Stmt]) -> None:
        if stmt:
            stmt.accept(self)

    def _resolve_stmts(self: "Resolver", stmts: list[Optional[Stmt]]) -> None:
        self._statement_index = 0
        for i, stmt in enumerate(stmts):
            self._statement_index = i
            self._resolve_stmt(stmt)

    def resolve(self: "Resolver", statements: list[Optional[Stmt]]) -> None:
        self._begin_scope()
        self._resolve_stmts(statements)
        self._end_scope()

    def visit_assign_expr(self: "Resolver", expr: Assign) -> None:
        self._resolve_expr(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_binary_expr(self: "Resolver", expr: Binary) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_call_expr(self: "Resolver", expr: Call) -> None:
        self._resolve_expr(expr.callee)

        if (
            self._current_constructor_type == ConstructorType.SUPER
            and self._current_function != FunctionType.INITIALIZER
        ):
            self._agent.error_on_token(
                expr.paren,
                "Can't use 'super' constructor in a function that is not an initializer.",
            )
            return

        if (
            self._current_constructor_type == ConstructorType.SUPER
            and self._statement_index != 0
        ):
            self._agent.error_on_token(
                expr.paren,
                "'super' constructor must be called before any other statement.",
            )
            return

        for argument in expr.arguments:
            self._resolve_expr(argument)

    def visit_comma_expr(self: "Resolver", expr: Comma) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_function_expr(self: "Resolver", expr: FunctionExpr) -> None:
        self._resolve_function(expr, FunctionType.FUNCTION)

    def visit_get_expr(self: "Resolver", expr: Get) -> None:
        self._resolve_expr(expr.obj)

    def visit_grouping_expr(self: "Resolver", expr: Grouping) -> None:
        self._resolve_expr(expr.expression)

    def visit_literal_expr(self: "Resolver", expr: Literal) -> None:
        return

    def visit_logical_expr(self: "Resolver", expr: Logical) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_set_expr(self: "Resolver", expr: Set) -> None:
        self._resolve_expr(expr.value)
        self._resolve_expr(expr.obj)

    def visit_super_expr(self: "Resolver", expr: Super) -> None:
        if self._current_class == ClassType.NONE:
            self._agent.error_on_token(
                expr.keyword, f"Cannot use '{expr.keyword.lexeme}' outside class."
            )
            return

        elif self._current_class != ClassType.SUBCLASS:
            self._agent.error_on_token(
                expr.keyword,
                f"Cannot use '{expr.keyword.lexeme}' in class with no superclass.",
            )
            return

        self._resolve_local(expr, expr.keyword)

        if expr.method is None:
            self._current_constructor_type = ConstructorType.SUPER

    def visit_ternary_expr(self: "Resolver", expr: Ternary) -> None:
        self._resolve_expr(expr.condition)
        self._resolve_expr(expr.then_branch)
        self._resolve_expr(expr.else_branch)

    def visit_this_expr(self: "Resolver", expr: "This") -> None:
        if self._current_class == ClassType.NONE:
            self._agent.error_on_token(
                expr.keyword, f"Cannot use '{expr.keyword.lexeme}' outside class."
            )

        self._resolve_local(expr, expr.keyword)

    def visit_uarithmeticop_expr(self: "Resolver", expr: UArithmeticOp) -> None:
        self._resolve_expr(expr.expression)

    def visit_unary_expr(self: "Resolver", expr: Unary) -> None:
        self._resolve_expr(expr.right)

    def visit_variable_expr(self: "Resolver", expr: Variable) -> None:
        tracker: Optional[VariableTracker] = self._scopes[-1].get(expr.name)
        if tracker and tracker.initialized is False:
            self._agent.error_on_token(
                expr.name,
                "Cannot access before initialization.",
            )

        self._resolve_local(expr, expr.name)

    def visit_block_stmt(self: "Resolver", stmt: Block) -> None:
        self._begin_scope()
        self._resolve_stmts(stmt.statements)
        self._end_scope()

    def visit_break_stmt(self: "Resolver") -> None:
        return

    def visit_class_stmt(self: "Resolver", stmt: ClassStmt) -> None:
        enclosing_class: ClassType = self._current_class
        self._current_class = ClassType.CLASS

        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass:
            self._current_class = ClassType.SUBCLASS
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                self._agent.error_on_token(
                    stmt.superclass.name, "A class cannot inherit from itself."
                )

            self._resolve_expr(stmt.superclass)
            self._begin_scope()
            self._scopes[-1][
                Token(TokenType.SUPER, "super", None, stmt.name.line, 0)
            ] = VariableTracker(True)

        self._begin_scope()
        self._scopes[-1][
            Token(TokenType.THIS, "this", None, stmt.name.line + 1, 0)
        ] = VariableTracker(True)

        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD

            if method.name.lexeme == stmt.name.lexeme:
                declaration = FunctionType.INITIALIZER

            self._resolve_function(method.function, declaration)

        self._end_scope()

        if stmt.superclass:
            self._end_scope()

        self._current_class = enclosing_class

    def visit_continue_stmt(self: "Resolver") -> None:
        return

    def visit_expression_stmt(self: "Resolver", stmt: Expression) -> None:
        self._resolve_expr(stmt.expression)

    def visit_for_stmt(self: "Resolver", stmt: For) -> None:
        self._resolve_stmt(stmt.initializer)
        self._resolve_expr(stmt.condition)
        self._resolve_expr(stmt.increment)
        self._resolve_stmt(stmt.body)

    def visit_function_stmt(self: "Resolver", stmt: FunctionStmt) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt.function, FunctionType.FUNCTION)

    def visit_if_stmt(self: "Resolver", stmt: If) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.then_branch)

    def visit_multi_var_stmt(self: "Resolver", stmt: MultiVar) -> None:
        for var in stmt.variables:
            self._resolve_stmt(var)

    def visit_return_stmt(self: "Resolver", stmt: ReturnStmt) -> None:
        if self._current_function == FunctionType.NONE:
            self._agent.error_on_token(
                stmt.keyword, "Cannot return from top-level code."
            )

        if stmt.value:
            if self._current_function == FunctionType.INITIALIZER:
                self._agent.error_on_token(
                    stmt.keyword, "Cannot return a value from an initializer."
                )

            self._resolve_expr(stmt.value)

    def visit_var_stmt(self: "Resolver", stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer:
            self._resolve_expr(stmt.initializer)
            self._define(stmt.name)

    def visit_while_stmt(self: "Resolver", stmt: While) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.body)
