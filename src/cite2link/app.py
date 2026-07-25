"""Command-line entry point for cite2link."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__
from .cite import resolve
from .errors import Cite2LinkError
from .link import print_all


def build_parser() -> argparse.ArgumentParser:
    # ~5np2 Future: default to emitting a naked URL, with --md/--html (etc.)
    # flags to opt into the extra renderings that print_all currently shows.
    parser = argparse.ArgumentParser(
        prog="cite2link",
        description="Convert a scripture citation into hyperlinks "
        "(canonical URL, short/long reference, HTML, and Markdown).",
    )
    parser.add_argument(
        "reference",
        nargs="+",
        metavar="REFERENCE",
        help='a citation, e.g. "John 3:15" or "Hel 5:1, 3-5, 7"',
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ref = " ".join(args.reference)
    try:
        resolved = resolve(ref)
    except Cite2LinkError as e:
        print(f"cite2link: {e}", file=sys.stderr)
        return 1
    if resolved is None:
        print(
            f"cite2link: could not resolve {ref!r}; check the book name and syntax.",
            file=sys.stderr,
        )
        return 1
    print_all(*resolved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
