import re
import sys

from .cite import resolve
from .link import print_all

help_pat = re.compile(r"[?]|--?h(elp)?", re.I)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 2 or len(argv) == 2 and help_pat.match(argv[1]):
        print("cite2link Genesis 1:1 (or any other scripture reference)\n")
    else:
        ref = " ".join(argv[1:])
        try:
            book, chapter, verses = resolve(ref)
            print_all(book, chapter, verses)
        except Exception:
            import traceback

            traceback.print_exc()
            sys.stderr.write("Can't resolve reference; check syntax or name of book.")
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
