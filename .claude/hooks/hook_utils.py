"""Helpers shared by the Claude Code ``PreToolUse`` hooks in this directory."""

import contextlib
import json
import pathlib
import sys
import typing as _t  # noqa: WPS111  # house convention; drop once the lint config allows `_t`


def relative_path(file_path: str, project_dir: pathlib.Path) -> str:
    """Return ``file_path`` relative to its checkout, POSIX-style.

    Files outside the project directory, e.g. in another worktree of
    the same repository, are resolved against their own worktree.
    """
    absolute_path = pathlib.Path(file_path)
    if not absolute_path.is_absolute():
        absolute_path = project_dir / absolute_path
    absolute_path = absolute_path.resolve()
    worktree_dir = next(
        (
            candidate_dir
            for candidate_dir in absolute_path.parents
            if (candidate_dir / '.git').exists()
        ),
        project_dir,
    )
    for checkout_dir in (project_dir, worktree_dir):
        with contextlib.suppress(ValueError):
            return absolute_path.relative_to(checkout_dir).as_posix()
    return absolute_path.as_posix()


def edit_texts(
    tool_name: str,
    tool_input: _t.Mapping[str, _t.Any],
    project_dir: pathlib.Path,
) -> tuple[str, str]:
    """Collect the text an edit tool removes and the text it adds."""
    if tool_name == 'Write':
        target_path = pathlib.Path(tool_input.get('file_path', ''))
        if not target_path.is_absolute():
            target_path = project_dir / target_path
        try:
            old_text = target_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            old_text = ''
        return old_text, tool_input.get('content', '')

    if tool_name == 'NotebookEdit':
        return '', tool_input.get('new_source', '')

    edits = tool_input.get('edits') or (tool_input,)
    return (
        '\n'.join(edit.get('old_string', '') for edit in edits),
        '\n'.join(edit.get('new_string', '') for edit in edits),
    )


def ask_operator(decision_reason: str) -> None:
    """Tell Claude Code to prompt the operator, giving the reason."""
    json.dump(
        {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'ask',
                'permissionDecisionReason': decision_reason,
            },
        },
        sys.stdout,
    )
