"""Resolver tests."""

from pathlib import Path
from bash_dance.resolver import Resolver

_test_docs = Path(__file__).absolute().parent / "test_docs"
_test_docs_1 = Path(_test_docs / "test_docs_1.bash")
_test_docs_2 = Path(_test_docs / "test_docs_2.bash")
_test_lib_a = Path(_test_docs / "lib/test_lib_a.bash")
_test_lib_b = Path(_test_docs / "lib/test_lib_b.bash")

def _same_paths(a: Path, b: Path):
    assert a.samefile(b)


def test_resolve():
    resolver = Resolver(_test_docs)
    _same_paths(_test_docs_1, resolver.resolve("test_docs_1.bash"))
    _same_paths(_test_lib_a, resolver.resolve("lib/test_lib_a.bash"))

def test_resolve_with_peer():
    resolver = Resolver(_test_docs)
    _same_paths(
        _test_lib_a,
        resolver.resolve("./test_lib_a.bash", _test_lib_b),
    )
    _same_paths(
        _test_lib_a,
        resolver.resolve("./lib/test_lib_a.bash", _test_docs_1),
    )
    _same_paths(
        _test_docs_1,
        resolver.resolve("../test_docs_1.bash", _test_lib_a),
    )

def test_resolve_with_lib():
    resolver = Resolver(_test_docs, (_test_docs / "lib",))
    _same_paths(_test_lib_a, resolver.resolve("test_lib_a.bash"))

def test_canonicalize():
    resolver = Resolver(_test_docs)
    assert resolver.canonicalize(_test_docs_1) == "test_docs_1.bash"
    assert resolver.canonicalize(_test_lib_a) == "lib/test_lib_a.bash"

def test_canonicalize_with_lib():
    resolver = Resolver(_test_docs, (_test_docs / "lib",))
    assert resolver.canonicalize(_test_lib_a) == "test_lib_a.bash"
