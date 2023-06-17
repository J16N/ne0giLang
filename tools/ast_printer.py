from interpreter.expr import Binary, Literal, Unary
from interpreter.expr import (
    Binary,
    Comma,
    Expr,
    Grouping,
    Ternary,
    Visitor as ExprVisitor,
)


class AstPrinter(ExprVisitor[str]):
    def print(self: "AstPrinter", expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self: "AstPrinter", expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_comma_expr(self: "AstPrinter", expr: Comma) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self: "AstPrinter", expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self: "AstPrinter", expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_ternary_expr(self: "AstPrinter", expr: Ternary) -> str:
        return self.parenthesize(
            "ternary", expr.condition, expr.then_branch, expr.else_branch
        )

    def visit_unary_expr(self: "AstPrinter", expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self: "AstPrinter", name: str, *exprs: Expr) -> str:
        builder: list[str] = [expr.accept(self) for expr in exprs]
        return f"({name} {' '.join(builder)})"
