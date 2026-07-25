#!/usr/bin/env python3
"""Cut a cite2link release: bump version, commit, tag, push the tag.

HUMAN-run by default: pushing to main and tags is reserved for the maintainer.
An AI agent may run this script ONLY when a human has explicitly instructed it
to cut a release.

Usage:
    python3 scripts/release.py                      # patch bump, default message
    python3 scripts/release.py -m "fix parser"      # patch bump, custom message
    python3 scripts/release.py --minor -m "gc"      # minor bump
    python3 scripts/release.py --major -m "1.0"     # major bump
    python3 scripts/release.py --set 0.3.0 -m "..." # set an explicit version
    python3 scripts/release.py --no-bump            # tag the CURRENT version as-is

Self-guarding: the script establishes the right state instead of demanding you
set it up first. It refuses a dirty working tree, switches to main if you are on
another branch, and fast-forwards main to origin/main (failing only if local
main has unpushed/diverged commits a human must resolve). It is pure-stdlib and
operates on the repo root regardless of cwd. (`uv` must be on PATH: the script
shells out to `uv run` for the test suite.)

The library version is single-sourced in src/cite2link/__init__.py
(`__version__`); this script edits that one line and hatch derives the package
version from it.

The pushed `v<x.y.z>` tag triggers .github/workflows/release.yml, which re-runs
the tests on the tagged commit, builds the sdist + wheel with `uv build`,
publishes them to PyPI via Trusted Publishing (OIDC — no API token), and creates
a GitHub Release with the same artifacts attached.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INIT_PY = REPO_ROOT / "src" / "cite2link" / "__init__.py"

_VERSION_RE = re.compile(r'^(__version__\s*=\s*)"([^"]+)"', re.MULTILINE)


def run(cmd, *, capture=False, check=True):
    return subprocess.run(cmd, capture_output=capture, text=True, check=check, cwd=REPO_ROOT)


def get(cmd):
    return run(cmd, capture=True).stdout.strip()


def current_version():
    m = _VERSION_RE.search(INIT_PY.read_text())
    if not m:
        sys.exit(f"Could not find __version__ in {INIT_PY}")
    return m.group(2)


def bump(version, part):
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def parse_explicit_version(value, current, *, allow_major_jump=False):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        sys.exit(f"--set expects X.Y.Z (got {value!r}).")
    as_tuple = lambda v: tuple(int(p) for p in v.split("."))  # noqa: E731
    new, cur = as_tuple(value), as_tuple(current)
    if new <= cur:
        sys.exit(f"--set {value} is not greater than current {current}; refusing to downgrade.")
    if new[0] - cur[0] > 1 and not allow_major_jump:
        sys.exit(
            f"--set {value} raises the major version from {cur[0]} to {new[0]} "
            f"(more than one step) — almost always a typo. "
            f"If it is intentional, re-run with --allow-major-jump."
        )
    return value


def check_clean():
    if run(["git", "status", "--porcelain"], capture=True).stdout.strip():
        sys.exit("Working tree is not clean. Commit or stash changes first.")


def ensure_on_main():
    branch = get(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch != "main":
        print(f"On {branch!r}; switching to main...")
        run(["git", "checkout", "main"])


def sync_main():
    run(["git", "fetch", "--quiet", "origin"])
    local = get(["git", "rev-parse", "HEAD"])
    remote = get(["git", "rev-parse", "origin/main"])
    if local == remote:
        return
    ahead = get(["git", "rev-list", "--count", "origin/main..HEAD"])
    behind = get(["git", "rev-list", "--count", "HEAD..origin/main"])
    if ahead != "0":
        sys.exit(
            f"Local main is {ahead} commit(s) ahead of origin/main"
            + (f" and {behind} behind" if behind != "0" else "")
            + ". Push or reconcile before releasing."
        )
    print(f"Fast-forwarding main to origin/main ({behind} commit(s) behind)...")
    run(["git", "merge", "--ff-only", "origin/main"])


def check_tag_absent(tag):
    if run(["git", "tag", "--list", tag], capture=True).stdout.strip():
        sys.exit(f"Tag {tag} already exists locally. Delete it or choose another version.")
    if run(["git", "ls-remote", "--tags", "origin", tag], capture=True).stdout.strip():
        sys.exit(f"Tag {tag} already exists on origin. Choose another version.")


def run_tests():
    print("Running tests (uv run pytest)...")
    run(["uv", "run", "pytest"])


def set_version(new_version):
    text = INIT_PY.read_text()
    updated, n = _VERSION_RE.subn(rf'\g<1>"{new_version}"', text)
    if n != 1:
        sys.exit(f"Version substitution in {INIT_PY} affected {n} lines (expected 1).")
    INIT_PY.write_text(updated)


def prompt_message(part):
    if not sys.stdin.isatty():
        sys.exit(f"--{part} release requires a commit message; pass -m '<message>'.")
    try:
        msg = input(f"Commit message for {part} release: ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit("\nAborted.")
    if not msg:
        sys.exit("Commit message cannot be empty.")
    return msg


def main():
    parser = argparse.ArgumentParser(
        description="Cut a release. Defaults to --patch if no bump flag is given.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--major", dest="part", action="store_const", const="major")
    group.add_argument("--minor", dest="part", action="store_const", const="minor")
    group.add_argument("--patch", dest="part", action="store_const", const="patch")
    group.add_argument(
        "--set",
        dest="explicit",
        metavar="X.Y.Z",
        default=None,
        help="set an explicit version instead of bumping; must be > current",
    )
    group.add_argument(
        "--no-bump",
        dest="no_bump",
        action="store_true",
        help="release the CURRENT version as-is (no version change, no commit) — "
        "just tag HEAD and push the tag.",
    )
    parser.add_argument(
        "--allow-major-jump",
        action="store_true",
        help="permit --set to raise the major version by more than one step",
    )
    parser.add_argument("-m", dest="message", default=None, help="commit message")
    args = parser.parse_args()

    check_clean()
    ensure_on_main()
    sync_main()

    old = current_version()
    if args.no_bump:
        new = old
        label = "no-bump"
    elif args.explicit:
        new = parse_explicit_version(args.explicit, old, allow_major_jump=args.allow_major_jump)
        label = "set"
    else:
        label = args.part or "patch"
        new = bump(old, label)

    tag = f"v{new}"

    if args.message:
        message = args.message
    elif label == "patch":
        message = "misc fixes/enhancements"
    elif label == "no-bump":
        message = f"release {tag}"
    else:
        message = prompt_message(label)

    check_tag_absent(tag)
    run_tests()

    if args.no_bump:
        print(f"Releasing current version {new} (no bump)")
    else:
        verb = "Setting" if args.explicit else "Bumping"
        print(f"{verb} {old} -> {new}")
        set_version(new)
        run(["git", "add", "src/cite2link/__init__.py"])
        # DCO sign-off (we work in DCO-enforced repos and sign every commit).
        run(["git", "commit", "-s", "-m", f"Release {tag}: {message}"])
        run(["git", "push", "origin", "main"])

    run(["git", "tag", "-a", tag, "-m", f"Release {tag}: {message}"])
    run(["git", "push", "origin", tag])

    print(f"Tagged and pushed {tag}. The release workflow will build and attach assets.")


if __name__ == "__main__":
    main()
