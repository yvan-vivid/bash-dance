"""Lexical analysis -- a stream of lines."""

from dataclasses import dataclass
import re
from typing import Optional, Iterable, Iterator, Type


_block_open = r"\s*{\s*"
_block_close = r"\s*}\s*"
_prefix = "#%"
_prefix_reg = r"#%\s*"

def _directive(reg: str = ""):
    return re.compile(_prefix_reg + reg)

def _open_directive(reg: str = ""):
    return _directive(reg + _block_open)

def _close_directive(reg: str = ""):
    return _directive(_block_close + reg)


class LexicalError(Exception):
    """Errors involving lexical structure."""


class Token:
    """General class for tokens."""
    matcher = re.compile(r".*")
    def __init__(self, **kwargs):
        pass

    @classmethod
    def recognize(cls, line: str) -> Optional['Token']:
        """Given a line check if it matches this token type"""
        m = re.match(cls.matcher, line)
        if m is None:
            return None
        return cls(**m.groupdict())


@dataclass
class Line(Token):
    """Regular line"""
    line: str = ""

    def __str__(self) -> str:
        return self.line

    @classmethod
    def recognize(cls, line: str) -> Optional['Token']:
        if line.startswith(_prefix):
            return None
        return cls(line=line)


@dataclass
class Include(Token):
    """Include directive"""
    matcher = _open_directive(r"include\s+\"(?P<reference>.*)\"")
    reference: str


@dataclass
class Ignore(Token):
    """Ignore directive"""
    matcher = _open_directive(r"ignore")


@dataclass
class Close(Token):
    """Block directive closure"""
    matcher = _close_directive()


def lexer(lines: Iterable[str]) -> Iterator[Token]:
    """Lex lines into tokens from iterable"""
    for line in lines:
        line = line.rstrip()
        token: Optional[Token] = None
        token_type: Type[Token]
        for token_type in (Line, Include, Ignore, Close):
            token = token_type.recognize(line)
            if token is not None:
                break

        if token is None:
            raise LexicalError(f"Could not parse: '{line}'")

        yield token
