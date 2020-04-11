"""Lexical analysis -- a stream of lines."""

from dataclasses import dataclass
import re
from typing import Optional, Iterable, Iterator, ClassVar, Type


_block_open = r"\s*{\s*"
_block_close = r"\s*}\s*"
_prefix = "#%"
_prefix_reg = r"#%\s*"

def directive(reg: str = ""):
    return re.compile(_prefix_reg + reg)

def open_directive(reg: str = ""):
    return directive(reg + _block_open)

def close_directive(reg: str = ""):
    return directive(_block_close + reg)


class Token:
    matcher = re.compile(r".*")
    def __init__(self, **kwargs):
        pass

    @classmethod
    def recognize(cls, line: str) -> Optional['Token']:
        m = re.match(cls.matcher, line)
        if m is None:
            return None
        return cls(**m.groupdict())


@dataclass
class Line(Token):
    line: str

    @classmethod
    def recognize(cls, line: str) -> Optional['Token']:
        if line.startswith(_prefix):
            return None
        return cls(line)


@dataclass
class Include(Token):
    matcher = open_directive(r"include\s+\"(?P<reference>.*)\"")
    reference: str


@dataclass
class Ignore(Token):
    matcher = open_directive(r"ignore")


@dataclass
class Close(Token):
    matcher = close_directive()


def lexer(lines: Iterable[str]) -> Iterator[Token]:
    for line in lines:
        line = line.rstrip()
        token: Optional[Token] = None
        token_type: Type[Token] 
        for token_type in (Line, Include, Ignore, Close):
            token = token_type.recognize(line)
            if token is not None:
                break
        
        if token is None:
            raise ValueError(f"Could not parse: '{line}'")

        yield token
