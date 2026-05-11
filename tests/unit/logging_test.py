"""Tests suite for logging module."""

import logging

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.logging import (
    ANSIBLE_PYLIBSSH_NOLOG,
    ANSIBLE_PYLIBSSH_TRACE,
    LOG_MAP,
    LOG_MAP_REV,
    _add_trace_log_level,
    _initialize_logging,
    _set_level,
    _set_log_callback,
)


class TestLoggingConstants:
    """Tests for logging module constants."""

    def test_ansible_pylibssh_nolog_value(self):
        """Test ANSIBLE_PYLIBSSH_NOLOG is set correctly."""
        assert ANSIBLE_PYLIBSSH_NOLOG == logging.FATAL * 2
        assert isinstance(ANSIBLE_PYLIBSSH_NOLOG, int)
        assert ANSIBLE_PYLIBSSH_NOLOG > logging.FATAL

    def test_ansible_pylibssh_trace_value(self):
        """Test ANSIBLE_PYLIBSSH_TRACE is set correctly."""
        assert ANSIBLE_PYLIBSSH_TRACE == int(logging.DEBUG / 2)
        assert isinstance(ANSIBLE_PYLIBSSH_TRACE, int)
        assert ANSIBLE_PYLIBSSH_TRACE < logging.DEBUG

    def test_constants_are_different(self):
        """Test that NOLOG and TRACE constants are different values."""
        assert ANSIBLE_PYLIBSSH_NOLOG != ANSIBLE_PYLIBSSH_TRACE


class TestLogMap:
    """Tests for LOG_MAP dictionary."""

    def test_log_map_contains_expected_keys(self):
        """Test LOG_MAP contains Python logging levels."""
        expected_keys = [
            ANSIBLE_PYLIBSSH_TRACE,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            ANSIBLE_PYLIBSSH_NOLOG,
            logging.NOTSET,
            logging.ERROR,
            logging.CRITICAL,
        ]
        for key in expected_keys:
            assert key in LOG_MAP

    def test_log_map_trace_mapping(self):
        """Test ANSIBLE_PYLIBSSH_TRACE is mapped."""
        assert ANSIBLE_PYLIBSSH_TRACE in LOG_MAP
        assert LOG_MAP[ANSIBLE_PYLIBSSH_TRACE] is not None

    def test_log_map_nolog_mapping(self):
        """Test ANSIBLE_PYLIBSSH_NOLOG is mapped."""
        assert ANSIBLE_PYLIBSSH_NOLOG in LOG_MAP
        assert LOG_MAP[ANSIBLE_PYLIBSSH_NOLOG] is not None

    def test_log_map_standard_levels(self):
        """Test standard Python logging levels are mapped."""
        standard_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
        ]
        for level in standard_levels:
            assert level in LOG_MAP

    def test_log_map_aliases(self):
        """Test logging level aliases are present."""
        assert logging.NOTSET in LOG_MAP
        assert logging.ERROR in LOG_MAP
        assert logging.CRITICAL in LOG_MAP

    def test_log_map_error_alias_points_to_warn(self):
        """Test ERROR alias maps to same value as WARNING."""
        assert LOG_MAP[logging.ERROR] == LOG_MAP[logging.WARNING]

    def test_log_map_critical_alias_points_to_warn(self):
        """Test CRITICAL alias maps to same value as WARNING."""
        assert LOG_MAP[logging.CRITICAL] == LOG_MAP[logging.WARNING]

    def test_log_map_notset_alias_points_to_trace(self):
        """Test NOTSET alias maps to same value as TRACE."""
        assert LOG_MAP[logging.NOTSET] == LOG_MAP[ANSIBLE_PYLIBSSH_TRACE]

    def test_log_map_values_are_integers(self):
        """Test all LOG_MAP values are integers."""
        for value in LOG_MAP.values():
            assert isinstance(value, int)


class TestLogMapRev:
    """Tests for LOG_MAP_REV reverse mapping dictionary."""

    def test_log_map_rev_exists(self):
        """Test LOG_MAP_REV is defined."""
        assert LOG_MAP_REV is not None
        assert isinstance(LOG_MAP_REV, dict)

    def test_log_map_rev_is_reverse_of_log_map(self):
        """Test LOG_MAP_REV contains reverse mappings."""
        for py_level, libssh_level in LOG_MAP.items():
            if libssh_level in LOG_MAP_REV:
                assert isinstance(LOG_MAP_REV[libssh_level], int)

    def test_log_map_rev_keys_are_from_log_map_values(self):
        """Test LOG_MAP_REV keys come from LOG_MAP values."""
        log_map_values = set(LOG_MAP.values())
        for key in LOG_MAP_REV.keys():
            assert key in log_map_values

    def test_log_map_rev_values_are_integers(self):
        """Test all LOG_MAP_REV values are integers."""
        for value in LOG_MAP_REV.values():
            assert isinstance(value, int)


class TestAddTraceLogLevel:
    """Tests for _add_trace_log_level function."""

    def test_add_trace_log_level_callable(self):
        """Test _add_trace_log_level is callable."""
        assert callable(_add_trace_log_level)

    def test_add_trace_log_level_registers_level(self):
        """Test _add_trace_log_level registers TRACE level name."""
        _add_trace_log_level()
        level_name = logging.getLevelName(ANSIBLE_PYLIBSSH_TRACE)
        assert level_name == 'TRACE'

    def test_add_trace_log_level_idempotent(self):
        """Test calling _add_trace_log_level multiple times is safe."""
        _add_trace_log_level()
        _add_trace_log_level()
        level_name = logging.getLevelName(ANSIBLE_PYLIBSSH_TRACE)
        assert level_name == 'TRACE'


class TestSetLevel:
    """Tests for _set_level function."""

    def test_set_level_callable(self):
        """Test _set_level is callable."""
        assert callable(_set_level)

    def test_set_level_raises_for_invalid_level(self):
        """Test _set_level raises LibsshSessionException for invalid level."""
        invalid_level = 99999
        error_msg = f'Invalid log level \\[{invalid_level:d}\\]'
        with pytest.raises(LibsshSessionException, match=error_msg):
            _set_level(invalid_level)

    def test_set_level_raises_for_none(self):
        """Test _set_level raises exception when level is None."""
        with pytest.raises(Exception):
            _set_level(None)

    def test_set_level_raises_for_string(self):
        """Test _set_level raises exception for string input."""
        with pytest.raises(Exception):
            _set_level('DEBUG')

    def test_set_level_accepts_valid_levels_from_log_map(self):
        """Test _set_level accepts all valid levels from LOG_MAP."""
        for valid_level in LOG_MAP.keys():
            try:
                _set_level(valid_level)
            except Exception as exc:
                pytest.fail(
                    f'_set_level raised {exc!r} for valid level {valid_level}',
                )


class TestSetLogCallback:
    """Tests for _set_log_callback function."""

    def test_set_log_callback_callable(self):
        """Test _set_log_callback is callable."""
        assert callable(_set_log_callback)

    def test_set_log_callback_executes(self):
        """Test _set_log_callback can be called without error."""
        _set_log_callback()

    def test_set_log_callback_idempotent(self):
        """Test calling _set_log_callback multiple times is safe."""
        _set_log_callback()
        _set_log_callback()


class TestInitializeLogging:
    """Tests for _initialize_logging function."""

    def test_initialize_logging_callable(self):
        """Test _initialize_logging is callable."""
        assert callable(_initialize_logging)

    def test_initialize_logging_registers_trace(self):
        """Test _initialize_logging registers the TRACE level."""
        _initialize_logging()
        level_name = logging.getLevelName(ANSIBLE_PYLIBSSH_TRACE)
        assert level_name == 'TRACE'

    def test_initialize_logging_idempotent(self):
        """Test calling _initialize_logging multiple times is safe."""
        _initialize_logging()
        _initialize_logging()
        level_name = logging.getLevelName(ANSIBLE_PYLIBSSH_TRACE)
        assert level_name == 'TRACE'


class TestSetLevelEdgeCases:
    """Tests for _set_level edge cases."""

    def test_set_level_raises_for_negative(self):
        """Test _set_level raises LibsshSessionException for negative level."""
        with pytest.raises(LibsshSessionException, match='Invalid log level'):
            _set_level(-1)

    def test_set_level_raises_for_zero(self):
        """Test _set_level works for zero (NOTSET is in LOG_MAP)."""
        _set_level(0)

    def test_set_level_raises_for_large_value(self):
        """Test _set_level raises for arbitrary large level not in LOG_MAP."""
        with pytest.raises(LibsshSessionException, match='Invalid log level'):
            _set_level(12345)

    def test_set_level_returns_none(self):
        """Test _set_level returns None for valid levels."""
        result = _set_level(logging.DEBUG)
        assert result is None


class TestLoggingModuleIntegration:
    """Integration tests for logging module components."""

    def test_constants_work_with_log_map(self):
        """Test custom constants can be used with LOG_MAP."""
        assert ANSIBLE_PYLIBSSH_TRACE in LOG_MAP
        assert ANSIBLE_PYLIBSSH_NOLOG in LOG_MAP

    def test_all_standard_python_levels_covered(self):
        """Test all commonly used Python logging levels are in LOG_MAP."""
        common_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]
        for level in common_levels:
            assert level in LOG_MAP, f'Level {level} not in LOG_MAP'

    def test_log_map_keys_can_be_used_with_set_level(self):
        """Test all LOG_MAP keys are accepted by _set_level."""
        for level in LOG_MAP.keys():
            try:
                _set_level(level)
            except LibsshSessionException:
                pytest.fail(f'_set_level rejected valid level {level}')

    def test_trace_level_ordering(self):
        """Test TRACE level is below DEBUG."""
        assert ANSIBLE_PYLIBSSH_TRACE < logging.DEBUG

    def test_nolog_level_ordering(self):
        """Test NOLOG level is above FATAL."""
        assert ANSIBLE_PYLIBSSH_NOLOG > logging.FATAL

    def test_log_map_covers_all_custom_levels(self):
        """Test LOG_MAP includes both custom levels."""
        custom_levels = [ANSIBLE_PYLIBSSH_TRACE, ANSIBLE_PYLIBSSH_NOLOG]
        for level in custom_levels:
            assert level in LOG_MAP

    def test_log_map_rev_covers_unique_libssh_levels(self):
        """Test LOG_MAP_REV maps back all unique libssh log levels."""
        unique_libssh_levels = set(LOG_MAP.values())
        for libssh_level in unique_libssh_levels:
            assert libssh_level in LOG_MAP_REV
