from typing import cast, TYPE_CHECKING
from .token import Token
from .token_type import TokenType
from .runtime_error import RuntimeError
from .expr import (
    Binary,
    Comma,
    Expr,
    Grouping,
    Literal,
    Ternary,
    Unary,
    Visitor as ExprVisitor,
)

if TYPE_CHECKING:
    from .lox import Lox


class Interpreter(ExprVisitor[object]):
    def __init__(self: "Interpreter", agent: "Lox"):
        self.agent = agent

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

    def _is_equal(self: "Interpreter", a: object, b: object) -> bool:
        return a == b

    def _is_truthy(self: "Interpreter", obj: object) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return bool(obj)
        return True

    def _stringify(self: "Interpreter", obj: object) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            return f"{obj:g}"

        if isinstance(obj, bool):
            return str(obj).lower()

        return str(obj)

    def interpret(self: "Interpreter", expr: Expr) -> None:
        try:
            value: object = self._evaluate(expr)
            print(self._stringify(value))

        except RuntimeError as e:
            self.agent.runtime_error(e)

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

    def visit_comma_expr(self: "Interpreter", expr: Comma) -> object:
        self._evaluate(expr.left)
        return self._evaluate(expr.right)

    def visit_grouping_expr(self: "Interpreter", expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_literal_expr(self: "Interpreter", expr: Literal) -> object:
        return expr.value

    def visit_ternary_expr(self: "Interpreter", expr: Ternary) -> object:
        condition: object = self._evaluate(expr.condition)
        return (
            self._evaluate(expr.then_branch)
            if self._is_truthy(condition)
            else self._evaluate(expr.else_branch)
        )

    def visit_unary_expr(self: "Interpreter", expr: Unary) -> object:
        right: object = self._evaluate(expr.right)

        match (expr.operator.type):
            case TokenType.BANG:
                return not self._is_truthy(right)

            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -cast(float, right)

            case _:
                ...

        return None
