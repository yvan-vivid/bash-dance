"""Path resolvers"""

from pathlib import Path
from typing import Optional, Sequence

class Resolver:
    search_paths: Sequence[Path]

    def __init__(self, paths: Sequence[Path]):
        self.search_paths = list(paths)
        self.search_paths.append(Path("."))

    def resolve(self, specifier: str, peer: Optional[Path] = None) -> Path:
        if specifier.startswith(("./", "../")):
            if peer is not None:
                path = peer.parent / specifier
            else:
                path = Path(specifier)
            if not path.is_file():
                raise ValueError(f"Path {specifier} does not exist.")
            return path.absolute()

        for search_path in self.search_paths:
            path = search_path / specifier
            if path.is_file():
                return path.absolute()

        raise ValueError("Cannot find {specifier} in search path.")
