"""Tests suite for errors module."""

import pytest

from pylibsshext.errors import (
    LibsshChannelException,
    LibsshChannelReadFailure,
    LibsshException,
    LibsshSCPException,
    LibsshSessionException,
    LibsshSFTPException,
)


class TestLibsshException:
    """Tests for LibsshException base class."""

    def test_exception_with_message(self):
        """Test LibsshException instantiation with a message."""
        error_message = 'Test error message'
        exc = LibsshException(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message
        assert repr(exc) == error_message

    def test_exception_without_message(self):
        """Test LibsshException instantiation without a message."""
        exc = LibsshException()
        assert exc.message == ''
        assert str(exc) == ''
        assert repr(exc) == ''

    def test_exception_can_be_raised(self):
        """Test that LibsshException can be raised and caught."""
        error_message = 'Something went wrong'
        with pytest.raises(LibsshException, match=error_message):
            raise LibsshException(error_message)

    def test_exception_inherits_from_exception(self):
        """Test that LibsshException is a proper Exception."""
        exc = LibsshException('test')
        assert isinstance(exc, Exception)

    def test_exception_message_attribute(self):
        """Test that message attribute is accessible."""
        error_message = 'Custom error'
        exc = LibsshException(error_message)
        assert hasattr(exc, 'message')
        assert exc.message == error_message


class TestLibsshSessionException:
    """Tests for LibsshSessionException."""

    def test_session_exception_inherits_from_libssh_exception(self):
        """Test LibsshSessionException inherits from LibsshException."""
        exc = LibsshSessionException('session error')
        assert isinstance(exc, LibsshException)
        assert isinstance(exc, Exception)

    def test_session_exception_with_message(self):
        """Test LibsshSessionException instantiation with message."""
        error_message = 'Session connection failed'
        exc = LibsshSessionException(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message

    def test_session_exception_can_be_raised(self):
        """Test that LibsshSessionException can be raised and caught."""
        error_message = 'Session timeout'
        with pytest.raises(LibsshSessionException, match=error_message):
            raise LibsshSessionException(error_message)

    def test_session_exception_caught_as_base_class(self):
        """Test that LibsshSessionException can be caught as LibsshException."""
        error_message = 'Session error'
        with pytest.raises(LibsshException, match=error_message):
            raise LibsshSessionException(error_message)


class TestLibsshChannelException:
    """Tests for LibsshChannelException."""

    def test_channel_exception_inherits_from_libssh_exception(self):
        """Test LibsshChannelException inherits from LibsshException."""
        exc = LibsshChannelException('channel error')
        assert isinstance(exc, LibsshException)
        assert isinstance(exc, Exception)

    def test_channel_exception_with_message(self):
        """Test LibsshChannelException instantiation with message."""
        error_message = 'Channel open failed'
        exc = LibsshChannelException(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message

    def test_channel_exception_can_be_raised(self):
        """Test that LibsshChannelException can be raised and caught."""
        error_message = 'Channel closed'
        with pytest.raises(LibsshChannelException, match=error_message):
            raise LibsshChannelException(error_message)

    def test_channel_exception_caught_as_base_class(self):
        """Test that LibsshChannelException can be caught as LibsshException."""
        error_message = 'Channel error'
        with pytest.raises(LibsshException, match=error_message):
            raise LibsshChannelException(error_message)


class TestLibsshChannelReadFailure:
    """Tests for LibsshChannelReadFailure."""

    def test_channel_read_failure_multiple_inheritance(self):
        """Test LibsshChannelReadFailure inherits from both parent classes."""
        exc = LibsshChannelReadFailure('read failed')
        assert isinstance(exc, LibsshChannelException)
        assert isinstance(exc, ConnectionError)
        assert isinstance(exc, LibsshException)
        assert isinstance(exc, Exception)

    def test_channel_read_failure_with_message(self):
        """Test LibsshChannelReadFailure instantiation with message."""
        error_message = 'Failed to read from channel'
        exc = LibsshChannelReadFailure(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message

    def test_channel_read_failure_has_docstring(self):
        """Test that LibsshChannelReadFailure has a docstring."""
        assert LibsshChannelReadFailure.__doc__ is not None
        assert 'failure to read from a libssh channel' in LibsshChannelReadFailure.__doc__

    def test_channel_read_failure_can_be_raised(self):
        """Test that LibsshChannelReadFailure can be raised and caught."""
        error_message = 'Connection lost during read'
        with pytest.raises(LibsshChannelReadFailure, match=error_message):
            raise LibsshChannelReadFailure(error_message)

    def test_channel_read_failure_caught_as_connection_error(self):
        """Test LibsshChannelReadFailure can be caught as ConnectionError."""
        error_message = 'Read timeout'
        with pytest.raises(ConnectionError, match=error_message):
            raise LibsshChannelReadFailure(error_message)

    def test_channel_read_failure_caught_as_channel_exception(self):
        """Test LibsshChannelReadFailure can be caught as LibsshChannelException."""
        error_message = 'Read error'
        with pytest.raises(LibsshChannelException, match=error_message):
            raise LibsshChannelReadFailure(error_message)


class TestLibsshSCPException:
    """Tests for LibsshSCPException."""

    def test_scp_exception_inherits_from_libssh_exception(self):
        """Test LibsshSCPException inherits from LibsshException."""
        exc = LibsshSCPException('scp error')
        assert isinstance(exc, LibsshException)
        assert isinstance(exc, Exception)

    def test_scp_exception_with_message(self):
        """Test LibsshSCPException instantiation with message."""
        error_message = 'SCP transfer failed'
        exc = LibsshSCPException(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message

    def test_scp_exception_can_be_raised(self):
        """Test that LibsshSCPException can be raised and caught."""
        error_message = 'Permission denied'
        with pytest.raises(LibsshSCPException, match=error_message):
            raise LibsshSCPException(error_message)

    def test_scp_exception_caught_as_base_class(self):
        """Test that LibsshSCPException can be caught as LibsshException."""
        error_message = 'SCP error'
        with pytest.raises(LibsshException, match=error_message):
            raise LibsshSCPException(error_message)


class TestLibsshSFTPException:
    """Tests for LibsshSFTPException."""

    def test_sftp_exception_inherits_from_libssh_exception(self):
        """Test LibsshSFTPException inherits from LibsshException."""
        exc = LibsshSFTPException('sftp error')
        assert isinstance(exc, LibsshException)
        assert isinstance(exc, Exception)

    def test_sftp_exception_with_message(self):
        """Test LibsshSFTPException instantiation with message."""
        error_message = 'SFTP operation failed'
        exc = LibsshSFTPException(error_message)
        assert exc.message == error_message
        assert str(exc) == error_message

    def test_sftp_exception_can_be_raised(self):
        """Test that LibsshSFTPException can be raised and caught."""
        error_message = 'File not found'
        with pytest.raises(LibsshSFTPException, match=error_message):
            raise LibsshSFTPException(error_message)

    def test_sftp_exception_caught_as_base_class(self):
        """Test that LibsshSFTPException can be caught as LibsshException."""
        error_message = 'SFTP error'
        with pytest.raises(LibsshException, match=error_message):
            raise LibsshSFTPException(error_message)


class TestExceptionHierarchy:
    """Tests for the exception hierarchy relationships."""

    def test_all_specific_exceptions_inherit_from_base(self):
        """Test that all specific exceptions inherit from LibsshException."""
        exceptions = [
            LibsshSessionException('test'),
            LibsshChannelException('test'),
            LibsshChannelReadFailure('test'),
            LibsshSCPException('test'),
            LibsshSFTPException('test'),
        ]
        for exc in exceptions:
            assert isinstance(exc, LibsshException)

    def test_exception_type_differentiation(self):
        """Test that different exception types can be distinguished."""
        session_exc = LibsshSessionException('session')
        channel_exc = LibsshChannelException('channel')
        scp_exc = LibsshSCPException('scp')
        sftp_exc = LibsshSFTPException('sftp')

        assert type(session_exc) != type(channel_exc)
        assert type(channel_exc) != type(scp_exc)
        assert type(scp_exc) != type(sftp_exc)

    def test_catching_specific_exception_type(self):
        """Test that specific exception types can be caught precisely."""
        with pytest.raises(LibsshSessionException):
            raise LibsshSessionException('test')

        with pytest.raises(LibsshChannelException):
            raise LibsshChannelException('test')

        with pytest.raises(LibsshSCPException):
            raise LibsshSCPException('test')

        with pytest.raises(LibsshSFTPException):
            raise LibsshSFTPException('test')
