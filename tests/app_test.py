import pytest

from cite2link import __version__
from cite2link.app import main


def test_main_happy_path(capsys):
    rc = main(["John 3:15"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "short ref\n  John 3:15" in out
    assert "nt/john/3.15?lang=eng#p14" in out
    assert '<a href="' in out  # html style
    assert "](https://" in out  # markdown style


def test_main_accepts_multiple_argv_tokens(capsys):
    # The reference may arrive as several argv tokens; they are joined.
    rc = main(["Hel", "5:1,", "3-5,", "7"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "bofm/hel/5.1,3-5,7?lang=eng" in out


def test_main_unresolvable_book(capsys):
    rc = main(["Nonexistent 3:4"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "could not resolve" in err


def test_main_bad_verse_range(capsys):
    # A descending range raises BadVerseRange (a Cite2LinkError); the CLI turns
    # it into a clean message and a non-zero exit rather than a traceback.
    rc = main(["John 3:5-3"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "cite2link:" in err


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_main_no_args_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err
