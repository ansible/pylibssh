# House Rules

> [!tip]
>
> This is how we do things here, get used to it.

## Operating mode

> [!important]
>
> Bidirectional quizzing is mandatory. Before executing any plan,
> quiz the operator on their exact understanding of every step and
> every decision it contains -- do not skip this self-check, and
> do not assume implicit consent from earlier turns; re-check,
> re-confirm.

> [!important]
>
> Never self-approve prose meant for humans. Show every draft
> (change notes, commits, PR text, replies) and ask the operator
> whether it is concise enough. The operator decides.

Concretely:

- Read the relevant files in full before proposing edits -- never
  guess what they currently contain.
- Show diffs for non-trivial changes and pause for explicit
  approval.
- Quiz the operator: restate what you understand the task to be,
  call out assumptions, ask one or two clarifying questions when
  the prompt is ambiguous.
- Do not invoke `git commit` / `git push` / `git tag` / any other
  history-mutating command without an explicit "go ahead" in the
  current turn.
- Treat external network calls, package installs, and process
  spawns as actions that need authorization too.
- When in doubt, ask. The operator prefers a clarifying question
  over an unwound mistake.

## Naming the ducks

See [NAMING_THE_DUCKS.md](NAMING_THE_DUCKS.md) for the project's
canonical names (distribution, import, repository) and which one
to use where.

## Coding style and architecture

See [HOUSE_STYLE.md](HOUSE_STYLE.md) for coding style and
architectural/structural conventions, including the rule against
introducing new `@`-syntax in memory files.

## Testing

See [TESTING.md](TESTING.md) for how tests are written and
structured in this project.

## PR and commit hygiene

See [PR_HYGIENE.md](PR_HYGIENE.md) for scope, changelog-fragment,
and naming conventions maintainers consistently enforce in review.

## Don't ghost the reviewer

See [DONT_GHOST_THE_REVIEWER.md](DONT_GHOST_THE_REVIEWER.md) for
review-conversation etiquette when participating in PR review on
the maintainer's behalf -- responding to feedback, resolving
threads, and not disrupting review flow with careless pushes.

## Tooling

See [CONTRIB_WORKFLOW_INFRA_TOOLING.md](CONTRIB_WORKFLOW_INFRA_TOOLING.md)
for how to run tests, linters, and other project automation --
always through `tox`, never by invoking the wrapped tools directly.
