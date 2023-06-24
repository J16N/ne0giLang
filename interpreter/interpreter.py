from typing import TYPE_CHECKING, Final, Optional, cast

from .callable import Callable
from .environment import Environment
from .exceptions import Break, Continue, Return, RuntimeError
from .expr import Assign, Binary, Call, Comma, Expr
from .expr import Function as FunctionExpr
from .expr import Get, Grouping, Literal, Logical, Set, Ternary, This, Unary, Variable
from .expr import Visitor as ExprVisitor
from .function import Function
from .instance import Instance
from .klass import Class
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
from .types import Uninitialized
from .utils import Clock, Print

if TYPE_CHECKING:
    from .lox import Lox


class Interpreter(ExprVisitor[object], StmtVisitor[None]):
    def __init__(self: "Interpreter", agent: "Lox", repl: bool = False):
        self._agent: Final["Lox"] = agent
        self.repl: Final[bool] = repl
        self._print_called: bool = False
        self.globals: Final[Environment] = Environment()
        self._environment: Environment = self.globals
        self._locals: Final[dict[Expr, int]] = {}
        self.globals.define("clock", Clock())
        self.globals.define("print", Print())

    def _check_lvalue_operand(
        self: "Interpreter", operator: Token, operand: object
    ) -> None:
        if isinstance(operand, Uninitialized):
            raise RuntimeError(operator, "Cannot assign to uninitialized variable.")
        if isinstance(operand, (Literal, Grouping)):
            raise RuntimeError(operator, "Cannot assign to literal.")

    def _check_number_operands(
        self: "Interpreter", operator: Token, left: object, right: object
    ) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def _check_number_operand(
        self: "Interpreter", operator: Token, operand: object
    ) -> None:
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def _evaluate(self: "Interpreter", expr: Expr) -> object:
        return expr.accept(self)

    def _execute(self: "Interpreter", stmt: Optional[Stmt]) -> None:
        if not stmt:
            return
        stmt.accept(self)

    def _is_equal(self: "Interpreter", a: object, b: object) -> bool:
        return a == b

    def _is_truthy(self: "Interpreter", obj: object) -> bool:
        return bool(obj)

    def _lookup_variable(self: "Interpreter", name: Token, expr: Expr) -> object:
        distance: int = self._locals.get(expr, -1)
        if distance >= 0:
            return self._environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def execute_block(
        self: "Interpreter", statements: list[Optional[Stmt]], environment: Environment
    ) -> None:
        previous: Environment = self._environment
        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)

        finally:
            self._environment = previous

    def interpret(self: "Interpreter", statements: list[Optional[Stmt]]) -> None:
        try:
            for statement in statements:
                self._execute(statement)

        except RuntimeError as e:
            self._agent.runtime_error(e)

    def resolve(self: "Interpreter", expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def stringify(self: "Interpreter", obj: object) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            return f"{obj:g}"

        if isinstance(obj, bool):
            return str(obj).lower()

        if isinstance(obj, str):
            return f"'{obj}'"

        return str(obj)

    def visit_assign_expr(self: "Interpreter", expr: Assign) -> object:
        value: object = self._evaluate(expr.value)
        distance: int = self._locals.get(expr, -1)
        if distance >= 0:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_binary_expr(self: "Interpreter", expr: Binary) -> object:
        left: object = self._evaluate(expr.left)
        right: object = self._evaluate(expr.right)

        match (expr.operator.type):
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)

            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)

            case TokenType.GREATER:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) > float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) > str(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.GREATER_EQUAL:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) >= float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) >= str(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.LESS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) < float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) < str(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.LESS_EQUAL:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) <= float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) <= str(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return cast(float, left) - cast(float, right)

            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise RuntimeError(expr.operator, "Division by zero.")
                return cast(float, left) / cast(float, right)

            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
                return cast(float, left) * cast(float, right)

            case _:
                ...

    def visit_call_expr(self: "Interpreter", expr: Call) -> object:
        callee: object = self._evaluate(expr.callee)
        if isinstance(callee, Print):
            self._print_called = True

        arguments: list[object] = [
            self._evaluate(argument) for argument in expr.arguments
        ]

        if not isinstance(callee, Callable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        function: Callable = callee
        if len(arguments) != function.arity():
            raise RuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )

        return function.call(self, arguments)

    def visit_comma_expr(self: "Interpreter", expr: Comma) -> object:
        self._evaluate(expr.left)
        return self._evaluate(expr.right)

    def visit_function_expr(self: "Interpreter", expr: FunctionExpr) -> object:
        return Function(None, expr, self._environment)

    def visit_get_expr(self: "Interpreter", expr: Get) -> object:
        obj: object = self._evaluate(expr.obj)
        if isinstance(obj, Instance):
            return obj.get(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self: "Interpreter", expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_literal_expr(self: "Interpreter", expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self: "Interpreter", expr: Logical) -> object:
        left: object = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_set_expr(self: "Interpreter", expr: Set) -> object:
        obj: object = self._evaluate(expr.obj)

        if not isinstance(obj, Instance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value: object = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_ternary_expr(self: "Interpreter", expr: Ternary) -> object:
        condition: object = self._evaluate(expr.condition)
        return (
            self._evaluate(expr.then_branch)
            if self._is_truthy(condition)
            else self._evaluate(expr.else_branch)
        )

    def visit_this_expr(self: "Interpreter", expr: This) -> object:
        return self._lookup_variable(expr.keyword, expr)

    def visit_unary_expr(self: "Interpreter", expr: Unary) -> object:
        right: object = self._evaluate(expr.right)

        match (expr.operator.type):
            case TokenType.BANG:
                return not self._is_truthy(right)

            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -cast(float, right)

            case TokenType.PLUS:
                self._check_number_operand(expr.operator, right)
                return cast(float, right)

            case TokenType.INCREMENT:
                self._check_lvalue_operand(expr.operator, expr.right)

            case TokenType.DECREMENT:
                self._check_lvalue_operand(expr.operator, expr.right)

            case _:
                ...

        return None

    def visit_variable_expr(self: "Interpreter", expr: Variable) -> object:
        return self._lookup_variable(expr.name, expr)

    def visit_block_stmt(self: "Interpreter", stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self._environment))

    def visit_break_stmt(self: "Interpreter") -> None:
        raise Break()

    def visit_class_stmt(self: "Interpreter", stmt: ClassStmt) -> None:
        self._environment.define(stmt.name.lexeme, None)
        methods: dict[str, Function] = {}
        for method in stmt.methods:
            function: Function = Function(
                method.name.lexeme,
                method.function,
                self._environment,
                method.name.lexeme == stmt.name.lexeme,
            )
            methods[method.name.lexeme] = function

        klass: Class = Class(stmt.name.lexeme, methods)
        self._environment.assign(stmt.name, klass)

    def visit_continue_stmt(self: "Interpreter") -> None:
        raise Continue()

    def visit_expression_stmt(self: "Interpreter", stmt: Expression) -> None:
        value: object = self._evaluate(stmt.expression)
        if self.repl and not self._print_called:
            print(self.stringify(value))
        self._print_called = False

    def visit_for_stmt(self: "Interpreter", stmt: For) -> None:
        self._execute(stmt.initializer)
        while self._is_truthy(
            self._evaluate(stmt.condition) if stmt.condition else True
        ):
            try:
                self._execute(stmt.body)
            except Break:
                break
            except Continue:
                continue
            finally:
                if stmt.increment:
                    self._evaluate(stmt.increment)

    def visit_function_stmt(self: "Interpreter", stmt: FunctionStmt) -> None:
        fn_name: str = stmt.name.lexeme
        function: Function = Function(fn_name, stmt.function, self._environment)
        self._environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self: "Interpreter", stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)) and stmt.then_branch:
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def visit_multi_var_stmt(self: "Interpreter", stmt: MultiVar) -> None:
        for variable in stmt.variables:
            variable.accept(self)

    def visit_return_stmt(self: "Interpreter", stmt: ReturnStmt) -> None:
        value: object = None
        if stmt.value:
            value = self._evaluate(stmt.value)
        raise Return(value)

    def visit_var_stmt(self: "Interpreter", stmt: Var) -> None:
        value: object = Uninitialized()
        self._environment.define(stmt.name.lexeme, value)

        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)
            self._environment.assign(stmt.name, value)

    def visit_while_stmt(self: "Interpreter", stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            try:
                self._execute(stmt.body)
            except Break:
                break
            except Continue:
                continue
