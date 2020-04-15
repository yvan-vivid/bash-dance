"""Tool to preprocess bash scripts."""

from argparse import ArgumentParser
from pathlib import Path
from io import StringIO
import sys
import logging

from bash_dance.script import ScriptFrame, ParsingError
from bash_dance.formatter import Formatter
from bash_dance.resolver import Resolver
from bash_dance.lexer import LexicalError

def _arg_setup() -> ArgumentParser:
    parser = ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "input",
        type=Path,
        help="input file",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="output file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count", default=0,
        help="logging verboseness",
    )
    parser.add_argument(
        "--include", "-I",
        action="append",
        type=Path,
        default=[],
        help="include search path item",
    )
    return parser


def _log_setup(args):
    level = logging.WARN
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose > 1:
        level = logging.DEBUG

    logging.basicConfig(level=level)
    logging.info("Showing info log.")
    logging.debug("Showing debugging information.")

def run():
    """Entrypoint for tool."""
    args = _arg_setup().parse_args()
    _log_setup(args)

    logging.info("Setting up resolver with includes = %s", args.include)
    resolver = Resolver(paths=args.include)

    buff = StringIO()
    formatter = Formatter(buff)

    logging.info("Processing %s", args.input)
    frame = ScriptFrame(formatter, resolver)

    try:
        frame.construct(args.input)
    except LexicalError as ex:
        logging.error("Lexical Error: %s", ex)
        sys.exit(1)
    except ParsingError as ex:
        logging.error("Parsing Error: %s", ex)
        sys.exit(1)

    if args.output is None:
        logging.info("Writing to standard out.")
        print(buff.getvalue())
    else:
        logging.info("Writing to file %s", args.output)
        with args.output.open("w") as handle:
            handle.write(buff.getvalue())

    logging.info("Done.")

if __name__ == "__main__":
    run()
