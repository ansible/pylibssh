# Testing

Grounded in the project's own review history and merged commits,
plus explicit maintainer conventions carried over from other
projects — not guesses.

## Tests are proof, not decoration

New or changed behavior needs a test demonstrating it, covering the
cases actually touched (including edge cases like `None`). "I don't
think there's a proof that this works as intended without tests" is
a near-verbatim recurring review comment (e.g. PR #756, #786, #790,
#479, #669, #809). Missing test coverage is the single most common
reason PRs stall or get closed unmerged in this project.

Justify new tests by what they actually verify, not by the
coverage number alone. Coverage still matters a lot here --
`.codecov.yml` already targets 100% for `src/`/`tests/`, and 100%
coverage is a genuinely useful self-check (e.g. it can catch tests
that silently start getting skipped in CI). It isn't wired up as a
required CI check yet, only because of unresolved infra problems
measuring Cython coverage -- not because it's considered optional.
The point is: don't game the number -- a test that exercises a
line without meaningfully checking behavior doesn't count, passing
or not. The same reasoning-over-metrics standard applies to every
change, not just tests: infra, packaging, and runtime code all
need well-reasoned, architecturally sound justification, not just
a passing check.

Deleting, commenting out, skipping, xfailing, or weakening a test
is never the agent's call -- see
[DONT_SHOOT_THE_MESSENGER.md](DONT_SHOOT_THE_MESSENGER.md).

## No test classes

Every test in `tests/` is a plain `def test_*` function. There are
zero `class` definitions anywhere in the test suite, across the
full project history. Don't introduce `unittest.TestCase`
subclasses or bare grouping classes.

## Prefer parametrize/fixtures over duplicated test logic

When two tests differ only in their input data, that's a
parametrized fixture, not two near-identical functions, e.g.
`@pytest.fixture(params=(32, SFTP_MAX_CHUNK + 1), ids=(...))`.
Precedent: PR #638 collapses `other_payload`/`large_payload` into
one parametrized fixture; a project commit merges near-duplicate
`NOTSET`/`TRACE` tests into a single `@pytest.mark.parametrize`
case.

Loop-based checks inside a single test are generally a sign the
test should be parametrized instead. The one accepted exception is
`pytest-subtests` (the `subtests` fixture), for structured,
individually reported sub-assertions within one test.

## Real e2e over mocking

`tests/` contains zero uses of `mock`, `Mock`, or `monkeypatch`.
Every test -- unit and integration alike -- exercises a real
`sshd` process spun up per-test via the `sshd_addr` fixture in
`tests/conftest.py`. Don't introduce mocking as a substitute for
exercising real libssh/sshd behavior.

## Design for testability

Prefer decoupling techniques -- dependency injection in particular
-- that let code be tested in isolation, over reaching for
monkeypatching. Monkeypatching (via `unittest.mock` or the
`monkeypatch` fixture) is only acceptable at real system
boundaries: the system clock/timezone, environment variables, or
swapping in a stub server. It's not a substitute for designing
components to be testable on their own.

## Test layout

Under `tests/unit/`, test files are named `<module>_test.py`, not
`test_<module>.py`, loosely mirroring `src/pylibsshext/`:
`channel_test.py`, `session_test.py`, `sftp_test.py`, `scp_test.py`,
`version_test.py`. The correspondence isn't strict 1:1 (e.g.
`errors` is covered via `pytest.raises` inside other files, not its
own file) -- match the existing file when extending it, and only
add a new `<module>_test.py` for a genuinely new module. This
module-mirroring convention applies to `tests/unit/` specifically;
other test categories (e.g. `tests/integration/`) are organized by
scenario/feature instead, not by source module.

## Tests usually land in the same commit as the behavior they cover

When a change adds or alters behavior, the test change normally
lands in the *same* atomic commit, not a follow-up -- there's no
evidence of strict test-first/TDD commit ordering as a project
ritual. That style of TDD is mainly useful for interactive
development and exploration, used in tandem with continuous
adjustment, not as a blanket rule here.

The one accepted exception: a PR that adds only a failing test,
marked `@pytest.mark.xfail`, can be merged on its own ahead of the
fix, to be resolved in a follow-up. Don't treat a merged `xfail` as
done, though -- it's a tracked gap, not a resolution. This
exception covers adding a *new* failing test; marking an existing
test `xfail` because it broke is silencing it.

## Assertions

Use `pytest.raises(..., match=...)` -- never a bare
`pytest.raises(SomeError)` -- so the assertion pins down which
failure is expected, not just its type.

## Filesystem fixtures

Use pytest's built-in `tmp_path` fixture; don't hand-roll
temp-directory setup/teardown.

## Test payload data: prefer random bytes, once debugging is done

Printable/readable payload data (e.g. hand-crafted ASCII strings)
helped root-cause bugs when file-transfer implementations used to
corrupt data -- readability mattered more than realism while
chasing corruption bugs. Once an implementation is no longer
prone to that class of bug, prefer `random.randbytes()`-style
payloads instead: constructing large printable-string payloads is
inefficient, and random bytes exercise the code more realistically
at scale. This is a tradeoff that shifts with implementation
maturity, not a blanket "always use random data" rule (PR #872).

## Type annotations on new tests

New test functions and fixtures need type annotations too --
parameters and return types -- same as any other new code. See
[PR_HYGIENE.md](PR_HYGIENE.md) for the full rule, including why
this doesn't apply retroactively to the existing (currently
unannotated) test suite.

## Every test and fixture has a one-line docstring

Describing what it checks or provides, not restating the code,
e.g. `"""Check that SFTP file transfer works."""`. Enforced by
`darglint` in CI.
