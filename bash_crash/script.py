"""Scripts"""

from pathlib import Path
from typing import Dict, Set, Tuple, Union, Iterator, Optional, Sequence
from typing_extensions import Literal

from bash_crash.lexer import (
    lexer, Token, Line, Include, Ignore, Close
)
from bash_crash.resolver import Resolver


class Script:
    path: Path
    frame: 'ScriptFrame'
    state: Literal["init", "running", "done"]

    def __init__(self, path: Path, frame: 'ScriptFrame'):
        self.path = path
        self.frame = frame
        self.state = "init"

    def process(self):
        self.state = "running"
        with self.path.open('r') as handle:
            token_stream = lexer(line.rstrip() for line in handle)
            self.process_tokens(token_stream)
        self.state = "done"

    def process_tokens(self, tokens: Iterator[Token]):
        state: Literal["pass", "block"] = "pass"
        block_head: Union[Include, Ignore, None] 
        for token in tokens:
            if state == "pass" and isinstance(token, Line):
                print(token.line)
            elif state == "pass" and isinstance(token, (Ignore, Include)):
                block_head = token
                state = "block"
            elif state == "block" and isinstance(token, Close):
                if isinstance(block_head, Include):
                    self.include_action(block_head)
                state = "pass"
            elif state == "block" and isinstance(token, Line):
                pass
            else:
                raise ValueError("Parsing error")

    def include_action(self, head: Include):
        self.frame.require(head.reference, self.path)


class ScriptFrame:
    scripts: Dict[Path, Script]
    dependencies: Set[Tuple[Path, Path]]
    resolver: Resolver

    def __init__(self, resolver: Optional[Resolver] = None):
        self.scripts = {}
        self.dependencies = set()
        if resolver is None:
            self.resolver = Resolver(())
        else:
            self.resolver = resolver

    def require(
        self, path_specifier: str, source: Optional[Path] = None
    ) -> Script:
        path = self.resolver.resolve(path_specifier, source)

        if path in self.scripts:
            script = self.scripts[path]
            if script.state != "done":
                raise ValueError("Include cycle")
            return script

        script = Script(path, self)
        self.scripts[path] = script
        if source is not None:
            self.dependencies.add((source, path))
        script.process()

        return script
