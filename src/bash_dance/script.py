"""Script parser and processor."""

import logging
from pathlib import Path
from typing import (
Dict, Set, Tuple, Union, Iterator, Optional
)
from typing_extensions import Literal

from bash_dance.lexer import (
lexer, Token, Line, Include, Ignore, Close
)
from bash_dance.resolver import Resolver
from bash_dance.formatter import Formatter
import bash_dance.formatter as F

ScriptState = Literal["init", "running", "done"]

class ParsingError(Exception):
    """Error involving token organization."""


class Script:
    """Processing container for a single script."""
    path: Path
    frame: 'ScriptFrame'
    state: ScriptState
    formatter: Formatter

    def __init__(self, path: Path, frame: 'ScriptFrame'):
        self.path = path
        self.frame = frame
        self.state = "init"
        self.formatter = frame.formatter

    def _write(self, token: F.Token):
        self.formatter.write(token)

    def process(self):
        """Run processor."""
        is_root = self.path in self.frame.roots
        self.state = "running"
        with self.path.open('r') as handle:
            self._write(F.Prefix(self.path, is_root))
            self._process_tokens(lexer(handle))
            self._write(F.Suffix(self.path, is_root))
        self.state = "done"

    def _process_tokens(self, tokens: Iterator[Token]):
        state: Literal["pass", "block"] = "pass"
        block_head: Union[Include, Ignore, None]
        for token in tokens:
            if state == "pass" and isinstance(token, Line):
                self._line_action(token)
            elif state == "pass" and isinstance(token, (Ignore, Include)):
                block_head = token
                state = "block"
            elif state == "block" and isinstance(token, Close):
                if isinstance(block_head, Include):
                    self._include_action(block_head)
                state = "pass"
            elif state == "block" and isinstance(token, Line):
                pass
            else:
                raise ParsingError("Parsing error")

    def _include_action(self, head: Include):
        self.frame.construct(head.reference, self.path)

    def _line_action(self, line: Line):
        self._write(F.Line(line.line))

class ScriptFrame:
    """Processing frame for script and its dependencies."""
    scripts: Dict[Path, Script]
    dependencies: Set[Tuple[Path, Path]]
    resolver: Resolver
    roots: Set[Path]
    formatter: Formatter

    def __init__(
        self,
        formatter: Formatter,
        resolver: Resolver
    ):
        self.scripts = {}
        self.dependencies = set()
        self.roots = set()
        self.formatter = formatter
        self.resolver = resolver

    def construct(
        self,
        path_specifier: Union[str, Path],
        source: Optional[Path] = None
    ) -> Script:
        """Construct output to formatter given a path or specifier."""
        if isinstance(path_specifier, str):
            path = self.resolver.resolve(path_specifier, source)
        else:
            path = path_specifier
        canonical = self.resolver.canonicalize(path)

        # resolve already processed scripts
        script_ref = self.scripts.get(path, None)
        if script_ref is not None:
            if script_ref.state == "done":
                logging.info("Confluent reference to [%s].", canonical)
                return self.scripts[path]
            if script_ref.state == "running":
                raise ParsingError("Include cycle")

        # handle new scripts
        if source is None:
            self.roots.add(path)
            logging.info("Constructing root [%s].", canonical)
        else:
            self.dependencies.add((source, path))
            source_canonical = self.resolver.canonicalize(source)
            logging.info(
                "Constructing dependency [%s] from [%s].",
                canonical, source_canonical
            )
        script = Script(path, self)
        self.scripts[path] = script
        script.process()
        return script
