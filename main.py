import sys
from typing import Optional
from interpreter.ne0gi import Ne0giLang

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python main.py [script]")
        sys.exit(64)

    file: Optional[str] = sys.argv[1] if (len(sys.argv) == 2) else None
    Ne0giLang.execute(file)
