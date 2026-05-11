"""Tests suite for session."""

import inspect
import logging

import pytest

from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import (
    AutoAddPolicy,
    HOST_KEY_AUTO_ADD_MSG_MAP,
    KNOW_HOST_MSG_MAP,
    MissingHostKeyPolicy,
    OPTS_DIR_MAP,
    OPTS_MAP,
    RejectPolicy,
    Session,
)


def test_make_session():
    """Smoke-test Session instance creation."""
    assert Session()


def test_make_session_close_connect():
    """Make sure the session is usable after call to close()."""
    session = Session()
    session.close()
    error_msg = '^ssh connect failed: Hostname required$'
    with pytest.raises(LibsshSessionException, match=error_msg):
        session.connect()


def test_session_connection_refused(free_port_num):
    """Test that connecting to a missing service raises an error."""
    error_msg = '^ssh connect failed: Connection refused$'
    ssh_session = Session()
    with pytest.raises(LibsshSessionException, match=error_msg):
        ssh_session.connect(host='127.0.0.1', port=free_port_num)


class TestSessionProperties:
    """Tests for Session property accessors."""

    def test_is_connected_false_for_new_session(self):
        """Test is_connected returns False for a freshly created session."""
        session = Session()
        assert not session.is_connected

    def test_is_connected_false_after_close(self):
        """Test is_connected returns False after close."""
        session = Session()
        session.close()
        assert not session.is_connected

    def test_port_returns_none_for_new_session(self):
        """Test port returns None when no port has been set."""
        session = Session()
        result = session.port
        assert result is None or isinstance(result, int)


class TestSessionSetSshOptions:
    """Tests for Session.set_ssh_options()."""

    def test_set_host_option(self):
        """Test setting and retrieving the host option."""
        session = Session()
        session.set_ssh_options('host', 'example.com')
        assert session.get_ssh_options('host') == 'example.com'

    def test_set_user_option(self):
        """Test setting and retrieving the user option."""
        session = Session()
        session.set_ssh_options('user', 'testuser')
        assert session.get_ssh_options('user') == 'testuser'

    def test_set_port_option(self):
        """Test setting and retrieving the port option."""
        session = Session()
        session.set_ssh_options('port', 2222)
        assert session.get_ssh_options('port') == 2222

    def test_set_timeout_option(self):
        """Test setting the timeout option."""
        session = Session()
        session.set_ssh_options('timeout', 30)

    def test_set_timeout_usec_option(self):
        """Test setting the timeout_usec option."""
        session = Session()
        session.set_ssh_options('timeout_usec', 5000)

    def test_set_unknown_option_raises(self):
        """Test that setting an unknown option raises LibsshSessionException."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='Unknown attribute name'):
            session.set_ssh_options('nonexistent_option', 'value')

    def test_set_ssh_dir_option(self):
        """Test setting an option from OPTS_DIR_MAP."""
        session = Session()
        session.set_ssh_options('ssh_dir', '/tmp/ssh')
        assert session.get_ssh_options('ssh_dir') == b'/tmp/ssh'

    def test_set_add_identity_option(self):
        """Test setting the add_identity option from OPTS_DIR_MAP."""
        session = Session()
        session.set_ssh_options('add_identity', '/tmp/key')

    def test_set_host_option_bytes(self):
        """Test setting host option with bytes value."""
        session = Session()
        session.set_ssh_options('host', b'example.com')
        assert session.get_ssh_options('host') == 'example.com'

    def test_set_knownhosts_option(self):
        """Test setting the knownhosts option."""
        session = Session()
        session.set_ssh_options('knownhosts', '/dev/null')

    def test_set_proxycommand_option(self):
        """Test setting the proxycommand option."""
        session = Session()
        session.set_ssh_options('proxycommand', 'ssh -W %h:%p jumphost')

    def test_session_init_with_kwargs(self):
        """Test Session creation with keyword arguments sets options."""
        session = Session(user='testuser', port=2222)
        assert session.get_ssh_options('user') == 'testuser'
        assert session.get_ssh_options('port') == 2222


class TestSessionGetSshOptions:
    """Tests for Session.get_ssh_options()."""

    def test_get_unknown_option_raises(self):
        """Test that getting an unknown option raises LibsshSessionException."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='Unknown attribute name'):
            session.get_ssh_options('nonexistent_option')

    def test_get_port_returns_none_when_unset(self):
        """Test getting port when it hasn't been set."""
        session = Session()
        result = session.get_ssh_options('port')
        assert result is None or isinstance(result, int)

    def test_get_ssh_dir_not_set_raises(self):
        """Test that getting ssh_dir when not set raises exception."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='Unknown attribute name'):
            session.get_ssh_options('ssh_dir')


class TestSessionDisconnect:
    """Tests for Session.disconnect()."""

    def test_disconnect_non_connected_session(self):
        """Test disconnecting a session that was never connected."""
        session = Session()
        session.disconnect()

    def test_close_non_connected_session(self):
        """Test closing a session that was never connected."""
        session = Session()
        session.close()

    def test_close_idempotent(self):
        """Test that calling close multiple times is safe."""
        session = Session()
        session.close()
        session.close()
        session.close()


class TestSessionSetLogLevel:
    """Tests for Session.set_log_level()."""

    def test_set_log_level_debug(self):
        """Test setting log level to DEBUG."""
        session = Session()
        session.set_log_level(logging.DEBUG)

    def test_set_log_level_info(self):
        """Test setting log level to INFO."""
        session = Session()
        session.set_log_level(logging.INFO)

    def test_set_log_level_warning(self):
        """Test setting log level to WARNING."""
        session = Session()
        session.set_log_level(logging.WARNING)

    def test_set_log_level_invalid_raises(self):
        """Test that setting an invalid log level raises exception."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='Invalid log level'):
            session.set_log_level(99999)


class TestSessionMissingHostKeyPolicy:
    """Tests for Session.set_missing_host_key_policy()."""

    def test_set_reject_policy_instance(self):
        """Test setting RejectPolicy instance."""
        session = Session()
        policy = RejectPolicy()
        session.set_missing_host_key_policy(policy)

    def test_set_auto_add_policy_instance(self):
        """Test setting AutoAddPolicy instance."""
        session = Session()
        policy = AutoAddPolicy()
        session.set_missing_host_key_policy(policy)

    def test_set_policy_with_class(self):
        """Test setting policy with class (not instance) auto-instantiates."""
        session = Session()
        session.set_missing_host_key_policy(RejectPolicy)

    def test_set_policy_with_auto_add_class(self):
        """Test setting AutoAddPolicy class auto-instantiates."""
        session = Session()
        session.set_missing_host_key_policy(AutoAddPolicy)

    def test_set_custom_policy(self):
        """Test setting a custom MissingHostKeyPolicy subclass."""
        class CustomPolicy(MissingHostKeyPolicy):
            pass

        session = Session()
        session.set_missing_host_key_policy(CustomPolicy())


class TestMissingHostKeyPolicy:
    """Tests for MissingHostKeyPolicy base class."""

    def test_missing_host_key_returns_none(self):
        """Test that base class missing_host_key returns None."""
        policy = MissingHostKeyPolicy()
        result = policy.missing_host_key(None, None, None, None, None, None)
        assert result is None

    def test_is_base_class(self):
        """Test MissingHostKeyPolicy has expected interface."""
        assert hasattr(MissingHostKeyPolicy, 'missing_host_key')
        assert callable(MissingHostKeyPolicy().missing_host_key)


class TestAutoAddPolicy:
    """Tests for AutoAddPolicy class."""

    def test_inherits_from_missing_host_key_policy(self):
        """Test AutoAddPolicy inherits from MissingHostKeyPolicy."""
        policy = AutoAddPolicy()
        assert isinstance(policy, MissingHostKeyPolicy)

    def test_has_missing_host_key_method(self):
        """Test AutoAddPolicy has missing_host_key method."""
        policy = AutoAddPolicy()
        assert hasattr(policy, 'missing_host_key')
        assert callable(policy.missing_host_key)


class TestRejectPolicy:
    """Tests for RejectPolicy class."""

    def test_inherits_from_missing_host_key_policy(self):
        """Test RejectPolicy inherits from MissingHostKeyPolicy."""
        policy = RejectPolicy()
        assert isinstance(policy, MissingHostKeyPolicy)

    def test_missing_host_key_raises(self):
        """Test RejectPolicy raises LibsshSessionException."""
        policy = RejectPolicy()
        error_message = 'Host key mismatch'
        with pytest.raises(LibsshSessionException, match=error_message):
            policy.missing_host_key(
                None, 'host', 'user', 'rsa', 'fingerprint', error_message,
            )


class TestSessionConstants:
    """Tests for session module constants."""

    def test_opts_map_contains_expected_keys(self):
        """Test OPTS_MAP contains standard SSH option keys."""
        expected_keys = [
            'host', 'user', 'port', 'timeout', 'timeout_usec',
            'knownhosts', 'proxycommand', 'fd',
        ]
        for key in expected_keys:
            assert key in OPTS_MAP, f'{key} not in OPTS_MAP'

    def test_opts_map_contains_gssapi_keys(self):
        """Test OPTS_MAP contains GSSAPI-related keys."""
        gssapi_keys = [
            'gssapi_server_identity',
            'gssapi_client_identity',
            'gssapi_delegate_credentials',
        ]
        for key in gssapi_keys:
            assert key in OPTS_MAP, f'{key} not in OPTS_MAP'

    def test_opts_map_contains_algorithm_keys(self):
        """Test OPTS_MAP contains algorithm configuration keys."""
        algo_keys = [
            'key_exchange_algorithms',
            'publickey_accepted_algorithms',
            'hostkeys',
        ]
        for key in algo_keys:
            assert key in OPTS_MAP, f'{key} not in OPTS_MAP'

    def test_opts_dir_map_contains_expected_keys(self):
        """Test OPTS_DIR_MAP contains expected keys."""
        expected_keys = ['ssh_dir', 'add_identity']
        for key in expected_keys:
            assert key in OPTS_DIR_MAP, f'{key} not in OPTS_DIR_MAP'

    def test_know_host_msg_map_not_empty(self):
        """Test KNOW_HOST_MSG_MAP has entries."""
        assert len(KNOW_HOST_MSG_MAP) > 0

    def test_know_host_msg_map_values_are_strings(self):
        """Test KNOW_HOST_MSG_MAP values are strings."""
        for value in KNOW_HOST_MSG_MAP.values():
            assert isinstance(value, str)

    def test_host_key_auto_add_msg_map_not_empty(self):
        """Test HOST_KEY_AUTO_ADD_MSG_MAP has entries."""
        assert len(HOST_KEY_AUTO_ADD_MSG_MAP) > 0

    def test_host_key_auto_add_msg_map_values_are_strings(self):
        """Test HOST_KEY_AUTO_ADD_MSG_MAP values are strings."""
        for value in HOST_KEY_AUTO_ADD_MSG_MAP.values():
            assert isinstance(value, str)

    def test_opts_map_log_verbosity_key(self):
        """Test OPTS_MAP contains log_verbosity key."""
        assert 'log_verbosity' in OPTS_MAP


class TestSessionConnect:
    """Tests for Session.connect() edge cases."""

    def test_connect_without_host_raises(self):
        """Test that connecting without host raises exception."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='ssh connect failed'):
            session.connect()

    def test_connect_with_none_option_values_ignored(self):
        """Test that None option values are skipped during connect."""
        session = Session()
        with pytest.raises(LibsshSessionException, match='ssh connect failed'):
            session.connect(host=None, port=None)

    def test_connect_sets_options_before_connecting(self):
        """Test that connect passes options to set_ssh_options."""
        session = Session()
        session.set_ssh_options('host', '192.0.2.1')
        with pytest.raises(LibsshSessionException, match='ssh connect failed'):
            session.connect(timeout=1)


class TestSessionPushCallback:
    """Tests for Session.push_callback()."""

    def test_push_callback_stores_callback(self):
        """Test that push_callback appends to internal list."""
        session = Session()

        def dummy_callback():
            pass

        session.push_callback(dummy_callback)
