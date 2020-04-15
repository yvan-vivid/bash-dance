"""Output writing -- a token stream consumer."""

from typing import IO
from pathlib import Path
import sys
from dataclasses import dataclass

_hr = 80*"#"

class Token:
    """Abstract class for a formatter token."""


@dataclass
class Line(Token):
    """Single line."""
    line: str = ""


@dataclass
class Prefix(Token):
    """Prefix for a section."""
    path: Path
    is_root: bool = False


@dataclass
class Suffix(Token):
    """Suffix for a section."""
    path: Path
    is_root: bool = False


class Formatter:
    """Given a text stream write format output tokens to it."""
    handle: IO[str]
    count: int

    def __init__(self, handle: IO[str] = sys.stdout):
        self.handle = handle
        self.count = 0

    def writeline(self, line: str = ""):
        """Write single line."""
        prefix = "" if self.count == 0 else "\n"
        self.handle.write(f"{prefix}{line!s}")
        self.count += 1

    def rule(self):
        """Write horizontal rule."""
        self.writeline(_hr)

    def banner(self, message: str):
        """Write banner to formatter stream."""
        self.rule()
        self.writeline(f"## {message}")
        self.rule()

    def write(self, token: Token):
        """Write token to formatter stream."""
        if isinstance(token, Line):
            self.writeline(token.line)
        elif isinstance(token, Prefix) and not token.is_root:
            self.banner(f"start \"{token.path.name}\"")
            self.writeline()
        elif isinstance(token, Suffix) and not token.is_root:
            self.writeline()
            self.banner(f"end \"{token.path.name}\"")
