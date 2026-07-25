"""Exception types raised by cite2link.

A single small hierarchy so callers (and the CLI) can catch everything this
library raises with ``except Cite2LinkError`` while still distinguishing the
specific failure.
"""

from __future__ import annotations


class Cite2LinkError(Exception):
    """Base class for every error cite2link raises."""


class BadVerseRange(Cite2LinkError, ValueError):
    """A verse specification is malformed or a range descends (e.g. ``5-3``).

    Subclasses ``ValueError`` too, so existing ``except ValueError`` callers
    keep working.
    """
