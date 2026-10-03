# Don't Shoot the Messenger

> [!important]
>
> Linters, type checkers, coverage, and tests are messengers. When
> one of them reports a problem, fix the problem -- don't silence
> the messenger. Whether a check gets silenced is always the
> operator's decision, made case by case, never the agent's.

## What counts as silencing

All of these need an explicit, per-case decision from the
operator.

Linters, type checkers, coverage:

- Inline suppressions: `# noqa[: ...]`, `# ruff: noqa`,
  `# flake8: noqa`, `# type: ignore[...]`, `# mypy: ignore-errors`,
  `# pylint: disable=...`, `# pragma: no cover`.
- Config-level ignores: `per-file-ignores`, `extend-ignore`,
  `exclude` entries, and similar in `.flake8`, `.ruff.toml`, mypy
  or any other tool config. Editing a tool's config to make a
  finding go away is a suppression too.
- Disabling or narrowing a pre-commit hook, or bypassing hooks
  with `SKIP=` / `git commit --no-verify`.

Tests:

- Deleting a test, a fixture, or a whole test module.
- Commenting out a test or a test module.
- Adding `skip`/`skipif`/`xfail` markers to an existing test, or
  calling `pytest.skip()`/`pytest.xfail()`/`pytest.importorskip()`
  to dodge a failure.
- Weakening assertions: removing them, dropping `match=` from
  `pytest.raises()`, catching a broader exception type, or
  changing an expected value to match buggy output.
- Adding `ignore` entries to `filterwarnings`.

Thresholds and CI:

- Lowering coverage targets, adding `continue-on-error`, dropping
  a job or a matrix entry.

Reporting:

- Running a subset (`-k`, `--deselect`, `--ignore`) is fine while
  iterating, but never report a run as green while failures are
  excluded from it.

## Presenting a case

When you believe silencing is warranted, stop and show the
operator, one case at a time:

1. The tool or test, the error code or failure message, and the
   `file:line`.
2. Why the cause can't reasonably be fixed right now.
3. The proposed scope -- line, file, or (rarely) directory.
4. The exact comment text that will accompany it.
5. When it can be removed -- the condition, the issue, or the
   upstream fix it waits for.

Then restate the trade-off in your own words and confirm the
operator understands and agrees with it. Approval of one case says
nothing about the next one.

## Preferred shape: line-scoped, explained, temporary

Scope a suppression to the single line that needs it, name the
specific codes, and explain why it exists and when it can go:

```python
value = call(42)  # noqa: WPS432  # mirrors libssh's SSH_OK; drop once exposed as a named constant
```

Blanket `# noqa` without codes is rejected by the
`python-check-blanket-noqa` pre-commit hook anyway. A `skip` or
`xfail` carries a `reason=` that links the tracking issue.

Most suppressions should be temporary. Treat each as tracked debt,
not a resolution.

## File-level suppressions are exceptional

Acceptable only with the operator's decision, for well-reasoned
cases -- e.g. a test module that intentionally passes wrong
argument types to check that runtime validation rejects them.
Where the tool supports code-specific file-level directives
(`# ruff: noqa: <CODE>` at the top of the file), use those.
Otherwise, use a `per-file-ignores` entry preceded by a comment
explaining each code, following the convention at the top of the
`per-file-ignores` block in `.flake8`.

## Directory-scoped suppressions

Avoid globs like `tests/**.py` in ignore lists. They hide every
future violation in that tree, not just the one in front of you.
Only add one with a well-reasoned decision from the operator,
recorded in a comment next to the entry.

## Legitimate test changes still get presented

When behavior changes on purpose and a test's expectations have
to change with it, say so explicitly -- don't slip it into a
larger diff. The accepted `xfail`-only PR in
[TESTING.md](TESTING.md) openly adds a *new* failing test ahead of
its fix. It is not a way to hide an existing test that broke.

## Existing suppressions

Many suppressions in the tree predate this rule (e.g. bare
`# noqa: DAR101` lines in `tests/conftest.py` without an
explanation). Don't rewrite them unasked. Point them out to the
operator if they're in the area you're touching. Removing a
suppression that's no longer needed is welcome, but show it too.

## Tool-config changes are standalone

Changing a linter, test runner, coverage, or CI config is its own
atomic change, never mixed into a functional one. See
[PR_HYGIENE.md](PR_HYGIENE.md).

## Claude Code guard hook

`.claude/hooks/guard_silenced_checks.py` makes Claude Code ask the
operator before edits that add suppression markers, reduce the
number of tests or assertions under `tests/`, touch tool configs,
or bypass/delete things from the shell. That prompt is a backstop,
not a rubber stamp: present the case as described above *before*
attempting the edit. Agents other than Claude Code follow the same
rule without the backstop.
