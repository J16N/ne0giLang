import sys
from typing import Optional
from .scanner import Scanner
from .token import Token


class Lox:
    had_error: bool = False

    @staticmethod
    def execute(file: Optional[str] = None) -> None:
        if file:
            Lox.run_file(file)
        else:
            Lox.run_prompt()

    @staticmethod
    def run_file(file: str) -> None:
        with open(file, "r") as f:
            Lox.run(f.read())

            # Indicate an error in the exit code.
            if Lox.had_error:
                sys.exit(65)

    @staticmethod
    def run_prompt() -> None:
        while True:
            try:
                line: str = input("> ")
                Lox.run(line)
                Lox.had_error = False
            except KeyboardInterrupt:
                break

    @staticmethod
    def run(source: str) -> None:
        scanner: Scanner = Scanner(source)
        tokens: list[Token] = scanner.scan_tokens()

        for token in tokens:
            print(token)

    @staticmethod
    def error(line: int, message: str) -> None:
        Lox.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: lox.py [script]")
        sys.exit(64)

    file: Optional[str] = sys.argv[1] if (len(sys.argv) == 2) else None
    Lox.execute(file)
