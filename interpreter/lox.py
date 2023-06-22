import sys
from typing import ClassVar, Optional, cast

from .exceptions import RuntimeError
from .interpreter import Interpreter

# from tools.ast_printer import AstPrinter
from .parser import ParseError, Parser
from .resolver import Resolver
from .scanner import Scanner
from .stmt import Stmt
from .token import Token
from .token_type import TokenType


class Lox:
    had_error: ClassVar[bool] = False
    had_runtime_error: ClassVar[bool] = False
    _interpreter: ClassVar[Interpreter]

    @classmethod
    def execute(cls, file: Optional[str] = None) -> None:
        if file:
            cls._interpreter = Interpreter(cast(Lox, cls))
            cls.run_file(file)
        else:
            cls._interpreter = Interpreter(cast(Lox, cls), True)
            cls.run_prompt()

    @classmethod
    def run_file(cls, file: str) -> None:
        try:
            with open(file, "r") as f:
                try:
                    cls.run(f.read())

                    # Indicate an error in the exit code.
                    if cls.had_error:
                        sys.exit(65)
                    if cls.had_runtime_error:
                        sys.exit(70)

                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt")

        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
            sys.exit(74)

    @classmethod
    def run_prompt(cls) -> None:
        while True:
            try:
                line: str = input("> ")
                cls.run(f"{line};")
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
        print(*tokens, sep="\n")
        parser: Parser = Parser(tokens, cast(Lox, cls))
        statements: list[Optional[Stmt]] = parser.parse()

        # Stop if there was a syntax error.
        if cls.had_error:
            return

        resolver: Resolver = Resolver(cast(Lox, cls), cls._interpreter)
        resolver.resolve(statements)

        # Stop if there was a resolution error.
        if cls.had_error:
            return

        cls._interpreter.interpret(statements)
        # print(AstPrinter().print(expression))

    @classmethod
    def error_on_line(cls, line: int, message: str) -> None:
        cls.report(line, "", message)

    @classmethod
    def error_on_token(cls, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            cls.report(token.line, "at end", message)
        else:
            cls.report(token.line, f"at '{token.lexeme}'", message)

    @classmethod
    def report(cls, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}")
        cls.had_error = True

    @classmethod
    def runtime_error(cls, error: RuntimeError) -> None:
        print(f"[line {error.token.line}] {error.message}")
        cls.had_runtime_error = True
