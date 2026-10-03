# PR & Commit Hygiene

Grounded in the project's own review history, plus explicit
maintainer conventions carried over from other projects — not
guesses.

## Point contributors to the official guidelines

Route contributors to
<https://ansible-pylibssh.rtfd.io/en/latest/contributing/guidelines>
for the canonical contribution process, rather than improvising or
restating it secondhand.

## Keep PRs and commits atomic and scoped

One conceptual change per PR, one conceptual change per commit.
"I'm definitely not going to accept a bunch of unrelated changes
smashed together" (PR #809); a PR mixing formatting, docstring
rewording, and a behavior change got split into three (PR #862)
before being accepted. Rebase onto the target branch for real
instead of adding merge commits ("foxtrot merges") to a feature
branch.

### Tool-config changes are standalone

Changes to tool configuration -- `.flake8`, `.ruff.toml`,
`.pre-commit-config.yaml`, `pytest.ini`, `tox.ini`, `.codecov.yml`,
CI workflows, and the like -- go in their own commit, with their
own rationale, never mixed into a functional change. Ask the
operator whether one also needs its own PR. This is the same
reasoning behind keeping type-annotation retrofits a deliberate,
standalone effort (see below). When the config change relaxes a
check, it's also a suppression -- see
[DONT_SHOOT_THE_MESSENGER.md](DONT_SHOOT_THE_MESSENGER.md).

## Don't dump AI-generated bloat

"LLMs are good at generating way too much stuff and it even works
under some circumstances but we're still responsible for keeping
the patches maintainable, having Git tree tell a story and contain
sufficient context. Be accountable." (PR #790) -- trim anything not
directly related to the stated change before proposing it.
You don't decide when the trimming is done. The operator does
(see [HOUSE_RULES.md](HOUSE_RULES.md)).

The same restraint applies to the PR description, not just the
diff -- see
[DONT_GHOST_THE_REVIEWER.md](DONT_GHOST_THE_REVIEWER.md) for why
internal self-check noise (e.g. a "Verification" section
restating that conventional tooling was run) doesn't belong
there either.

## Every change needs a changelog fragment

One fragment per PR, filed under `docs/changelog-fragments/` as
`<issue/PR#>.<type>.rst`.

A changelog fragment is not a restated commit message -- it covers
everything since the previous release, for end-users, not
developers. See `docs/changelog-fragments/README.rst` for the full
rationale, including why changelog entries are a permanent
historical record (never retroactively removed, even if the
underlying code is later reverted) unlike commit history, which
can be reworded, rebased, or squashed.

Recurring, specific review feedback:

- One change per fragment, not several changes "smashed" into one
  (#756, #862).
- Wording is past-tense and end-user-facing, not
  imperative/developer-facing.
- Reference related issues/PRs using `sphinx-issues` roles
  (`:pr:`, `:user:`, `:file:`) instead of raw links or backticks
  (#620, #786, #790, #809).
- Fully agentic work gets no `-- by :user:` byline -- it's not
  human work, and crediting a probabilistic machine in a loop is
  silly. Disclose AI involvement in the PR instead.

## Credit the people whose work you use

When incorporating a patch someone suggested, credit them with a
`Co-Authored-By: Name <email>` trailer, per
<https://hynek.me/til/easier-crediting-contributors-github/>
(GitHub's `ID+username@users.noreply.github.com` works). If it
came via `git format-patch`/`git am`, preserve the original Author
field instead. Add one trailer per contributor when there are
several. Who to credit, and how, is always the operator's call --
ask every time, not only when unsure.

- Prefer native authorship: the operator clicking "Commit
  suggestion" in the GitHub UI, or the author pushing it
  themselves, beats re-applying their change locally.
- Look the trailer up with `gh api users/<login>` (`.id`, and
  `.name` falling back to `.login`) -- don't guess. Keep the
  `+login` part; the bare ID doesn't work. Show the exact trailer
  to the operator before committing.
- Rewording, restructuring, or re-implementing a suggestion so it
  "isn't really theirs" anymore still requires the credit.
- Never drop existing `Co-Authored-By` trailers, or replace the
  original author, when rebasing, squashing, or rewording.

## Names and docstrings carry the meaning, not comments

"Comments repeating what the code does are pointless. Proper
identifier names should be used instead" (PR #621). Docstrings
describe what a function does; motivation/rationale, if needed,
belongs in a comment or the PR description, not the docstring
(PR #658).

## Type annotations on new code

New code -- including new tests -- needs type annotations:
parameter types and return types, using `import typing as _t`
for standard-library constructs (e.g. `_t.Optional[...]`). This
isn't retrofitted into existing/legacy code as a side effect of
an unrelated change -- that's a deliberate, standalone future
effort, not something to bundle into whatever else a PR is
doing.

This is a real, acknowledged gap today: `.ruff.toml` disables
`ANN001`/`ANN201`/`ANN202`/`ANN401` with an explicit `# FIXME:
These flake8-annotations errors need fixing and removal`
comment, and none of the current test functions in `tests/` are
annotated. Don't read the absence of annotations in existing
code as license to skip them in new code -- it's tracked debt,
not the house style.

## Common micro-conventions flagged in review

- f-strings over `.format()`/`%` formatting.
- `contextlib.suppress()` over bare `try`/`except: pass`.
- No monkey-patching stdlib.
- Public vs. private intent must be explicit -- prefix with `_` if
  not part of the public API.
