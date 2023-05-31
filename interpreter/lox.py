import sys
from typing import Optional, ClassVar, cast
from .token import Token
from .scanner import Scanner


class Lox:
    had_error: ClassVar[bool] = False

    @classmethod
    def execute(cls, file: Optional[str] = None) -> None:
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

    @classmethod
    def run_prompt(cls) -> None:
        while True:
            try:
                line: str = input("> ")
                cls.run(line)
                cls.had_error = False
            except KeyboardInterrupt:
                break

    @classmethod
    def run(cls, source: str) -> None:
        scanner: Scanner = Scanner(source, cast(cls, Lox))
        tokens: list[Token] = scanner.scan_tokens()

        for token in tokens:
            print(token)

    @classmethod
    def error(cls, line: int, message: str) -> None:
        cls.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")
