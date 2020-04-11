from pathlib import Path
from typing import List, Tuple, Iterator, Iterable
from dataclasses import dataclass
import re

_directive_prefix = "#%"
_match_closed = re.compile(r"#%\s*}")


def _block_start_matcher(reg_str: str):
    return re.compile(r"#%\s*" + reg_str + "\s*{")


class ParseStream:
    line_it: Iterator[str]
    look: str
    state: str
    line_num: int

    def __init__(self, lines: Iterable[str]):
        self.line_it = iter(lines)
        self.state = "initialized"
        self.look = ""
        self.line_num = 0

    def start(self):
        if self.state != "initialized":
            raise NotImplementedError

        reg = next(self.line_it, None)
        if reg is None:
            self.state = "done"
        else:
            self.look = reg.rstrip()
            self.state = "running"

    def advance(self) -> bool:
        """Shift stream forward."""
        if self.state == "initialized":
            raise NotImplementedError

        if self.state == "done":
            return False

        reg = next(self.line_it, None)
        if reg is None:
            self.state = "done"
            return False

        self.line_num += 1
        self.look = reg.rstrip()
        return True

    def is_done(self) -> str:
        """Is stream complete."""
        return self.state == "done"


def _recognize_block_suffix_ignore(stream):
    while not stream.is_done():
        if re.match(_match_closed, stream.look) is not None:
            return
        stream.advance()
    raise Error()


class Recognizer:
    @classmethod
    def recognize(cls, stream: ParseStream, output: List[str]):
        raise NotImplementedError


@dataclass
class Include(Recognizer):
    match_directive = _block_start_matcher(r"include\s+\"(.*)\"")
    line_range: Tuple[int, int]
    reference: Path

    @classmethod
    def recognize(cls, stream: ParseStream, output: List[str]):
        m = re.match(cls.match_directive, stream.look)
        if m is None:
            return None

        ref = Path(m.group(0))
        st = stream.line_num
        stream.advance()
        _recognize_block_suffix_ignore(stream)
        return cls((st, stream.line_num), ref)


@dataclass
class Ignore(Recognizer):
    match_directive = _block_start_matcher(r"ignore")
    line_range: Tuple[int, int]

    @classmethod
    def recognize(cls, stream: ParseStream, output: List[str]):
        m = re.match(cls.match_directive, stream.look)
        if m is None:
            return None

        st = stream.line_num
        stream.advance()
        _recognize_block_suffix_ignore(stream)
        return cls((st, stream.line_num))


class Script:
    path: Path
    output: List[str]
    recognizers: List[Recognizer] = [Include, Ignore]
    stream: ParseStream
    features: List[Recognizer]
    done: bool

    def __init__(self, source: Path):
        self.path = source
        self.output = []
        self.features = []
        self.done = False
        with source.open('r') as fh:
            self.stream = ParseStream(fh)
            self.parse()

    def parse(self, cache: 'ScriptCache' = ScriptCache()):
        self.stream.start()
        while not self.stream.is_done():
            if not self.stream.look.startswith(_directive_prefix):
                self.output.append(self.stream.look)
                self.stream.advance()
                continue

            for recognizer in self.recognizers:
                feature = recognizer.recognize(self.stream, self.output)
                if feature is not None: 
                    self.features.append(feature)
                    self.stream.advance()
                    break
            else:
                raise Error(f"Could not recognize {stream.look}")
        self.done = True


class ScriptCache:
    scripts: dict

    def __init__(self):
        self.scripts = dict()

    def process(self, path: Path):
        if path in self.scripts:
            script = self.scripts[path]
            if not script.done:
                raise Error("Dep cycle.")
                return script

        script = Script(path)
        self.scripts[path] = script
        script.parse()


_script_cache = ScriptCache()


def main():
    print("Running parser.")
    path = Path("./lib/lib.bash")
    script = _script_cache.process(path)

    print("\nFeatures")
    for f in script.features:
        print(f)

    print("\nOutput")
    for f in script.output:
        print(f)


if __name__ == "__main__":
    main()
