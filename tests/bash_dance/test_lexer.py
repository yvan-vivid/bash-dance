"""Lexical analysis tests."""
# pylint: disable=too-many-function-args

from pathlib import Path
from typing import NamedTuple, Sequence
from bash_dance.lexer import (
    lexer, Token, Line, Include, Ignore, Close
)

_test_docs = Path(__file__).absolute().parent / "test_docs"


class LexTest(NamedTuple):
    """Tuple for testing lexer with files."""
    path: Path
    reference: Sequence[Token]


_test_tokens_1 = LexTest(
    path=_test_docs / "test_docs_1.bash",
    reference=(
        Line("# test doc 1"), Line(),
        Line("# comment"),
        Line("line 1"),
        Line("line 2"), Line(),
        Include(reference="./lib/test_lib_a.bash"),
        Line("line 3"), Line(),
        Close(), Line(),
        Line("line 4"), Line(),
        Include(reference="./lib/test_lib_b.bash"),
        Line("line 5"), Line(),
        Close(), Line(),
        Ignore(),
        Line("line 6"),
        Close(), Line(),
        Line("line 7")
    )
)

_test_tokens_2 = LexTest(
    path=_test_docs / "test_docs_2.bash",
    reference=(
        Line("# test doc 2"), Line(),
        Line("# comment"),
        Line("line 2.1"),
        Line("line 2.2"), Line(),
        Ignore(),
        Line("line 2.ignore.1"),
        Line("line 2.ignore.2"),
        Close(), Line(),
        Include("./lib/test_lib_c.bash"),
        Line("line 2.ignore.1"),
        Line("line 2.ignore.2"),
        Close(), Line(),
        Line("line 2.3")
    )
)

def test_lexer():
    for token_file, ref_stream in (_test_tokens_1, _test_tokens_2):
        with token_file.open('r') as handle:
            tokens = tuple(lexer(handle.readlines()))
            assert tokens == ref_stream
