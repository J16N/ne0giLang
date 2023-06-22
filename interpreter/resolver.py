from enum import Enum
from typing import Final, Optional, TYPE_CHECKING
from .expr import (
    Assign,
    Binary,
    Call,
    Comma,
    Expr,
    Function as FunctionExpr,
    Grouping,
    Literal,
    Logical,
    Ternary,
    Unary,
    Variable,
    Visitor as ExprVisitor,
)
from .stmt import (
    Block,
    Expression,
    For,
    Function as FunctionStmt,
    If,
    MultiVar,
    Return as ReturnStmt,
    Stmt,
    Var,
    Visitor as StmtVisitor,
    While,
)
from .token import Token
from .interpreter import Interpreter

if TYPE_CHECKING:
    from .lox import Lox


class FunctionType(Enum):
    NONE = "none"
    FUNCTION = "function"


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    def __init__(self: "Resolver", agent: "Lox", interpreter: Interpreter):
        self._interpreter: Final[Interpreter] = interpreter
        self._scopes: Final[list[dict[str, bool]]] = []
        self._agent: Final[Lox] = agent
        self._current_function: FunctionType = FunctionType.NONE

    def _begin_scope(self: "Resolver") -> None:
        self._scopes.append({})

    def _declare(self: "Resolver", name: Token) -> None:
        if not self._scopes:
            return
        scope: dict[str, bool] = self._scopes[-1]
        if scope.get(name.lexeme):
            self._agent.error_on_token(
                name, "Already variable with this name in this scope."
            )
            return
        scope[name.lexeme] = False

    def _define(self: "Resolver", name: Token) -> None:
        if not self._scopes:
            return
        scope: dict[str, bool] = self._scopes[-1]
        scope[name.lexeme] = True

    def _end_scope(self: "Resolver") -> None:
        self._scopes.pop()

    def _resolve_expr(self: "Resolver", expr: Optional[Expr]) -> None:
        if expr:
            expr.accept(self)

    def _resolve_function(
        self: "Resolver", func: FunctionExpr, type: FunctionType
    ) -> None:
        enclosing_function: FunctionType = self._current_function
        self._current_function = type
        self._begin_scope()

        for param in func.params:
            self._declare(param)
            self._define(param)

        self._resolve_stmts(func.body)
        self._end_scope()
        self._current_function = enclosing_function

    def _resolve_local(self: "Resolver", expr: Expr, name: Token) -> None:
        for i, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope:
                self._interpreter.resolve(expr, i)

    def _resolve_stmt(self: "Resolver", stmt: Optional[Stmt]) -> None:
        if stmt:
            stmt.accept(self)

    def _resolve_stmts(self: "Resolver", stmts: list[Optional[Stmt]]) -> None:
        for stmt in stmts:
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
        for argument in expr.arguments:
            self._resolve_expr(argument)

    def visit_comma_expr(self: "Resolver", expr: Comma) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_function_expr(self: "Resolver", expr: FunctionExpr) -> None:
        self._resolve_function(expr, FunctionType.FUNCTION)

    def visit_grouping_expr(self: "Resolver", expr: Grouping) -> None:
        self._resolve_expr(expr.expression)

    def visit_literal_expr(self: "Resolver", expr: Literal) -> None:
        return

    def visit_logical_expr(self: "Resolver", expr: Logical) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_ternary_expr(self: "Resolver", expr: Ternary) -> None:
        self._resolve_expr(expr.condition)
        self._resolve_expr(expr.then_branch)
        self._resolve_expr(expr.else_branch)

    def visit_unary_expr(self: "Resolver", expr: Unary) -> None:
        self._resolve_expr(expr.right)

    def visit_variable_expr(self: "Resolver", expr: Variable) -> None:
        if self._scopes and self._scopes[-1].get(expr.name.lexeme) is False:
            self._agent.error_on_token(
                expr.name,
                "Uninitialized variable.",
            )

        self._resolve_local(expr, expr.name)

    def visit_block_stmt(self: "Resolver", stmt: Block) -> None:
        self._begin_scope()
        self._resolve_stmts(stmt.statements)
        self._end_scope()

    def visit_break_stmt(self: "Resolver") -> None:
        return

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
            self._resolve_expr(stmt.value)

    def visit_var_stmt(self: "Resolver", stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer:
            self._resolve_expr(stmt.initializer)
            self._define(stmt.name)

    def visit_while_stmt(self: "Resolver", stmt: While) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.body)
