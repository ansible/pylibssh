# Workflow & Tooling Infrastructure

The project uses `tox` as the single entry point for all local
automation -- the same one CI and core devs use. Agents must
never bypass it by invoking the wrapped tools (`pytest`,
`pre-commit`, `coverage`, `towncrier`, etc.) directly; doing so
skips project-specific configuration and is liable to run with
unsupported, undefined, or outright dangerous defaults.

## `tox list` is the source of truth

The contributing docs mention some environments, but that's not
exhaustive or authoritative -- `tox list` is. Run it to see
every available environment, each with its own description.
Don't assume an environment exists, or what it does, without
checking there first.

## Running tests

`tox run -e py` runs the test suite under whichever Python
runtime is currently active. Other environments cover other
purposes (lint, docs build, changelog draft/check, packaging,
etc.) -- check `tox list` rather than assuming `py` is the only
one relevant to a given task.

## Default to low verbosity

Prefer `tox run -e py -qq` by default. Only reach for more
verbose tox-level output (drop the `-q`, or add `-v`/`-vv`) once
there's an actual reason to inspect tox's own internals -- don't
lead with a wall of logs.

## Spell commands out

Use the long subcommand forms -- `tox run`, `tox list`,
`tox config` -- in automation, docs, and anything shown to the
operator. `tox r`/`tox l` are fine interactively but easy to
misread in scripts and CI logs.

Don't invent flags. Check `tox <subcommand> --help` when unsure:
e.g. env selection is `-e` only, there's no `--env`.

## `pyNNN`-style environment names are native tox behavior

`tox run -e py312` isn't something this project specifically
configured -- it's tox's own built-in convention: an env name
matching `pyNN`/`pyNNN` makes tox look up a `python3.N`
interpreter and create/use `.tox/py312` for it, if available.
This, and other generic tox mechanics not specific to this
project, are covered by tox's own documentation -- read that
rather than expecting everything generic about tox to be
re-explained here.

## Passing arguments through to the wrapped tool

Arguments after a bare `--` are forwarded to whatever tool the
environment wraps. For example, `tox run -e py -- -n0` passes
`-n0` to `pytest`, disabling `pytest-xdist` parallelism for that
run -- safe here since this project's `py`/`just-pytest` envs
both use a bare `{posargs:}` with an empty default in `tox.ini`,
so there's nothing to lose.

That's not true everywhere, though: when a `commands =` line uses
`{posargs:<default value>}` with a *non-empty* default, anything
passed after `--` **replaces that default wholesale** -- it does
not get appended to it. Two real examples from this project's own
`tox.ini`:

- `build-docs`'s Sphinx invocation defaults to a full flag set
  (`-j auto -b html ... -a -n -W --keep-going -d ... . <output>`)
  via `{posargs:...}` -- passing any custom posargs there replaces
  the whole thing, not just adds to it.
- `make-changelog`'s default posargs are `'[UNRELEASED DRAFT]'
  --draft` (draft-preview mode); its own `description` field
  documents overriding this deliberately -- passing a real version
  after `--` (e.g. `tox run -e make-changelog -- 1.3.2`) switches
  it into actually cutting that release, dropping `--draft`
  entirely.

Always check what a given env's default posargs actually are
(`tox config -e <env>`, or read `tox.ini`) before assuming `--`
just "adds more flags."

## Read the tool's own output

`build-docs` prints follow-up instructions after running -- where
the built HTML docs landed, and how to serve them locally. `lint`
prints a reminder of how to install its pre-commit hooks into
Git. Read what the invocation actually printed instead of
guessing a path or a next step.

## Red checks get fixed, not silenced

When `lint`, `py`, or any other env reports failures, fix their
cause. Suppressing a finding, or skipping/removing a test, is the
operator's decision -- see
[DONT_SHOOT_THE_MESSENGER.md](DONT_SHOOT_THE_MESSENGER.md).

## Shared automation across projects

The maintainer looks after many open source projects, at work and
on personal time, and shares automation between them in various
forms -- CI workflows, composite actions, tool configs, these
agent docs. Drift between similar projects makes that harder.

When changing shared tooling, consider whether the change is
generic or project-specific. If it looks generic, point that out
to the operator so it can be propagated -- don't propagate it
yourself. Drift is fine when there's a deliberate reason for it.
