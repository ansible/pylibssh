"""Tests for the test suite service helpers."""

import pathlib
import time

import pytest
from _service_utils import wait_for_svc_ready_state


_TIMEOUT_SECONDS = 0.1
_RECONNECT_ATTEMPT_DELAY_SECONDS = 0.001
_SSH_CONNECT_TIMEOUT_SECONDS = 1  # `-oConnectTimeout` in the helper
_PROCESS_SPAWN_SLACK_SECONDS = 1


def test_wait_for_svc_ready_state_times_out(
    free_port_num: int,
    tmp_path: pathlib.Path,
) -> None:
    """Check that waiting for an absent service gives up on deadline."""
    started_at = time.monotonic()
    error_msg = '^Timed out waiting for a successful connection$'
    with pytest.raises(TimeoutError, match=error_msg):
        wait_for_svc_ready_state(
            '127.0.0.1',
            free_port_num,
            tmp_path / 'missing-client-key',
            timeout_seconds=_TIMEOUT_SECONDS,
            reconnect_attempt_delay=_RECONNECT_ATTEMPT_DELAY_SECONDS,
        )
    elapsed_seconds = time.monotonic() - started_at
    assert elapsed_seconds >= _TIMEOUT_SECONDS
    assert elapsed_seconds < (
        _TIMEOUT_SECONDS
        + _SSH_CONNECT_TIMEOUT_SECONDS
        + _PROCESS_SPAWN_SLACK_SECONDS
    )
