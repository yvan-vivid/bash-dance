"""Lexical analysis tests."""

from pathlib import Path
from typing import NamedTuple, Sequence
from bash_crash.lexer import (
    lexer, Token, Line, Include, Ignore, Close
)

_test_docs = Path(__file__).absolute().parent / "test_docs"


class LexTest(NamedTuple):
    path: Path
    reference: Sequence[Token]


_test_tokens_1 = LexTest(
    path=_test_docs / "test_docs_1.bash",
    reference=(
        Line("# comment"),
        Line("line 1"),
        Line("line 2"),
        Line(""),
        Include(reference="library"),
        Line("line 3"),
        Line(""),
        Close(),
        Line(""),
        Line("line 4"),
        Line(""),
        Ignore(),
        Line("line 5"),
        Close(),
        Line(""),
        Line("line 6"),
    )
)


def test_lexer():
    token_file, ref_stream = _test_tokens_1
    with token_file.open('r') as fh:
        token_stream = lexer(fh.readlines())
        for ref, value in zip(ref_stream, token_stream):
            assert ref == value
