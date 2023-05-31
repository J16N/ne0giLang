import sys
from typing import Optional
from interpreter.lox import Lox

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: lox.py [script]")
        sys.exit(64)

    file: Optional[str] = sys.argv[1] if (len(sys.argv) == 2) else None
    Lox.execute(file)
