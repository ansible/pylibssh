# House Style

Grounded in the project's own review history, plus explicit
maintainer conventions carried over from other projects — not
guesses.

## No new `@`-syntax in memory files

Do not introduce additional Claude `@`-mention/import syntax inside
any file under `.agents-ctx/`. The existing chain (`CLAUDE.md` ->
`AGENTS.md` -> `.agents-ctx/HOUSE_RULES.md`) is the only sanctioned
use of `@`-imports.

`@`-mentions load eagerly, at the start of every session, whether
or not the content ends up being relevant. Everything reachable
from `HOUSE_RULES.md` onward links to further material with plain
Markdown links instead, so an agent can pull it into context on
demand -- when a task actually needs it -- rather than having the
whole tree pollute the context window up front.

## Structural constraints

- No `setup.py`. Packaging metadata is declarative; don't
  reintroduce an imperative build script.
- No `tests/__init__.py`. Pytest must not promote the project
  root into `sys.path` via package discovery.

Here: `setup.py` was dropped in `b08a7fd4`. The metadata lives in
the PEP 621 `[project]` table of `pyproject.toml` (see
[NAMING_THE_DUCKS.md](NAMING_THE_DUCKS.md)).

## Python

- `typing` is aliased as `_t` (see [PR_HYGIENE.md](PR_HYGIENE.md)),
  `collections.abc` as `_c`.
- Tuples for fixed-size sequences such as command arguments or
  `parametrize` values; lists only where something needs to
  mutate them, or where a tool documents a list as its
  convention (e.g. `pytest_plugins`).
- Single quotes for inline strings, triple-double quotes for
  multi-line strings.
- `from __future__ import annotations` in every *new* `.py`
  module. Don't add it to existing modules as a side effect of an
  unrelated change, and not in Cython sources.
- Compose shell commands as argument sequences, or with
  `shlex.join` when a string is unavoidable. Never `shell=True`,
  never raw string concatenation into a subprocess.
- Sphinx-native docstrings -- `:param X:`, `:returns:`,
  `:raises X:`. Not Google, not Napoleon, not NumPy.

Here: quotes and `parametrize` tuples are enforced by
`.ruff.toml`, and the docstring style by `.darglint`.

## Configuration files

- YAML uses no-indent sequences (`- foo` at the same indent as
  its key).
- Long YAML values use a `>-` or `|-` block rather than
  trailing-backslash continuation.
- GitHub Actions `if:` expressions starting with `!` go in a `>-`
  block to keep them out of YAML's quoting rules.

Here: no-indent sequences are enforced by `.yamllint`; see
`.github/workflows/ci-cd.yml` for the block style.

## Markdown

- Admonitions use the GitHub-flavoured `> [!note]` /
  `> [!tip]` / `> [!important]` / `> [!warning]` /
  `> [!caution]` syntax.
- Inline code uses *single* backticks. Double backticks are RST,
  not Markdown -- easy to mix up here, since the docs and change
  notes are RST.
- Prefer detached link definitions, grouped close to the
  paragraphs that use them rather than dumped at the bottom of
  the file. Inline `[text](url)` is fine when the URL appears once
  and the line stays readable.

## Links

Link Read the Docs projects through the shorter
`<project>.rtfd.io` domain, which redirects to `readthedocs.io` --
especially in code comments, where line length matters.

## Keep encoded-bytes objects alive when backing a `char*`

Assigning an intermediate result straight into a `char*`/`const
char*` (e.g. `cdef char* c_buf = value.encode("utf-8")`) is a
segfault waiting to happen: the encoded `bytes` object has no
Python reference keeping it alive, so it can be garbage-collected
while the pointer is still in use, leaving `c_buf` dangling.
Assign the encoded bytes to a named Python variable first and
keep that variable alive for as long as the pointer is used. When
you do this, add a code comment explaining why, citing Cython's
own docs on the gotcha:
https://cython.rtfd.io/en/latest/src/tutorial/strings.html#encoding-text-to-bytes
(PR #875).

## Cython still shims the removed Python 2 `unicode` name

Even under `language_level = 3`, Cython keeps `unicode` available
as a shim for `str`
(https://cython.rtfd.io/en/latest/src/tutorial/strings.html#python-string-types-in-cython-code),
which reads as confusing coming from plain Python 3, where
`unicode` doesn't exist. Don't be surprised to see it in Cython
code or docs, but don't introduce new uses of it -- prefer `str`.

A related open TODO, not yet acted on: unifying the
`language_level` compiler directive to a single explicit value
across the codebase, rather than leaving it implicit/inconsistent
(PR #875).

## The extension modules hold the GIL while in libssh

The Cython modules call into libssh without releasing the GIL, so
a blocking call -- connecting, authenticating, waiting on a
channel -- stalls every other Python thread in the process.
Anything that has to keep running meanwhile, like a server or
relay test double, needs a separate process.

## `str | bytes`-style type hints aren't enforced at runtime here

Union type annotations on Cython-extension methods (e.g. `data:
str | bytes`) aren't actually enforced at runtime by
CPython/Cython -- they have the same effect as a docstring, not
real validation. Don't treat a Union annotation as a substitute
for actual input-coercion/validation logic (PR #870/#874
discussion).

## No automated formatter for `.pyx` -- wrap long lines by hand

Unlike `.py` files (formatted by `ruff format`), there's
currently no formatter tool that works on Cython source. Long-line
wrapping in `.pyx` files is done by hand, following ordinary
Python-style continuation conventions -- not C-style formatting
habits (PR #869).
