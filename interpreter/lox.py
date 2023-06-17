import sys
from typing import Optional, ClassVar, cast
from .token import Token
from .parser import Parser
from .scanner import Scanner
from .token_type import TokenType
from .expr import Expr
from tools.ast_printer import AstPrinter
from .parser import ParseError
from .runtime_error import RuntimeError
from .interpreter import Interpreter


class Lox:
    had_error: ClassVar[bool] = False
    had_runtime_error: ClassVar[bool] = False
    _interpreter: ClassVar[Interpreter]

    @classmethod
    def execute(cls, file: Optional[str] = None) -> None:
        cls._interpreter = Interpreter(cast(Lox, cls))

        if file:
            cls.run_file(file)
        else:
            cls.run_prompt()

    @classmethod
    def run_file(cls, file: str) -> None:
        with open(file, "r") as f:
            cls.run(f.read())

            # Indicate an error in the exit code.
            if cls.had_error:
                sys.exit(65)
            if cls.had_runtime_error:
                sys.exit(70)

    @classmethod
    def run_prompt(cls) -> None:
        while True:
            try:
                line: str = input("> ")
                cls.run(line)
            except KeyboardInterrupt:
                break
            except ParseError:
                ...
            except RuntimeError:
                ...
            finally:
                cls.had_error = False
                cls.had_runtime_error = False

    @classmethod
    def run(cls, source: str) -> None:
        scanner: Scanner = Scanner(source, cast(Lox, cls))
        tokens: list[Token] = scanner.scan_tokens()
        parser: Parser = Parser(tokens, cast(Lox, cls))
        expression: Expr = parser.parse()

        # Stop if there was a syntax error.
        if cls.had_error:
            return

        cls._interpreter.interpret(expression)
        print(AstPrinter().print(expression))

    @classmethod
    def error_on_line(cls, line: int, message: str) -> None:
        cls.report(line, "", message)

    @classmethod
    def error_on_token(cls, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")

    @staticmethod
    def runtime_error(error: RuntimeError) -> None:
        print(f"[line {error.token.line}] {error.message}")
        Lox.had_runtime_error = True
