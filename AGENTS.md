# Working on cite2link

Orientation and conventions for humans and AI agents. cite2link is a small,
dependency-free Python library (`src/cite2link/`) with a thin CLI. Read
[docs/architecture.md](docs/architecture.md) for how the pieces fit together.

## Environment & commands

The project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # set up the environment from uv.lock
uv run pytest           # tests (runs with coverage; fail_under = 95)
uv run ruff check .     # lint
uv run ruff format .    # format
uv run cite2link "..."  # run the CLI from the checkout
```

CI runs the tests across Python 3.10–3.13, plus ruff and a Trojan-Source
Unicode guard; keep all of them green.

## Conventions

- **True TDD.** Add or adjust a failing test first, then make it pass. Never
  leave the suite red or coverage below the floor.
- **Behavior-preserving refactors must keep CLI output byte-identical.** The
  golden tests in `tests/link_test.py` encode the exact URL/HTML/Markdown
  output; if you intend to change output, change the tests deliberately.
- **Types and idioms.** New code is type-hinted and passes ruff (`E, F, I, UP,
  B, W`). Prefer f-strings, comprehensions, and specific exceptions
  (`cite2link.errors`) over bare `Exception`.
- **Single-sourced version.** `__version__` in `src/cite2link/__init__.py` is
  the only place the version lives; cut releases with `scripts/release.py`.
- **Pin new GitHub Actions to a full commit SHA** with a `# vN` comment, on a
  node24 runtime.
- **The `gc.py` General Conference feature is intentionally inert** (tick
  `~4g46`); don't wire it into the CLI or add a hard `requests` dependency
  without finishing it properly.

<!-- >>> tick stanza >>> (managed by `tick init`) -->

## Task tracking: `tick`

This repo tracks tasks, tech debt, and ideas in a local [`tick`](https://github.com/dhh1128/tick)
ledger (an orphan `tick` branch; the `tick` CLI is the interface). Reads are plain
files — do **not** use an external API for task tracking.

- **First, if a `tick` command says the repo isn't initialized**, run `tick init`
  once to connect this clone to the ledger — it adopts the existing remote ledger
  if a colleague already set one up, or creates a new one otherwise.
- **A tick mark is the sigil `~` immediately followed by a digit-first 4-char
  base32 id** (the id part looks like `4mz3`, so the full mark is that id with a
  leading `~`). It pins a tick to a code location.
- **Before editing a file**, grep it for marks and read what they reference:
  `rg '~[2-7][a-z2-7]{3}\b' <file>` then `tick show <id>`. A mark means recorded
  context exists for that spot — read it first.
- **Search** existing ticks with `tick grep <text>`; **list** with `tick ls`.
- **Capture** new work with `tick add "<title>"` and place the printed mark
  (`~` + the new id) at the relevant code spot.
- When your change **resolves** a tick, run `tick off <id>` and **delete the
  mark(s)** it reports still in the code.

<!-- <<< tick stanza <<< -->
