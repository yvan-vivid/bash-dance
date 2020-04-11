"""Tool to preprocess bash scripts."""

from pathlib import Path
import sys

from bash_crash.script import ScriptFrame

def run():
    if len(sys.argv) < 2:
        print("path of file.")
        sys.exit(1)

    frame = ScriptFrame()
    frame.require(sys.argv[1])

    print("Done.")

if "__main__" == __name__:
    run()
