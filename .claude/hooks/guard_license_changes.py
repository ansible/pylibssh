#! /usr/bin/env python3
"""Make Claude Code ask the operator before an agent touches licensing.

This is a ``PreToolUse`` hook. It never blocks anything on its own: when
an edit or a shell command looks like it changes a license file or drops
license notices, it asks Claude Code to prompt the operator for a
decision.

See ``.agents-ctx/LICENSING.md`` for the policy.
"""

import json
import os
import pathlib
import re
import sys
import typing as _t  # noqa: WPS111  # house convention; drop once the lint config allows `_t`

import hook_utils


POLICY_DOC = '.agents-ctx/LICENSING.md'

LICENSE_FILE_NAME = re.compile(
    r'^(?:LICEN[CS]E|COPYING|NOTICE)(?:[.-].*)?$',
    re.IGNORECASE,
)

LICENSE_NOTICE = re.compile(
    r'\bLicen[cs]e\b|SPDX-License-Identifier',
    re.IGNORECASE,
)

LICENSE_METADATA = re.compile(
    r'^\s*license(?:[-_]files?)?\s*[=:].*$',
    re.IGNORECASE | re.MULTILINE,
)

SHELL_LICENSE_TARGET = re.compile(
    r'\b(?:rm|mv|truncate|tee|git\s+rm|git\s+mv|sed\s+-i|perl\s+-\w*i)\b'
    r'[^|;&]*'
    r'\b(?:LICEN[CS]E|COPYING|NOTICE)',
    re.IGNORECASE,
)


def _edit_concerns(
    hook_input: _t.Mapping[str, _t.Any],
    project_dir: pathlib.Path,
) -> list[str]:
    """Describe why an edit tool call needs the operator's decision."""
    tool_input = hook_input.get('tool_input', {})
    relative_path = hook_utils.relative_path(
        tool_input.get('file_path') or tool_input.get('notebook_path', ''),
        project_dir,
    )
    old_text, new_text = hook_utils.edit_texts(
        hook_input.get('tool_name', ''),
        tool_input,
        project_dir,
    )

    concerns = []
    if LICENSE_FILE_NAME.match(pathlib.PurePosixPath(relative_path).name):
        concerns.append(f'changes the license file {relative_path}')
    if len(LICENSE_NOTICE.findall(new_text)) < len(
        LICENSE_NOTICE.findall(old_text),
    ):
        concerns.append(f'removes license notices in {relative_path}')
    if set(LICENSE_METADATA.findall(old_text)) != set(
        LICENSE_METADATA.findall(new_text),
    ):
        concerns.append(f'changes license metadata in {relative_path}')
    return concerns


def _shell_concerns(hook_input: _t.Mapping[str, _t.Any]) -> list[str]:
    """Describe why a shell command needs the operator's decision."""
    command = hook_input.get('tool_input', {}).get('command', '')
    if SHELL_LICENSE_TARGET.search(command):
        return ['the command deletes, moves or rewrites a license file']
    return []


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
            "License terms are the maintainer's decision "
            f'(see {POLICY_DOC}): {concerns_summary}. '
            'The agent must have presented this change to you first.'
        )
        hook_utils.ask_operator(decision_reason)
    return 0


if __name__ == '__main__':
    sys.exit(main())
