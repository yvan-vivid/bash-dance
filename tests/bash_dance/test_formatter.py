"""Formatter tests."""

from io import StringIO
from pathlib import Path
from typing import NamedTuple, Sequence

from bash_dance.formatter import (
    Formatter, Token, Line, Prefix, Suffix
)

_hr = 80*"#"

class FormatTest(NamedTuple):
    """Formatter test case"""
    tokens: Sequence[Token]
    reference: str


_test_path = Path("./test/path.bash")

_format_test_1 = FormatTest(
    (
        Line("first line"),
        Line("second line"), Line(),
        Prefix(_test_path, True),
        Line("third line"),
        Prefix(_test_path, False),
        Line("inside prefix"),
        Line("also inside prefix"),
        Suffix(_test_path, False),
        Line("fourth line"), Line(),
        Suffix(_test_path, True),
        Line("last line"),
    ),
    f"first line\nsecond line\n\nthird line\n"
    f"{_hr}\n## start \"{_test_path.name}\"\n{_hr}\n\n"
    f"inside prefix\nalso inside prefix\n"
    f"\n{_hr}\n## end \"{_test_path.name}\"\n{_hr}\n"
    f"fourth line\n\nlast line"
)


def test_formatter():
    buff = StringIO()
    formatter = Formatter(buff)
    tokens, reference = _format_test_1
    for token in tokens:
        formatter.write(token)
    output = buff.getvalue()
    assert output == reference
