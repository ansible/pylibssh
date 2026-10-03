#! /usr/bin/env python3
"""Make Claude Code ask the operator before an agent silences a check.

This is a ``PreToolUse`` hook. It never blocks anything on its own: when
an edit or a shell command looks like it suppresses a linter finding,
disables or weakens a test, or changes tool configuration, it asks
Claude Code to prompt the operator for a decision.

See ``.agents-ctx/DONT_SHOOT_THE_MESSENGER.md`` for the policy.
"""

import json
import os
import pathlib
import re
import sys
import typing as _t  # noqa: WPS111  # house convention; drop once the lint config allows `_t`


POLICY_DOC = '.agents-ctx/DONT_SHOOT_THE_MESSENGER.md'

MarkerTable = _t.Iterable[tuple[str, re.Pattern[str]]]

SUPPRESSION_MARKERS = (
    ('noqa', re.compile(r'#\s*noqa\b', re.IGNORECASE)),
    ('ruff: noqa', re.compile(r'#\s*ruff\s*:\s*noqa\b')),
    ('flake8: noqa', re.compile(r'#\s*flake8\s*:\s*noqa\b')),
    ('type: ignore', re.compile(r'#\s*type\s*:\s*ignore\b')),
    ('mypy: ignore', re.compile(r'#\s*mypy\s*:\s*ignore')),
    ('pylint: disable', re.compile(r'#\s*pylint\s*:\s*disable')),
    ('pragma: no cover', re.compile(r'#\s*pragma\s*:\s*no\s*cover')),
    ('skip/skipif marker', re.compile(r'\bpytest\.mark\.skip')),
    ('xfail marker', re.compile(r'\bpytest\.mark\.xfail\b')),
    (
        'imperative skip/xfail',
        re.compile(r'\bpytest\.(?:skip|xfail|importorskip)\s*\('),
    ),
    ('continue-on-error', re.compile(r'\bcontinue-on-error\b')),
)

TEST_STRENGTH_MARKERS = (
    (
        'test functions',
        re.compile(r'^\s*(?:async\s+)?def\s+test_', re.MULTILINE),
    ),
    ('assertions', re.compile(r'^\s*assert\b', re.MULTILINE)),
    ('pytest.raises() checks', re.compile(r'\bpytest\.raises\s*\(')),
)

TOOL_CONFIG_NAMES = frozenset(
    (
        '.codecov.yml',
        '.coveragerc',
        '.flake8',
        '.pre-commit-config.yaml',
        '.pylintrc',
        '.ruff.toml',
        '.yamllint',
        'mypy.ini',
        'pyproject.toml',
        'pytest.ini',
        'setup.cfg',
        'tox.ini',
    ),
)

TOOL_CONFIG_DIRS = ('.claude/', '.github/workflows/')

TESTS_DIR = 'tests/'

TOOL_CONFIG_NAMES_ALTERNATION = '|'.join(
    re.escape(config_name) for config_name in sorted(TOOL_CONFIG_NAMES)
)

SHELL_BYPASS = re.compile(r'--no-verify\b|(?:^|[\s;&|])SKIP=')

SHELL_RISKY_TARGET = re.compile(
    r'\b(?:rm|mv|truncate|tee|git\s+rm|git\s+mv|sed\s+-i|perl\s+-\w*i)\b'
    r'[^|;&]*'
    rf'(?:\b{re.escape(TESTS_DIR)}|{TOOL_CONFIG_NAMES_ALTERNATION}'
    r'|\.github/workflows/|\.claude/)',
)


def _relative_path(file_path: str, project_dir: pathlib.Path) -> str:
    """Return ``file_path`` relative to the project, POSIX-style."""
    absolute_path = pathlib.Path(file_path)
    if not absolute_path.is_absolute():
        absolute_path = project_dir / absolute_path
    try:
        return absolute_path.resolve().relative_to(project_dir).as_posix()
    except ValueError:
        return absolute_path.as_posix()


def _edit_texts(
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


def _more_frequent(
    markers: MarkerTable,
    baseline: str,
    candidate: str,
) -> list[str]:
    """List the markers that occur more often in candidate than baseline."""
    return [
        marker_name
        for marker_name, marker_regex in markers
        if len(marker_regex.findall(candidate))
        > len(marker_regex.findall(baseline))
    ]


def _is_tool_config(relative_path: str) -> bool:
    """Check whether the path is a linter, test, CI or agent config."""
    return pathlib.PurePosixPath(relative_path).name in TOOL_CONFIG_NAMES or (
        relative_path.startswith(TOOL_CONFIG_DIRS)
    )


def _edit_concerns(
    hook_input: _t.Mapping[str, _t.Any],
    project_dir: pathlib.Path,
) -> list[str]:
    """Describe why an edit tool call needs the operator's decision."""
    tool_input = hook_input.get('tool_input', {})
    relative_path = _relative_path(
        tool_input.get('file_path') or tool_input.get('notebook_path', ''),
        project_dir,
    )
    old_text, new_text = _edit_texts(
        hook_input.get('tool_name', ''),
        tool_input,
        project_dir,
    )

    concerns = [
        f'adds a suppression ({marker_name}) in {relative_path}'
        for marker_name in _more_frequent(
            SUPPRESSION_MARKERS,
            baseline=old_text,
            candidate=new_text,
        )
    ]
    if relative_path.startswith(TESTS_DIR):
        concerns.extend(
            f'reduces the number of {marker_name} in {relative_path}'
            for marker_name in _more_frequent(
                TEST_STRENGTH_MARKERS,
                baseline=new_text,
                candidate=old_text,
            )
        )
    if _is_tool_config(relative_path):
        concerns.append(
            f'changes tool configuration in {relative_path} '
            '(keep it in a standalone commit)',
        )
    return concerns


def _shell_concerns(hook_input: _t.Mapping[str, _t.Any]) -> list[str]:
    """Describe why a shell command needs the operator's decision."""
    command = hook_input.get('tool_input', {}).get('command', '')
    concerns = [
        f'the command mentions a suppression ({marker_name})'
        for marker_name, marker_regex in SUPPRESSION_MARKERS
        if marker_regex.search(command)
    ]
    if SHELL_BYPASS.search(command):
        concerns.append('the command bypasses pre-commit hooks')
    if SHELL_RISKY_TARGET.search(command):
        concerns.append(
            'the command deletes, moves or rewrites tests or tool config',
        )
    return concerns


def main() -> int:
    """Read the hook input and ask the operator when needed."""
    hook_input = json.load(sys.stdin)
    project_dir = pathlib.Path(
        os.environ.get('CLAUDE_PROJECT_DIR') or hook_input.get('cwd', '.'),
    ).resolve()

    if hook_input.get('tool_name') == 'Bash':
        concerns = _shell_concerns(hook_input)
    else:
        concerns = _edit_concerns(hook_input, project_dir)

    if concerns:
        concerns_summary = '; '.join(concerns)
        decision_reason = (
            'Silencing checks is a decision for the operator '
            f'(see {POLICY_DOC}): {concerns_summary}. '
            'The agent must have presented this case to you first.'
        )
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
