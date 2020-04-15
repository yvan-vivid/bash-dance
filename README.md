# Bash/Dance -- Yvan Vivid

This is a tool I created for the primary purpose of inlining `bash` files using a simple macro language embedded in comments. It could do more than it does with a little more work. At the moment, the motivation was that I wanted to develop a small bash library, write scripts that used it, then inline the libraries with the script into a single monolithic file, so that it could be easily downloaded as a self-contained bootstrap script for system configuration tasks.

In principle, this could be used with any simple shell scripting language that has include commands such as `source` or `.` that could be inlined without any side-effects. There is a lot of customization that could be done to this, but for now it is rooted in my own idiosyncratic aesthetic choices.

## Macro Language

Given a script like the following
```
# Beginning comment

echo "Doing tasks"

source "./library/module.bash"

command_from_module params

echo "Finished"
```

Directives can be added to replace the sourcing command with direct inline substitution

```
# Beginning comment

echo "Doing tasks"

#% include "module.bash" {
source "./library/module.bash"
#% }

command_from_module params

echo "Finished"
```

**Bash/Dance** substitutes in the content of `module.bash`, surrounding it in comment blocks.
```
# Beginning comment

echo "Doing tasks"

################################################################################
## start "module.bash"
################################################################################

command_from_module() {
  echo "Library actions"
}

################################################################################
## end "module.bash"
################################################################################

command_from_module params

echo "Finished"
```

Indeed, this process is recursive, so that inlined files are themselves inlined, throwing an error if there is a cyclic dependency. If there is a non-cyclic recurrance of the same file being inlined, only the first instance is included in the order of the depth-first traversal of the dependency graph.

There is also a directive to simply ignore sections.
```
# Beginning comment

echo "Doing tasks"

#% ignore {
echo "Only do when not inlined"
#% }

echo "Finished"
```

## CLI

The primary invocation is as follows

```
bash-dance <input-file> -o <output-file> -I ./path/to/library -I /other/library
```

If the `-o <output-file>` is omitted the output is written to `stdout`. The `-I` parameters add search paths to look for libraries. The current directory is included by default at the lowest precedences. Excluding this might be useful, but alas is among the many things not yet done.

## Building

This should build straightforwardly given python is available on ones system. In a typical unix-like environment `make` should do the following:
1. Build a tooling virtual environment and install the `poetry` tool in it.
2. Build an development virtual environment and install the package dependencies in it.
3. Run tests and the linter.

The entrypoint will be available in the development virtual environment. Either step into it with
`. .venv/bin/activate` and run it, or call it directly as `.venv/bin/bash-dance`.
