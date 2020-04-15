"""Path resolution
    This resolution approximates that of node.js and the like. There is given
    root directory <root> that is used as a reference point. A list of library
    paths are given as well. Each path of the form:

        path/to/library.ext

    is searched for in the given library paths, including the root (last). If
    a path begins with a './' or '../', this indicates a reference relative to
    the path of the referring file. Hence:

        ../location/of/library.ext

    referred to from

        path/to/referring.ext

    resolves to

        path/location/of/library.ext
"""

from pathlib import Path
from typing import Optional, Sequence, Dict, Tuple

Peer = Optional[Path]

class Resolver:
    """Resolves specifiers to paths using library list."""
    search_paths: Sequence[Path]
    resolutions: Dict[Tuple[str, Peer], Path]
    reverse: Dict[Path, str]
    root: Path

    def __init__(
        self,
        root: Path = Path("."),
        paths: Optional[Sequence[Path]] = None,
    ):
        self.search_paths = [] if paths is None else list(paths)
        self.search_paths.append(root)
        self.resolutions = dict()
        self.reverse = dict()
        self.root = root

    def _record_resolution(self, key: Tuple[str, Peer], path: Path):
        self.resolutions[key] = path
        self.canonicalize(path)

    def canonicalize(self, path: Path) -> str:
        """Using search path give a canonical specifier."""
        if path in self.reverse:
            return self.reverse[path]

        for search_path in self.search_paths:
            search_path = search_path.absolute()
            try:
                relative = path.relative_to(search_path)
                canonical = str(relative)
                break
            except ValueError:
                pass
        else:
            canonical = str(path)

        self.reverse[path] = canonical
        return canonical

    def resolve(self, specifier: str, peer: Peer = None) -> Path:
        """Resolve a specifier to a path.
            If 'peer' is given, resolve relative paths.
        """
        key = (specifier, peer)
        if key in self.resolutions:
            return self.resolutions[key]
        if specifier.startswith(("./", "../")):
            if peer is not None:
                path = peer.parent / specifier
            else:
                path = Path(specifier)
            if not path.is_file():
                raise ValueError(f"Path {specifier} does not exist.")
            path = path.absolute()
            self._record_resolution(key, path)
            return path

        for search_path in self.search_paths:
            path = search_path / specifier
            if path.is_file():
                return path.absolute()

        raise ValueError("Cannot find {specifier} in search path.")
